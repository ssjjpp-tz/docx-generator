# Docx Generator - Word文档生成器

一个简单的Python工具，用于生成格式化的Word文档(.docx)。

## 功能

- 根据文本内容生成Word文档
- 支持标题、段落、列表等格式
- 支持中英文论文翻译输出
- REST API接口
- 命令行工具

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行

```bash
python generate_docx.py --input content.txt --output output.docx
```

### Python API

```python
from docx_generator import DocxGenerator

generator = DocxGenerator()
generator.add_title("论文标题")
generator.add_paragraph("这是正文内容...")
generator.save("output.docx")
```

### REST API

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "论文标题",
    "content": "正文内容",
    "output": "output.docx"
  }'
```

## 作者

- GitHub: @ssjjpp-tz
