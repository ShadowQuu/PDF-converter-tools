"""
PDF转换模块 - 支持PDF转Word和图片
"""
import os
import logging
from pdf2docx import Converter
from pdf2image import convert_from_path
from PIL import Image

logger = logging.getLogger(__name__)


class PdfConverter:
    """PDF转换器 - 支持转换为Word和图片"""
    
    @staticmethod
    def to_word(input_path, output_path, progress_callback=None):
        """
        将PDF转换为Word文档
        
        Args:
            input_path: PDF文件路径
            output_path: 输出Word文件路径
            progress_callback: 进度回调函数
            
        Returns:
            bool: 转换是否成功
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始转换PDF到Word: {input_path}")
            
            # 使用pdf2docx进行转换
            cv = Converter(input_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()
            
            if progress_callback:
                progress_callback(100)
            
            logger.info(f"PDF转Word成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF转Word失败: {e}")
            raise Exception(f"转换失败: {str(e)}")
    
    @staticmethod
    def to_images(input_path, output_dir, image_format='png', dpi=200, progress_callback=None):
        """
        将PDF转换为图片
        
        Args:
            input_path: PDF文件路径
            output_dir: 输出图片目录
            image_format: 图片格式 (png, jpg, jpeg)
            dpi: 图片分辨率
            progress_callback: 进度回调函数
            
        Returns:
            list: 生成的图片文件路径列表
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            logger.info(f"开始转换PDF到图片: {input_path}")
            
            # 转换PDF为图片
            images = convert_from_path(input_path, dpi=dpi)
            
            output_files = []
            total_pages = len(images)
            
            for i, image in enumerate(images):
                # 生成输出文件名
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_filename = f"{base_name}_page_{i+1}.{image_format.lower()}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片
                if image_format.lower() in ['jpg', 'jpeg']:
                    image = image.convert('RGB')
                image.save(output_path, image_format.upper())
                output_files.append(output_path)
                
                # 更新进度
                if progress_callback:
                    progress = int(((i + 1) / total_pages) * 100)
                    progress_callback(progress)
            
            logger.info(f"PDF转图片成功，共{len(output_files)}页")
            return output_files
            
        except Exception as e:
            logger.error(f"PDF转图片失败: {e}")
            raise Exception(f"转换失败: {str(e)}")
