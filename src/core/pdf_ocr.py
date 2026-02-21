"""
PDF OCR文字识别模块 - 识别扫描版PDF中的文字（使用EasyOCR，无需Tesseract）
"""
import os
import logging
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import io
import numpy as np

logger = logging.getLogger(__name__)


class PdfOCR:
    """PDF OCR识别器 - 提取扫描版PDF文字"""
    
    # 类级别的OCR读取器缓存，避免重复初始化
    _reader_cache = {}
    
    @staticmethod
    def _get_reader(lang='ch_sim'):
        """获取或创建OCR读取器（带缓存）"""
        cache_key = lang
        if cache_key not in PdfOCR._reader_cache:
            logger.info(f"初始化EasyOCR读取器，语言: {lang}")
            PdfOCR._reader_cache[cache_key] = easyocr.Reader([lang])
        return PdfOCR._reader_cache[cache_key]
    
    @staticmethod
    def extract_text(input_path, page_num=None, lang='ch_sim', progress_callback=None):
        """
        从PDF中提取文字（OCR识别，使用EasyOCR）
        
        Args:
            input_path: PDF文件路径
            page_num: 指定页码（1-based），None表示所有页面
            lang: OCR语言，'ch_sim'表示简体中文，'en'表示英文
            progress_callback: 进度回调函数
            
        Returns:
            str or dict: 提取的文字内容
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF文件不存在: {input_path}")
        
        try:
            logger.info(f"开始OCR识别: {input_path}")
            
            # 使用PyMuPDF打开PDF
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            # 获取OCR读取器
            reader = PdfOCR._get_reader(lang)
            
            # 如果只识别指定页面
            if page_num is not None:
                if page_num < 1 or page_num > total_pages:
                    raise ValueError(f"页码 {page_num} 超出范围 (1-{total_pages})")
                
                # 识别指定页面
                page = doc[page_num - 1]
                text = PdfOCR._ocr_page(page, reader)
                
                doc.close()
                
                if progress_callback:
                    progress_callback(100)
                
                logger.info(f"OCR识别完成，第{page_num}页")
                return text
            else:
                # 识别所有页面
                all_text = {}
                for i in range(total_pages):
                    page = doc[i]
                    text = PdfOCR._ocr_page(page, reader)
                    all_text[f"第{i+1}页"] = text
                    
                    if progress_callback:
                        progress = int(((i + 1) / total_pages) * 100)
                        progress_callback(progress)
                
                doc.close()
                
                logger.info(f"OCR识别完成，共{total_pages}页")
                return all_text
                
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            raise Exception(f"OCR识别失败: {str(e)}")
    
    @staticmethod
    def _ocr_page(page, reader):
        """
        对单个页面进行OCR识别
        
        Args:
            page: PyMuPDF页面对象
            reader: EasyOCR读取器
            
        Returns:
            str: 识别的文字
        """
        # 将页面渲染为图片（150 DPI足够OCR使用）
        zoom = 150 / 72  # 150 DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        # 转换为numpy数组
        img_array = np.array(img)
        
        # 使用EasyOCR识别
        results = reader.readtext(img_array)
        
        # 提取文字
        texts = [result[1] for result in results]
        
        return '\n'.join(texts)
    
    @staticmethod
    def save_text_to_file(input_path, output_path, page_num=None, lang='ch_sim', progress_callback=None):
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
