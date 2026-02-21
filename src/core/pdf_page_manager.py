"""
PDF页面管理模块 - 支持页面删除和提取
"""
import os
import logging
from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)


class PdfPageManager:
    """PDF页面管理器 - 删除和提取页面"""
    
    @staticmethod
    def delete_pages(input_path, output_path, pages_to_delete, progress_callback=None):
        """
        删除指定页面
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            pages_to_delete: 要删除的页码列表（1-based）
            progress_callback: 进度回调函数
            
        Returns:
            bool: 操作是否成功
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始删除页面: {input_path}, 页码: {pages_to_delete}")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total_pages = len(reader.pages)
            pages_to_delete_set = set(pages_to_delete)
            
            # 验证页码
            for page_num in pages_to_delete:
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
            
            # 复制不需要删除的页面
            pages_kept = 0
            for i in range(total_pages):
                if i + 1 not in pages_to_delete_set:
                    writer.add_page(reader.pages[i])
                    pages_kept += 1
                
                if progress_callback:
                    progress = int(((i + 1) / total_pages) * 100)
                    progress_callback(progress)
            
            # 保存文件
            with open(output_path, "wb") as f:
                writer.write(f)
            
            logger.info(f"页面删除成功，保留了{pages_kept}页")
            return True
            
        except Exception as e:
            logger.error(f"页面删除失败: {e}")
            raise Exception(f"删除失败: {str(e)}")
    
    @staticmethod
    def extract_pages(input_path, output_path, pages_to_extract, progress_callback=None):
        """
        提取指定页面
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出PDF文件路径
            pages_to_extract: 要提取的页码列表（1-based）
            progress_callback: 进度回调函数
            
        Returns:
            bool: 操作是否成功
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始提取页面: {input_path}, 页码: {pages_to_extract}")
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            total_pages = len(reader.pages)
            
            # 验证页码
            for page_num in pages_to_extract:
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
            
            # 提取指定页面
            for i, page_num in enumerate(pages_to_extract):
                writer.add_page(reader.pages[page_num - 1])
                
                if progress_callback:
                    progress = int(((i + 1) / len(pages_to_extract)) * 100)
                    progress_callback(progress)
            
            # 保存文件
            with open(output_path, "wb") as f:
                writer.write(f)
            
            logger.info(f"页面提取成功，共提取{len(pages_to_extract)}页")
            return True
            
        except Exception as e:
            logger.error(f"页面提取失败: {e}")
            raise Exception(f"提取失败: {str(e)}")
