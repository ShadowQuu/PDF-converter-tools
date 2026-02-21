"""
PDF注释模块 - 支持添加高亮、下划线、批注等注释
"""
import os
import logging
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight, Text, Line

logger = logging.getLogger(__name__)


class PdfAnnotator:
    """PDF注释器 - 添加各种注释"""
    
    @staticmethod
    def add_highlight(input_path, output_path, page_num, rect, color=None, progress_callback=None):
        """
        添加高亮注释
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            page_num: 页码（1-based）
            rect: 高亮区域坐标 (x1, y1, x2, y2)
            color: 颜色元组 (R, G, B)，默认黄色
            progress_callback: 进度回调函数
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"添加高亮注释: 第{page_num}页")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 验证页码
            total_pages = len(reader.pages)
            if page_num < 1 or page_num > total_pages:
                raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
            
            # 默认黄色
            if color is None:
                color = (1, 1, 0)
            
            # 创建高亮注释
            highlight = Highlight(
                rect=rect,
                highlight_color=color
            )
            
            # 添加到指定页面
            writer.pages[page_num - 1].annotations.append(highlight)
            
            # 保存文件
            with open(output_path, "wb") as f:
                writer.write(f)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info("高亮注释添加成功")
            return True
            
        except Exception as e:
            logger.error(f"添加高亮注释失败: {e}")
            raise Exception(f"添加注释失败: {str(e)}")
    
    @staticmethod
    def add_text_note(input_path, output_path, page_num, rect, text, title="批注", progress_callback=None):
        """
        添加文本批注
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            page_num: 页码（1-based）
            rect: 批注位置坐标 (x1, y1, x2, y2)
            text: 批注内容
            title: 批注标题
            progress_callback: 进度回调函数
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"添加文本批注: 第{page_num}页")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 验证页码
            total_pages = len(reader.pages)
            if page_num < 1 or page_num > total_pages:
                raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
            
            # 创建文本注释
            text_annotation = Text(
                rect=rect,
                text=text,
                title=title
            )
            
            # 添加到指定页面
            writer.pages[page_num - 1].annotations.append(text_annotation)
            
            # 保存文件
            with open(output_path, "wb") as f:
                writer.write(f)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info("文本批注添加成功")
            return True
            
        except Exception as e:
            logger.error(f"添加文本批注失败: {e}")
            raise Exception(f"添加批注失败: {str(e)}")
    
    @staticmethod
    def add_underline(input_path, output_path, page_num, rect, color=None, progress_callback=None):
        """
        添加下划线注释
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            page_num: 页码（1-based）
            rect: 下划线区域坐标 (x1, y1, x2, y2)
            color: 颜色元组 (R, G, B)，默认红色
            progress_callback: 进度回调函数
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"添加下划线注释: 第{page_num}页")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # 复制所有页面
            for page in reader.pages:
                writer.add_page(page)
            
            # 验证页码
            total_pages = len(reader.pages)
            if page_num < 1 or page_num > total_pages:
                raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
            
            # 默认红色
            if color is None:
                color = (1, 0, 0)
            
            # 创建下划线（使用Line注释模拟）
            underline = Line(
                rect=rect,
                vertices=[rect[0], rect[1], rect[2], rect[1]],
                interior_color=color
            )
            
            # 添加到指定页面
            writer.pages[page_num - 1].annotations.append(underline)
            
            # 保存文件
            with open(output_path, "wb") as f:
                writer.write(f)
            
            if progress_callback:
                progress_callback(100)
            
            logger.info("下划线注释添加成功")
            return True
            
        except Exception as e:
            logger.error(f"添加下划线注释失败: {e}")
            raise Exception(f"添加下划线失败: {str(e)}")
