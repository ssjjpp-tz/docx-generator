#!/usr/bin/env python3
"""
命令行工具：生成Word文档
"""

import argparse
import sys
from docx_generator import DocxGenerator


def main():
    parser = argparse.ArgumentParser(description='生成Word文档(.docx)')
    parser.add_argument('--input', '-i', help='输入文本文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出docx文件路径')
    parser.add_argument('--title', '-t', help='文档标题')
    
    args = parser.parse_args()
    
    # 读取输入内容
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # 从stdin读取
        print("请粘贴内容（Ctrl+D结束）：")
        content = sys.stdin.read()
    
    # 生成文档
    generator = DocxGenerator()
    
    if args.title:
        generator.add_title(args.title)
    
    # 按段落处理
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            # 检测是否是标题（短行、不以标点结尾）
            if len(para) < 100 and not para[-1] in '。！？.!?':
                generator.add_title(para.strip(), level=2)
            else:
                generator.add_paragraph(para.strip())
    
    generator.save(args.output)
    print(f"✅ 文档已生成: {args.output}")


if __name__ == "__main__":
    main()
