"""
PDF转换模块 - 支持PDF转Word和图片
"""
import os
import logging
from pdf2docx import Converter
import fitz  # PyMuPDF
from PIL import Image
import io

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
        将PDF转换为图片（使用PyMuPDF，无需Poppler）
        
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
            
            # 使用PyMuPDF打开PDF
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            output_files = []
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            # 计算缩放比例（72 DPI是PDF默认分辨率）
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            
            for page_num in range(total_pages):
                # 获取页面
                page = doc[page_num]
                
                # 将页面渲染为图片
                pix = page.get_pixmap(matrix=mat)
                
                # 生成输出文件名
                output_filename = f"{base_name}_page_{page_num + 1}.{image_format.lower()}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片
                if image_format.lower() in ['jpg', 'jpeg']:
                    # 转换为PIL Image再保存为JPEG
                    img_data = pix.tobytes("ppm")
                    img = Image.open(io.BytesIO(img_data))
                    img = img.convert('RGB')
                    img.save(output_path, "JPEG", quality=95)
                else:
                    # 直接保存为PNG
                    pix.save(output_path)
                
                output_files.append(output_path)
                
                # 更新进度
                if progress_callback:
                    progress = int(((page_num + 1) / total_pages) * 100)
                    progress_callback(progress)
            
            doc.close()
            
            logger.info(f"PDF转图片成功，共{len(output_files)}页")
            return output_files
            
        except Exception as e:
            logger.error(f"PDF转图片失败: {e}")
            raise Exception(f"转换失败: {str(e)}")
