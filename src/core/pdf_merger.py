import logging
from pypdf import PdfWriter, PdfReader
import os

logger = logging.getLogger(__name__)


class PdfMerger:
    @staticmethod
    def merge(pdf_items, output_path, progress_callback=None):
        """
        Merge multiple PDFs into one.
        pdf_items: list of tuples (path, title) or just list of paths.
                   If title is provided, a bookmark will be created at the start of that file.
        """
        merger = PdfWriter()
        
        current_page = 0
        total_items = len(pdf_items)
        failed_files = []

        for i, item in enumerate(pdf_items):
            if isinstance(item, tuple):
                path, title = item
            else:
                path = item
                title = None

            if not os.path.exists(path):
                logger.warning(f"文件不存在，已跳过: {path}")
                failed_files.append((path, "文件不存在"))
                continue
            
            try:
                reader = PdfReader(path)
                num_pages = len(reader.pages)
                merger.append(reader)
                
                if title:
                    merger.add_outline_item(title, current_page)
                
                current_page += num_pages
                
                if progress_callback and total_items > 0:
                    progress = int(((i + 1) / total_items) * 90)
                    progress_callback(progress)
                
            except Exception as e:
                logger.error(f"添加文件失败 {path}: {e}")
                failed_files.append((os.path.basename(path), str(e)))
                continue

        with open(output_path, "wb") as f:
            merger.write(f)
        
        if progress_callback:
            progress_callback(100)
        
        merger.close()
        
        # 如果有失败的文件，抛出异常告知用户
        if failed_files:
            error_msg = "以下文件处理失败:\n"
            for filename, error in failed_files:
                error_msg += f"- {filename}: {error}\n"
            raise Exception(error_msg.strip())
        
        return True
