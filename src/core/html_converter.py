import os
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HtmlConverter:
    @staticmethod
    def convert(input_path, output_path, font_size="18px", progress_callback=None):
        """
        Convert HTML file to PDF using Playwright with Chromium browser.
        This provides browser-like rendering with proper support for images, CSS, and layout.
        
        Args:
            input_path: Path to input HTML file
            output_path: Path to save PDF
            font_size: Default font size to use (default: 16px)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        try:
            # Use Playwright for browser-like rendering
            from playwright.sync_api import sync_playwright
            
            logger.info("Using Playwright with Chromium for browser-like PDF generation...")
            
            # Read HTML content with explicit utf-8 encoding
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except UnicodeDecodeError:
                # Try other encodings if utf-8 fails
                with open(input_path, 'r', encoding='gbk') as f:
                    html_content = f.read()
            
            # Validate and fix HTML structure using BeautifulSoup if needed
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ensure basic HTML structure
            if not soup.html:
                logger.warning("No <html> tag found, adding basic structure...")
                # Create a proper HTML structure
                new_soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
                # Move all content to body
                for element in soup.contents:
                    new_soup.body.append(element)
                soup = new_soup
            
            # Ensure head and body tags
            if not soup.head:
                logger.warning("No <head> tag found, adding it...")
                head = soup.new_tag('head')
                soup.html.insert(0, head)
            
            if not soup.body:
                logger.warning("No <body> tag found, adding it...")
                body = soup.new_tag('body')
                soup.html.append(body)
            
            # Ensure meta charset tag
            if not soup.head.find('meta', charset=True):
                logger.info("Adding meta charset tag...")
                meta_charset = soup.new_tag('meta', charset='utf-8')
                soup.head.insert(0, meta_charset)
            
            # Add CSS to adjust font size for better readability
            # This will override default styles for better readability
            font_css = f'''<style>
                /* Set default font size for better readability */
                body {{
                    font-family: 'SimSun', 'Microsoft YaHei', Arial, sans-serif !important;
                    font-size: {font_size} !important;
                    line-height: 1.8 !important;
                    color: #333 !important;
                    margin: 0.5cm !important;
                }}
                
                /* Adjust headings for better hierarchy */
                h1 {{
                    font-size: 24px !important;
                    margin: 1em 0 !important;
                }}
                
                h2 {{
                    font-size: 20px !important;
                    margin: 0.8em 0 !important;
                }}
                
                /* Adjust paragraphs and lists */
                p, li {{
                    font-size: {font_size} !important;
                    margin: 0.5em 0 !important;
                }}
                
                /* Ensure images are properly sized */
                img {{
                    max-width: 100% !important;
                    height: auto !important;
                }}
            </style>'''
            
            # Add the font CSS to the head
            soup.head.append(BeautifulSoup(font_css, 'html.parser'))
            
            # Convert back to string
            fixed_html = str(soup)
            logger.info("HTML structure fixed successfully")
            
            # Create a temporary file to serve the HTML
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as temp_html:
                temp_html.write(fixed_html)
                temp_html_path = temp_html.name
            
            try:
                # Use Playwright to generate PDF with Chromium
                with sync_playwright() as p:
                    # Launch browser
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    
                    # Set page content
                    page.set_content(fixed_html)
                    
                    # Generate PDF with browser rendering
                    page.pdf(
                        path=output_path,
                        format="A4",
                        margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
                        print_background=True,  # Include background colors and images
                        prefer_css_page_size=False,  # Use the specified format
                    )
                    
                    browser.close()
                
                logger.info("PDF created successfully using Playwright")
                return True
                
            finally:
                # Clean up temporary file
                os.unlink(temp_html_path)
                
        except ImportError as e:
            logger.error(f"Playwright not available: {e}")
            # Fallback to simpler method if Playwright fails
            logger.info("Falling back to simplified conversion...")
            try:
                from weasyprint import HTML, CSS
                
                logger.info("Using WeasyPrint for PDF generation...")
                
                # Create CSS for better readability
                css = CSS(string=f"""
                    body {
                        font-family: 'SimSun', 'Microsoft YaHei', Arial, sans-serif;
                        font-size: {font_size};
                        line-height: 1.8;
                        color: #333;
                        margin: 0.5cm;
                    }
                    h1 {
                        font-size: 24px;
                        margin: 1em 0;
                    }
                    h2 {
                        font-size: 20px;
                        margin: 0.8em 0;
                    }
                    p, li {
                        font-size: {font_size};
                        margin: 0.5em 0;
                    }
                    img {
                        max-width: 100%;
                        height: auto;
                    }
                """)
                
                HTML(input_path).write_pdf(output_path, stylesheets=[css])
                logger.info("PDF created successfully using WeasyPrint")
                return True
                
            except Exception as fallback_error:
                logger.error(f"All methods failed: {fallback_error}")
                raise Exception(f"Conversion failed: {str(fallback_error)}")
                
        except Exception as e:
            logger.error(f"Playwright method failed: {e}")
            # Fallback to WeasyPrint if Playwright fails
            logger.info("Falling back to simplified conversion...")
            try:
                from weasyprint import HTML, CSS
                
                logger.info("Using WeasyPrint for PDF generation...")
                
                # Create CSS for better readability
                css = CSS(string=f"""
                    body {
                        font-family: 'SimSun', 'Microsoft YaHei', Arial, sans-serif;
                        font-size: {font_size};
                        line-height: 1.8;
                        color: #333;
                        margin: 0.5cm;
                    }
                    h1 {
                        font-size: 24px;
                        margin: 1em 0;
                    }
                    h2 {
                        font-size: 20px;
                        margin: 0.8em 0;
                    }
                    p, li {
                        font-size: {font_size};
                        margin: 0.5em 0;
                    }
                    img {
                        max-width: 100%;
                        height: auto;
                    }
                """)
                
                HTML(input_path).write_pdf(output_path, stylesheets=[css])
                logger.info("PDF created successfully using WeasyPrint")
                return True
                
            except Exception as fallback_error:
                logger.error(f"All methods failed: {fallback_error}")
                raise Exception(f"Conversion failed: {str(fallback_error)}")
