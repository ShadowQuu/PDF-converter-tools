"""
PDF编辑模块 - 支持基本文本编辑
"""
import os
import logging
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PdfEditor:
    """PDF编辑器 - 基本文本编辑功能"""
    
    @staticmethod
    def extract_text(input_path, page_num=None, progress_callback=None):
        """
        提取PDF中的文字
        
        Args:
            input_path: PDF文件路径
            page_num: 指定页码（1-based），None表示所有页面
            progress_callback: 进度回调函数
            
        Returns:
            str or dict: 提取的文字内容
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始提取文字: {input_path}")
            
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            if page_num is not None:
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
                
                page = doc[page_num - 1]
                text = page.get_text()
                
                if progress_callback:
                    progress_callback(100)
                
                doc.close()
                logger.info(f"文字提取完成，第{page_num}页")
                return text
            else:
                all_text = {}
                for i in range(total_pages):
                    page = doc[i]
                    text = page.get_text()
                    all_text[f"第{i+1}页"] = text
                    
                    if progress_callback:
                        progress = int(((i + 1) / total_pages) * 100)
                        progress_callback(progress)
                
                doc.close()
                logger.info(f"文字提取完成，共{total_pages}页")
                return all_text
                
        except Exception as e:
            logger.error(f"文字提取失败: {e}")
            raise Exception(f"提取失败: {str(e)}")
    
    @staticmethod
    def replace_text(input_path, output_path, page_num, old_text, new_text, progress_callback=None):
        """
        替换PDF中的文字（简单替换，格式可能不完全保留）
        
        Args:
            input_path: PDF文件路径
            output_path: 输出PDF文件路径
            page_num: 页码（1-based）
            old_text: 要替换的文字
            new_text: 新文字
            progress_callback: 进度回调函数
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始替换文字: 第{page_num}页, '{old_text}' -> '{new_text}'")
            
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            if page_num < 1 or page_num > total_pages:
                raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
            
            page = doc[page_num - 1]
            
            # 搜索文字位置
            text_instances = page.search_for(old_text)
            
            if not text_instances:
                doc.close()
                raise ValueError(f"未找到文字: '{old_text}'")
            
            # 替换每个实例
            for inst in text_instances:
                # 添加红色矩形覆盖原文字
                highlight = page.add_redact_annot(inst, fill=(1, 1, 1))
                highlight.update()
            
            # 应用修订
            page.apply_redactions()
            
            # 在相同位置添加新文字
            for inst in text_instances:
                page.insert_text(inst.tl, new_text, fontsize=11)
            
            # 保存文件
            doc.save(output_path)
            doc.close()
            
            if progress_callback:
                progress_callback(100)
            
            logger.info("文字替换成功")
            return True
            
        except Exception as e:
            logger.error(f"文字替换失败: {e}")
            raise Exception(f"替换失败: {str(e)}")
    
    @staticmethod
    def insert_text(input_path, output_path, page_num, text, position, fontsize=12, color=(0, 0, 0), progress_callback=None):
        """
        在指定位置插入文字
        
        Args:
            input_path: PDF文件路径
            output_path: 输出PDF文件路径
            page_num: 页码（1-based）
            text: 要插入的文字
            position: 位置坐标 (x, y)
            fontsize: 字体大小
            color: 文字颜色 (R, G, B)
            progress_callback: 进度回调函数
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始插入文字: 第{page_num}页, 位置{position}")
            
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            if page_num < 1 or page_num > total_pages:
                raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
            
            page = doc[page_num - 1]
            
            # 插入文字
            page.insert_text(position, text, fontsize=fontsize, color=color)
            
            # 保存文件
            doc.save(output_path)
            doc.close()
            
            if progress_callback:
                progress_callback(100)
            
            logger.info("文字插入成功")
            return True
            
        except Exception as e:
            logger.error(f"文字插入失败: {e}")
            raise Exception(f"插入失败: {str(e)}")
