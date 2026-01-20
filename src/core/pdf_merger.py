from pypdf import PdfWriter, PdfReader
import os

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

        for i, item in enumerate(pdf_items):
            if isinstance(item, tuple):
                path, title = item
            else:
                path = item
                title = None

            if not os.path.exists(path):
                continue
            
            try:
                reader = PdfReader(path)
                num_pages = len(reader.pages)
                merger.append(reader)
                
                if title:
                    # Add bookmark pointing to the first page of this appended file
                    # The page number in the new document is current_page
                    merger.add_outline_item(title, current_page)
                
                current_page += num_pages
                
                # Update progress after each PDF processed
                if progress_callback and total_items > 0:
                    progress = int(((i + 1) / total_items) * 90)  # 90% for processing PDFs
                    progress_callback(progress)
                
            except Exception as e:
                print(f"Error appending {path}: {e}")
                continue

        with open(output_path, "wb") as f:
            merger.write(f)
        
        # Final progress update
        if progress_callback:
            progress_callback(100)  # 100% when done
        
        merger.close()
        return True
