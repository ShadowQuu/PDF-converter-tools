import logging
import img2pdf
from PIL import Image
import os
import tempfile

logger = logging.getLogger(__name__)


class ImageConverter:
    @staticmethod
    def convert(image_paths, output_path, page_size=None, orientation=None, progress_callback=None, convert_mode="merge"):
        """
        Convert images to PDF.
        
        Args:
            image_paths: List of image file paths
            output_path: Output PDF file path or directory (for single mode)
            page_size: Page size (not used currently)
            orientation: Page orientation (not used currently)
            progress_callback: Progress callback function
            convert_mode: Conversion mode: "merge" (all images to one PDF) or "single" (each image to separate PDF)
        """
        if not image_paths:
            raise ValueError("没有提供图片文件")

        valid_images = []
        temp_files = []
        failed_images = []

        total_images = len(image_paths)
        try:
            for i, path in enumerate(image_paths):
                if not os.path.exists(path):
                    logger.warning(f"图片文件不存在，已跳过: {path}")
                    failed_images.append((os.path.basename(path), "文件不存在"))
                    continue
                
                try:
                    with Image.open(path) as img:
                        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                            bg = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            bg.paste(img, mask=img.split()[3])
                            
                            fd, temp_path = tempfile.mkstemp(suffix=".jpg")
                            os.close(fd)
                            bg.save(temp_path, "JPEG", quality=90)
                            temp_files.append(temp_path)
                            valid_images.append(temp_path)
                        else:
                            valid_images.append(path)
                except Exception as e:
                    logger.error(f"处理图片失败 {path}: {e}")
                    failed_images.append((os.path.basename(path), str(e)))
                    continue
                
                if progress_callback and total_images > 0:
                    progress = int(((i + 1) / total_images) * 90)
                    progress_callback(progress)

            if not valid_images:
                error_msg = "没有有效的图片可以转换"
                if failed_images:
                    error_msg += "\n失败的文件:\n"
                    for filename, error in failed_images:
                        error_msg += f"- {filename}: {error}\n"
                raise ValueError(error_msg)

            if convert_mode == "merge":
                with open(output_path, "wb") as f:
                    f.write(img2pdf.convert(valid_images, rotation=img2pdf.Rotation.ifvalid))
            else:
                base_output_dir = output_path
                for i, img_path in enumerate(valid_images):
                    base_name = os.path.splitext(os.path.basename(img_path))[0]
                    single_output_path = os.path.join(base_output_dir, f"{base_name}.pdf")
                    
                    with open(single_output_path, "wb") as f:
                        f.write(img2pdf.convert([img_path], rotation=img2pdf.Rotation.ifvalid))
            
            if progress_callback:
                progress_callback(100)
                
        finally:
            for temp_path in temp_files:
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.warning(f"清理临时文件失败 {temp_path}: {e}")
        
        # 如果有失败的文件，记录日志
        if failed_images:
            logger.warning(f"有 {len(failed_images)} 个图片处理失败")
        
        return True
