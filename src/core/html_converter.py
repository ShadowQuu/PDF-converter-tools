import os
import logging
import tempfile
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HtmlConverter:
    @staticmethod
    def _convert_with_weasyprint(input_path, output_path, font_size):
        """
        使用WeasyPrint将HTML转换为PDF的内部方法
        """
        from weasyprint import HTML, CSS
        
        logger.info("Using WeasyPrint for PDF generation...")
        
        css = CSS(string=f"""
            body {{
                font-family: 'SimSun', 'Microsoft YaHei', Arial, sans-serif;
                font-size: {font_size};
                line-height: 1.8;
                color: #333;
                margin: 0.5cm;
            }}
            h1 {{
                font-size: 24px;
                margin: 1em 0;
            }}
            h2 {{
                font-size: 20px;
                margin: 0.8em 0;
            }}
            p, li {{
                font-size: {font_size};
                margin: 0.5em 0;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
        """)
        
        HTML(input_path).write_pdf(output_path, stylesheets=[css])
        logger.info("PDF created successfully using WeasyPrint")
        return True

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
            from playwright.sync_api import sync_playwright
            
            logger.info("Using Playwright with Chromium for browser-like PDF generation...")
            
            # Read HTML content with explicit utf-8 encoding
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except UnicodeDecodeError:
                with open(input_path, 'r', encoding='gbk') as f:
                    html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            if not soup.html:
                logger.warning("No <html> tag found, adding basic structure...")
                new_soup = BeautifulSoup('<html><head></head><body></body></html>', 'html.parser')
                for element in soup.contents:
                    new_soup.body.append(element)
                soup = new_soup
            
            if not soup.head:
                logger.warning("No <head> tag found, adding it...")
                head = soup.new_tag('head')
                soup.html.insert(0, head)
            
            if not soup.body:
                logger.warning("No <body> tag found, adding it...")
                body = soup.new_tag('body')
                soup.html.append(body)
            
            if not soup.head.find('meta', charset=True):
                logger.info("Adding meta charset tag...")
                meta_charset = soup.new_tag('meta', charset='utf-8')
                soup.head.insert(0, meta_charset)
            
            font_css = f'''<style>
                body {{
                    font-family: 'SimSun', 'Microsoft YaHei', Arial, sans-serif !important;
                    font-size: {font_size} !important;
                    line-height: 1.8 !important;
                    color: #333 !important;
                    margin: 0.5cm !important;
                }}
                
                h1 {{
                    font-size: 24px !important;
                    margin: 1em 0 !important;
                }}
                
                h2 {{
                    font-size: 20px !important;
                    margin: 0.8em 0 !important;
                }}
                
                p, li {{
                    font-size: {font_size} !important;
                    margin: 0.5em 0 !important;
                }}
                
                img {{
                    max-width: 100% !important;
                    height: auto !important;
                }}
            </style>'''
            
            soup.head.append(BeautifulSoup(font_css, 'html.parser'))
            fixed_html = str(soup)
            logger.info("HTML structure fixed successfully")
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as temp_html:
                temp_html.write(fixed_html)
                temp_html_path = temp_html.name
            
            try:
                browser = None
                try:
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=True)
                        page = browser.new_page()
                        page.set_content(fixed_html)
                        page.pdf(
                            path=output_path,
                            format="A4",
                            margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
                            print_background=True,
                            prefer_css_page_size=False,
                        )
                    logger.info("PDF created successfully using Playwright")
                    return True
                finally:
                    if browser:
                        browser.close()
            finally:
                if os.path.exists(temp_html_path):
                    os.unlink(temp_html_path)
                
        except ImportError as e:
            logger.error(f"Playwright not available: {e}")
            logger.info("Falling back to WeasyPrint...")
            try:
                return HtmlConverter._convert_with_weasyprint(input_path, output_path, font_size)
            except Exception as fallback_error:
                logger.error(f"WeasyPrint conversion failed: {fallback_error}")
                raise Exception(f"转换失败: {str(fallback_error)}")
                
        except Exception as e:
            logger.error(f"Playwright method failed: {e}")
            logger.info("Falling back to WeasyPrint...")
            try:
                return HtmlConverter._convert_with_weasyprint(input_path, output_path, font_size)
            except Exception as fallback_error:
                logger.error(f"WeasyPrint conversion failed: {fallback_error}")
                raise Exception(f"转换失败: {str(fallback_error)}")
