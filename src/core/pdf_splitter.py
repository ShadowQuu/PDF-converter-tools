from pypdf import PdfReader, PdfWriter
import os

class PdfSplitter:
    @staticmethod
    def split(input_path, output_dir, split_mode="single", page_ranges=None, progress_callback=None):
        """
        Split PDF file.
        split_mode: "single" (extract all pages as separate files) or "range" (extract specific ranges)
        page_ranges: string like "1-5, 8, 10-12" (1-based index)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        reader = PdfReader(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        total_pages = len(reader.pages)

        if split_mode == "single":
            for i in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                
                output_filename = f"{base_name}_page_{i+1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                # Update progress
                if progress_callback:
                    progress = int(((i + 1) / total_pages) * 100)
                    progress_callback(progress)
                    
        elif split_mode == "range" and page_ranges:
            # Parse ranges
            # "1-5, 8" -> [0, 1, 2, 3, 4, 7]
            pages_to_extract = set()
            parts = [p.strip() for p in page_ranges.split(',')]
            
            # First pass: update progress during parsing
            total_parts = len(parts)
            for part_index, part in enumerate(parts):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    # 1-based to 0-based, inclusive
                    for i in range(start-1, end):
                        if 0 <= i < total_pages:
                            pages_to_extract.add(i)
                else:
                    i = int(part) - 1
                    if 0 <= i < total_pages:
                        pages_to_extract.add(i)
                
                # Update progress during parsing
                if progress_callback:
                    progress = int(((part_index + 1) / total_parts) * 50)  # 50% for parsing
                    progress_callback(progress)
            
            sorted_pages = sorted(list(pages_to_extract))
            
            if not sorted_pages:
                raise ValueError("No valid pages selected")

            writer = PdfWriter()
            
            # Second pass: update progress during writing
            total_sorted_pages = len(sorted_pages)
            for page_index, i in enumerate(sorted_pages):
                writer.add_page(reader.pages[i])
                
                # Update progress during writing
                if progress_callback:
                    progress = 50 + int(((page_index + 1) / total_sorted_pages) * 40)  # 40% for writing pages
                    progress_callback(progress)
            
            output_filename = f"{base_name}_split.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # Final progress update
            if progress_callback:
                progress_callback(100)  # 100% when done
                
        return True
