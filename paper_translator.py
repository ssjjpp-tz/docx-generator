#!/usr/bin/env python3
"""
论文翻译专用：生成双语对照Word文档
"""

from docx_generator import DocxGenerator
import argparse


def generate_translation_doc(sections, output_path, title="论文翻译"):
    """
    生成论文翻译文档
    
    sections: [
        {"title": "摘要", "original": "...", "translated": "..."},
        ...
    ]
    """
    gen = DocxGenerator()
    
    # 文档标题
    gen.add_title(title, level=1)
    gen.add_page_break()
    
    # 目录
    gen.add_title("目录", level=1)
    for i, section in enumerate(sections, 1):
        gen.add_paragraph(f"{i}. {section['title']}")
    gen.add_page_break()
    
    # 各章节
    for section in sections:
        gen.add_title(section['title'], level=2)
        gen.add_translation(section['original'], section['translated'])
        gen.add_page_break()
    
    return gen.save(output_path)


def generate_simple_doc(content, output_path, title=None):
    """生成简单文档"""
    gen = DocxGenerator()
    
    if title:
        gen.add_title(title, level=1)
    
    gen.add_paragraph(content)
    return gen.save(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='论文翻译文档生成器')
    parser.add_argument('--output', '-o', default='paper_translation.docx', help='输出文件')
    parser.add_argument('--title', '-t', default='论文翻译', help='文档标题')
    
    args = parser.parse_args()
    
    # 示例：生成测试文档
    sections = [
        {
            "title": "摘要",
            "original": "This is the abstract of the paper.",
            "translated": "这是论文的摘要。"
        },
        {
            "title": "引言",
            "original": "Introduction section content...",
            "translated": "引言部分内容..."
        }
    ]
    
    generate_translation_doc(sections, args.output, args.title)
    print(f"✅ 论文翻译文档已生成: {args.output}")
