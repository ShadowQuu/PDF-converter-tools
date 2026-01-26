import img2pdf
from PIL import Image
import os
import tempfile

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
            raise ValueError("No images provided")

        # Validate images
        valid_images = []
        temp_files = []

        total_images = len(image_paths)
        try:
            for i, path in enumerate(image_paths):
                if not os.path.exists(path):
                    continue
                
                # Check if image needs conversion (e.g. if it has alpha channel or is not compatible)
                try:
                    with Image.open(path) as img:
                        # If image has alpha, convert to RGB (white background)
                        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                            bg = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode != 'RGBA':
                                img = img.convert('RGBA')
                            bg.paste(img, mask=img.split()[3])
                            
                            # Save to temp file
                            fd, temp_path = tempfile.mkstemp(suffix=".jpg")
                            os.close(fd)
                            bg.save(temp_path, "JPEG", quality=90)
                            temp_files.append(temp_path)
                            valid_images.append(temp_path)
                        else:
                            valid_images.append(path)
                except Exception as e:
                    print(f"Error processing image {path}: {e}")
                    continue
                
                # Update progress after each image processed
                if progress_callback and total_images > 0:
                    progress = int(((i + 1) / total_images) * 90)  # 90% for image processing
                    progress_callback(progress)

            if not valid_images:
                raise ValueError("No valid images to convert")

            if convert_mode == "merge":
                # Merge all images into one PDF
                with open(output_path, "wb") as f:
                    f.write(img2pdf.convert(valid_images, rotation=img2pdf.Rotation.ifvalid))
            else:
                # Convert each image to separate PDF
                # output_path is already a directory for single mode
                base_output_dir = output_path
                for i, img_path in enumerate(valid_images):
                    # Generate output filename
                    base_name = os.path.splitext(os.path.basename(img_path))[0]
                    single_output_path = os.path.join(base_output_dir, f"{base_name}.pdf")
                    
                    # Convert single image to PDF
                    with open(single_output_path, "wb") as f:
                        f.write(img2pdf.convert([img_path], rotation=img2pdf.Rotation.ifvalid))
            
            # Final progress update
            if progress_callback:
                progress_callback(100)  # 100% when done
                
        finally:
            # Cleanup temp files
            for temp_path in temp_files:
                try:
                    os.remove(temp_path)
                except:
                    pass
        
        return True
