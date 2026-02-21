"""
PDF OCR文字识别模块 - 识别扫描版PDF中的文字
"""
import os
import logging
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


class PdfOCR:
    """PDF OCR识别器 - 提取扫描版PDF文字"""
    
    @staticmethod
    def extract_text(input_path, page_num=None, lang='chi_sim+eng', progress_callback=None):
        """
        从PDF中提取文字（OCR识别）
        
        Args:
            input_path: PDF文件路径
            page_num: 指定页码（1-based），None表示所有页面
            lang: OCR语言，默认中文简体+英文
            progress_callback: 进度回调函数
            
        Returns:
            str or dict: 提取的文字内容
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始OCR识别: {input_path}")
            
            # 转换PDF为图片
            images = convert_from_path(input_path, dpi=300)
            total_pages = len(images)
            
            # 如果只识别指定页面
            if page_num is not None:
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
                
                # 识别指定页面
                image = images[page_num - 1]
                text = pytesseract.image_to_string(image, lang=lang)
                
                if progress_callback:
                    progress_callback(100)
                
                logger.info(f"OCR识别完成，第{page_num}页")
                return text
            else:
                # 识别所有页面
                all_text = {}
                for i, image in enumerate(images):
                    text = pytesseract.image_to_string(image, lang=lang)
                    all_text[f"第{i+1}页"] = text
                    
                    if progress_callback:
                        progress = int(((i + 1) / total_pages) * 100)
                        progress_callback(progress)
                
                logger.info(f"OCR识别完成，共{total_pages}页")
                return all_text
                
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            raise Exception(f"OCR识别失败: {str(e)}")
    
    @staticmethod
    def save_text_to_file(input_path, output_path, page_num=None, lang='chi_sim+eng', progress_callback=None):
        """
        将OCR识别的文字保存到文件
        
        Args:
            input_path: PDF文件路径
            output_path: 输出文本文件路径
            page_num: 指定页码（1-based），None表示所有页面
            lang: OCR语言
            progress_callback: 进度回调函数
        """
        try:
            # 提取文字
            result = PdfOCR.extract_text(input_path, page_num, lang, progress_callback)
            
            # 保存到文件
            with open(output_path, 'w', encoding='utf-8') as f:
                if isinstance(result, dict):
                    for page_name, text in result.items():
                        f.write(f"\n{'='*50}\n")
                        f.write(f"{page_name}\n")
                        f.write(f"{'='*50}\n\n")
                        f.write(text)
                        f.write("\n")
                else:
                    f.write(result)
            
            logger.info(f"文字已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存文字失败: {e}")
            raise Exception(f"保存失败: {str(e)}")
