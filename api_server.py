#!/usr/bin/env python3
"""
REST API服务：生成Word文档
"""

from flask import Flask, request, jsonify, send_file
from docx_generator import DocxGenerator
import os
import tempfile

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({
        "service": "Docx Generator API",
        "version": "1.0",
        "endpoints": [
            "/generate - POST生成文档",
            "/health - 健康检查"
        ]
    })


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/generate', methods=['POST'])
def generate():
    """生成Word文档"""
    data = request.json
    
    if not data:
        return jsonify({"error": "请提供JSON数据"}), 400
    
    content = data.get('content', '')
    title = data.get('title', '')
    output_name = data.get('output', 'output.docx')
    
    if not content:
        return jsonify({"error": "请提供content字段"}), 400
    
    try:
        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, output_name)
        
        # 生成文档
        generator = DocxGenerator()
        
        if title:
            generator.add_title(title)
        
        # 处理内容
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                generator.add_paragraph(para.strip())
        
        generator.save(output_path)
        
        return jsonify({
            "success": True,
            "message": "文档生成成功",
            "file_path": output_path
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    """下载生成的文档"""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "文件不存在"}), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
