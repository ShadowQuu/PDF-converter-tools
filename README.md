# PDF处理器

一个功能完善的PDF处理工具，支持HTML转PDF、JPG转PDF、PDF合并和电子书制作功能。

## 功能特性

### 1. HTML转PDF
- 将HTML文件完整转换为高质量PDF
- 支持保留原HTML的排版格式、图片和样式
- 自动处理相对路径资源引用问题

### 2. JPG转PDF
- 支持单张或多张JPG图片批量转换
- 提供图片尺寸调整功能
- 支持页面方向选择（横向/纵向）
- 可设置边距

### 3. PDF合并
- 将多个单页或多页PDF文件按指定顺序合并
- 保持原文件的质量和格式不变

### 4. 电子书制作
- 将多个PDF文件制作成带目录的电子书
- 支持自定义目录结构和章节标题
- 生成符合PDF标准的书签目录
- 确保在主流PDF阅读器中可正常显示和导航

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行界面

#### HTML转PDF
```bash
python pdf_processor_cli.py html2pdf <html_files> -o <output_dir>
```

示例：
```bash
python pdf_processor_cli.py html2pdf index.html -o output
```

#### JPG转PDF
```bash
python pdf_processor_cli.py jpg2pdf <jpg_files> <output_pdf> -o <orientation> -m <left> <right> <top> <bottom>
```

参数说明：
- `-o, --orientation`: 页面方向，可选值：纵向（默认）、横向
- `-m, --margins`: 边距设置，单位：mm，格式：左 右 上 下（默认：10 10 10 10）

示例：
```bash
python pdf_processor_cli.py jpg2pdf image1.jpg image2.jpg output.pdf -o 横向 -m 5 5 5 5
```

#### PDF合并
```bash
python pdf_processor_cli.py merge <pdf_files> <output_pdf>
```

示例：
```bash
python pdf_processor_cli.py merge file1.pdf file2.pdf merged.pdf
```

#### 电子书制作
```bash
python pdf_processor_cli.py ebook <pdf_files> <output_pdf> -t <chapter_titles>
```

参数说明：
- `-t, --titles`: 章节标题列表，可选

示例：
```bash
python pdf_processor_cli.py ebook chapter1.pdf chapter2.pdf book.pdf -t "第一章" "第二章"
```

### 图形界面（可选）

由于图形界面依赖PyQt6，可能在某些环境中安装困难，因此提供了命令行版本作为主要使用方式。如果需要使用图形界面，可以尝试运行：

```bash
python main.py
```

注意：图形界面需要安装PyQt6相关依赖，可能在某些Python版本中存在兼容性问题。

## 技术要求

- Python 3.7+
- 支持Windows、macOS和Linux操作系统

## 依赖库

- pdfkit: HTML转PDF
- Pillow: 图片处理
- PyPDF2: PDF合并
- pikepdf: 电子书制作
- reportlab: PDF生成
- PyQt6（可选）: 图形界面
- PyQt6-WebEngine（可选）: 图形界面中的PDF预览

## 许可证

MIT License
