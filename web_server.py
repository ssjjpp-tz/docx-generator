#!/usr/bin/env python3
"""
论文翻译生成器 - Web API服务
支持文件上传、异步处理、结果下载
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json
import time
import threading
from datetime import datetime, timedelta
from docx_generator import DocxGenerator

app = Flask(__name__)
CORS(app)  # 允许跨域

# 配置
UPLOAD_FOLDER = '/tmp/paper_uploads'
OUTPUT_FOLDER = '/tmp/paper_outputs'
TASKS_FILE = '/tmp/paper_tasks.json'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
TASK_EXPIRY_HOURS = 24

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 任务存储
tasks = {}


def load_tasks():
    """从文件加载任务"""
    global tasks
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
        except:
            tasks = {}


def save_tasks():
    """保存任务到文件"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def clean_expired_tasks():
    """清理过期任务"""
    current_time = datetime.now()
    expired_tasks = []
    
    for task_id, task in tasks.items():
        created_at = datetime.fromisoformat(task.get('created_at', '2000-01-01'))
        if current_time - created_at > timedelta(hours=TASK_EXPIRY_HOURS):
            expired_tasks.append(task_id)
    
    for task_id in expired_tasks:
        # 删除相关文件
        task = tasks.get(task_id, {})
        for key in ['input_file', 'output_file']:
            filepath = task.get(key)
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        del tasks[task_id]
    
    if expired_tasks:
        save_tasks()
        print(f"清理了 {len(expired_tasks)} 个过期任务")


def process_translation_task(task_id, content, title):
    """异步处理翻译任务"""
    try:
        tasks[task_id]['status'] = 'processing'
        tasks[task_id]['progress'] = 10
        save_tasks()
        
        # 模拟翻译处理（实际应调用翻译API或模型）
        time.sleep(2)
        tasks[task_id]['progress'] = 30
        save_tasks()
        
        # 生成Word文档
        generator = DocxGenerator()
        
        if title:
            generator.add_title(title, level=1)
        
        # 处理内容
        paragraphs = content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if para.strip():
                # 检测是否是标题
                if len(para) < 100 and not para[-1] in '。！？.!?':
                    generator.add_title(para.strip(), level=2)
                else:
                    generator.add_paragraph(para.strip())
            
            # 更新进度
            progress = 30 + int((i + 1) / len(paragraphs) * 60)
            tasks[task_id]['progress'] = min(progress, 90)
            save_tasks()
        
        # 保存文档
        output_filename = f"{task_id}.docx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        generator.save(output_path)
        
        # 更新任务状态
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['progress'] = 100
        tasks[task_id]['output_file'] = output_path
        tasks[task_id]['filename'] = f"{title or '翻译结果'}.docx"
        tasks[task_id]['completed_at'] = datetime.now().isoformat()
        save_tasks()
        
        print(f"任务 {task_id} 处理完成")
        
    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['message'] = str(e)
        save_tasks()
        print(f"任务 {task_id} 处理失败: {e}")


@app.route('/')
def index():
    """首页"""
    return jsonify({
        "service": "论文翻译生成器 API",
        "version": "1.0",
        "endpoints": {
            "/api/submit": "POST - 提交翻译任务",
            "/api/status/<task_id>": "GET - 查询任务状态",
            "/api/download/<task_id>": "GET - 下载生成的文档",
            "/api/health": "GET - 健康检查"
        }
    })


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "tasks_count": len(tasks),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/submit', methods=['POST'])
def submit_task():
    """提交翻译任务"""
    try:
        # 清理过期任务
        clean_expired_tasks()
        
        # 生成任务ID
        task_id = str(uuid.uuid4())[:8]
        
        # 获取表单数据
        title = request.form.get('title', '论文翻译')
        email = request.form.get('email', '')
        content = request.form.get('content', '')
        
        # 检查文件上传
        uploaded_file = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                # 保存上传的文件
                filename = f"{task_id}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                uploaded_file = filepath
                
                # 读取文件内容
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    # 如果不是文本文件，使用文件名作为内容标记
                    content = f"[文件: {file.filename}]\n\n{content}"
        
        # 检查内容
        if not content.strip():
            return jsonify({
                "success": False,
                "message": "请提供论文内容或上传文件"
            }), 400
        
        # 创建任务
        tasks[task_id] = {
            "task_id": task_id,
            "title": title,
            "email": email,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "input_file": uploaded_file
        }
        save_tasks()
        
        # 异步处理任务
        thread = threading.Thread(
            target=process_translation_task,
            args=(task_id, content, title)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": "任务已提交，请保存任务ID以便查询"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"提交失败: {str(e)}"
        }), 500


@app.route('/api/status/<task_id>')
def get_status(task_id):
    """获取任务状态"""
    if task_id not in tasks:
        return jsonify({
            "success": False,
            "message": "任务不存在"
        }), 404
    
    task = tasks[task_id].copy()
    # 不返回完整内容预览
    task.pop('content_preview', None)
    
    return jsonify({
        "success": True,
        "status": task.get('status'),
        "progress": task.get('progress', 0),
        "filename": task.get('filename'),
        "created_at": task.get('created_at'),
        "completed_at": task.get('completed_at')
    })


@app.route('/api/download/<task_id>')
def download_file(task_id):
    """下载生成的文档"""
    if task_id not in tasks:
        return jsonify({
            "success": False,
            "message": "任务不存在"
        }), 404
    
    task = tasks[task_id]
    
    if task.get('status') != 'completed':
        return jsonify({
            "success": False,
            "message": "任务尚未完成"
        }), 400
    
    output_file = task.get('output_file')
    if not output_file or not os.path.exists(output_file):
        return jsonify({
            "success": False,
            "message": "文件不存在"
        }), 404
    
    filename = task.get('filename', f'{task_id}.docx')
    
    return send_file(
        output_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


# 启动时加载任务
load_tasks()

if __name__ == '__main__':
    print("🚀 启动论文翻译生成器 API 服务...")
    print(f"📁 上传目录: {UPLOAD_FOLDER}")
    print(f"📁 输出目录: {OUTPUT_FOLDER}")
    app.run(host='0.0.0.0', port=8080, debug=False)
