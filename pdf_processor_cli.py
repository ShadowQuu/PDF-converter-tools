#!/usr/bin/env python3
"""
PDF处理器 - 命令行界面

功能：
1. HTML转PDF
2. JPG转PDF
3. PDF合并
4. 电子书制作
"""
import sys
import os
import argparse
from typing import List, Optional, Tuple
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import pikepdf
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import pdfkit
from executable_detector import detect_executable

class PDFProcessor:
    """PDF处理核心类"""
    
    def html_to_pdf(self, input_files: List[str], output_dir: str) -> None:
        """
        将HTML文件转换为PDF
        
        Args:
            input_files: HTML文件列表
            output_dir: 输出目录
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        total_files = len(input_files)
        print(f"开始处理 {total_files} 个HTML文件...")
        
        success_count = 0
        for i, html_file in enumerate(input_files, 1):
            print(f"处理中 ({i}/{total_files}): {os.path.basename(html_file)}")
            
            if not os.path.exists(html_file):
                print(f"❌ 错误: 文件不存在 - {html_file}")
                continue
            
            if not html_file.lower().endswith(('.html', '.htm')):
                print(f"❌ 错误: 不是HTML文件 - {html_file}")
                continue
            
            base_name = os.path.basename(html_file)
            output_pdf = os.path.join(output_dir, os.path.splitext(base_name)[0] + '.pdf')
            
            try:
                # 处理相对路径资源问题
                options = {
                    'enable-local-file-access': None,
                    'margin-top': '10mm',
                    'margin-right': '10mm',
                    'margin-bottom': '10mm',
                    'margin-left': '10mm',
                }
                
                # 保存当前工作目录
                original_cwd = os.getcwd()
                
                # 切换到HTML文件所在目录
                html_dir = os.path.dirname(html_file)
                if html_dir:
                    os.chdir(html_dir)
                    html_file = os.path.basename(html_file)
                
                # 转换HTML到PDF
                try:
                    # 尝试使用默认配置
                    pdfkit.from_file(html_file, output_pdf, options=options)
                except OSError:
                    # 如果默认配置失败，尝试自动查找wkhtmltopdf路径
                    wkhtmltopdf_path = detect_executable('wkhtmltopdf')
                    
                    if wkhtmltopdf_path:
                        # 使用找到的路径
                        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                        pdfkit.from_file(html_file, output_pdf, options=options, configuration=config)
                    else:
                        # 如果找不到，提示用户安装和设置路径
                        raise Exception('\n'.join([
                            'No wkhtmltopdf executable found.',
                            'Please install wkhtmltopdf:',
                            '1. Download from https://wkhtmltopdf.org/downloads.html',
                            '2. Install it to a standard location or add it to PATH'
                        ]))
                
                # 恢复原工作目录
                os.chdir(original_cwd)
                
                print(f"✅ HTML转PDF成功: {os.path.basename(output_pdf)}")
                success_count += 1
            except Exception as e:
                # 确保恢复原工作目录
                os.chdir(original_cwd)
                print(f"❌ 错误: 转换HTML到PDF失败 - {str(e)}")
        
        print(f"\n处理完成: {success_count}/{total_files} 个文件成功")
    
    def jpg_to_pdf(self, input_files: List[str], output_pdf: str, 
                  orientation: str = '纵向', margins: Tuple[float, float, float, float] = (10, 10, 10, 10)) -> None:
        """
        将JPG文件转换为PDF
        
        Args:
            input_files: JPG文件列表
            output_pdf: 输出PDF文件路径
            orientation: 页面方向，可选值：纵向、横向
            margins: 边距设置，格式：(左, 右, 上, 下)，单位：mm
        """
        print(f"开始将 {len(input_files)} 个JPG文件转换为PDF...")
        
        try:
            # 创建PDF文件
            c = canvas.Canvas(output_pdf, pagesize=A4 if orientation == '纵向' else landscape(A4))
            
            left_margin, right_margin, top_margin, bottom_margin = margins
            # 转换边距从mm到英寸
            left_margin = left_margin / 25.4
            right_margin = right_margin / 25.4
            top_margin = top_margin / 25.4
            bottom_margin = bottom_margin / 25.4
            
            total_files = len(input_files)
            for i, img_path in enumerate(input_files, 1):
                print(f"处理图片 ({i}/{total_files}): {os.path.basename(img_path)}")
                
                if not os.path.exists(img_path):
                    print(f"❌ 错误: 文件不存在 - {img_path}")
                    continue
                
                if not img_path.lower().endswith(('.jpg', '.jpeg')):
                    print(f"❌ 错误: 不是JPG文件 - {img_path}")
                    continue
                
                # 打开图片获取尺寸
                with Image.open(img_path) as img:
                    img_width, img_height = img.size
                
                # 获取页面尺寸
                page_width, page_height = A4 if orientation == '纵向' else landscape(A4)
                
                # 计算可用绘制区域
                draw_width = page_width - (left_margin + right_margin) * inch
                draw_height = page_height - (top_margin + bottom_margin) * inch
                
                # 计算图片缩放比例，保持纵横比
                scale = min(draw_width / img_width, draw_height / img_height)
                
                # 计算图片居中位置
                x = left_margin * inch + (draw_width - img_width * scale) / 2
                y = bottom_margin * inch + (draw_height - img_height * scale) / 2
                
                # 绘制图片
                c.drawImage(img_path, x, y, width=img_width*scale, height=img_height*scale)
                c.showPage()
            
            # 保存PDF文件
            c.save()
            print(f"✅ JPG转PDF成功: {os.path.basename(output_pdf)}")
        except Exception as e:
            print(f"❌ 错误: 转换JPG到PDF失败 - {str(e)}")
    
    def merge_pdfs(self, input_files: List[str], output_pdf: str) -> None:
        """
        合并多个PDF文件
        
        Args:
            input_files: PDF文件列表
            output_pdf: 输出PDF文件路径
        """
        print(f"开始合并 {len(input_files)} 个PDF文件...")
        
        try:
            pdf_writer = PdfWriter()
            
            total_files = len(input_files)
            total_pages = 0
            
            for i, pdf_file in enumerate(input_files, 1):
                print(f"处理PDF ({i}/{total_files}): {os.path.basename(pdf_file)}")
                
                if not os.path.exists(pdf_file):
                    print(f"❌ 错误: 文件不存在 - {pdf_file}")
                    continue
                
                if not pdf_file.lower().endswith('.pdf'):
                    print(f"❌ 错误: 不是PDF文件 - {pdf_file}")
                    continue
                
                # 读取PDF文件
                pdf_reader = PdfReader(pdf_file)
                file_pages = len(pdf_reader.pages)
                total_pages += file_pages
                
                print(f"  添加 {file_pages} 页")
                
                # 添加所有页面到合并结果
                for page_num in range(file_pages):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)
            
            # 保存合并后的PDF文件
            with open(output_pdf, 'wb') as out:
                pdf_writer.write(out)
            
            print(f"✅ PDF合并成功: {os.path.basename(output_pdf)} ({total_pages} 页)")
        except Exception as e:
            print(f"❌ 错误: 合并PDF失败 - {str(e)}")
    
    def create_ebook(self, input_files: List[str], output_pdf: str, 
                    chapter_titles: Optional[List[str]] = None) -> None:
        """
        创建带目录的电子书
        
        Args:
            input_files: PDF文件列表
            output_pdf: 输出PDF文件路径
            chapter_titles: 章节标题列表，可选
        """
        print(f"开始制作电子书，包含 {len(input_files)} 个章节...")
        
        try:
            # 使用pikepdf创建带书签的PDF
            result = pikepdf.Pdf.new()
            
            page_offset = 0
            bookmarks = []
            total_pages = 0
            
            # 添加文件内容和书签
            total_files = len(input_files)
            for i, pdf_file in enumerate(input_files, 1):
                print(f"处理章节 ({i}/{total_files}): {os.path.basename(pdf_file)}")
                
                if not os.path.exists(pdf_file):
                    print(f"❌ 错误: 文件不存在 - {pdf_file}")
                    continue
                
                if not pdf_file.lower().endswith('.pdf'):
                    print(f"❌ 错误: 不是PDF文件 - {pdf_file}")
                    continue
                
                with pikepdf.open(pdf_file) as src:
                    file_pages = len(src.pages)
                    total_pages += file_pages
                    
                    # 获取章节标题
                    if chapter_titles and i <= len(chapter_titles):
                        chapter_title = chapter_titles[i-1]
                    else:
                        chapter_title = os.path.splitext(os.path.basename(pdf_file))[0]
                    
                    # 添加书签信息
                    bookmarks.append((chapter_title, page_offset))
                    
                    # 合并页面
                    result.pages.extend(src.pages)
                    page_offset += file_pages
                    
                    print(f"  添加 {file_pages} 页，章节: {chapter_title}")
            
            # 添加书签
            if bookmarks:
                print(f"正在添加 {len(bookmarks)} 个书签...")
                with pikepdf.open(result, allow_overwriting_input=True) as pdf:
                    outline = pdf.outline
                    for title, page_num in bookmarks:
                        outline.add(title, page_num)
                    pdf.save(output_pdf)
            else:
                result.save(output_pdf)
            
            print(f"✅ 电子书生成成功: {os.path.basename(output_pdf)} ({total_pages} 页, {len(bookmarks)} 个书签)")
        except Exception as e:
            print(f"❌ 错误: 生成电子书失败 - {str(e)}")

def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="PDF处理器 - 命令行界面")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # HTML转PDF命令
    html_parser = subparsers.add_parser("html2pdf", help="将HTML文件转换为PDF")
    html_parser.add_argument("input_files", nargs="+", help="输入HTML文件路径")
    html_parser.add_argument("-o", "--output-dir", default=".", help="输出目录，默认为当前目录")
    
    # JPG转PDF命令
    jpg_parser = subparsers.add_parser("jpg2pdf", help="将JPG文件转换为PDF")
    jpg_parser.add_argument("input_files", nargs="+", help="输入JPG文件路径")
    jpg_parser.add_argument("output_pdf", help="输出PDF文件路径")
    jpg_parser.add_argument("-o", "--orientation", choices=["纵向", "横向"], default="纵向", help="页面方向")
    jpg_parser.add_argument("-m", "--margins", nargs=4, type=float, default=[10, 10, 10, 10], help="边距 (左 右 上 下)，单位：mm")
    
    # PDF合并命令
    merge_parser = subparsers.add_parser("merge", help="合并多个PDF文件")
    merge_parser.add_argument("input_files", nargs="+", help="输入PDF文件路径")
    merge_parser.add_argument("output_pdf", help="输出PDF文件路径")
    
    # 电子书制作命令
    ebook_parser = subparsers.add_parser("ebook", help="创建带目录的电子书")
    ebook_parser.add_argument("input_files", nargs="+", help="输入PDF文件路径")
    ebook_parser.add_argument("output_pdf", help="输出PDF文件路径")
    ebook_parser.add_argument("-t", "--titles", nargs="*", help="章节标题列表")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    processor = PDFProcessor()
    
    if args.command == "html2pdf":
        processor.html_to_pdf(args.input_files, args.output_dir)
    
    elif args.command == "jpg2pdf":
        processor.jpg_to_pdf(args.input_files, args.output_pdf, args.orientation, tuple(args.margins))
    
    elif args.command == "merge":
        processor.merge_pdfs(args.input_files, args.output_pdf)
    
    elif args.command == "ebook":
        processor.create_ebook(args.input_files, args.output_pdf, args.titles)

if __name__ == "__main__":
    main()
