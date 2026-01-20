import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.html_converter import HtmlConverter

def test_chinese_html_conversion():
    input_html = os.path.join(os.path.dirname(__file__), 'chinese_sample.html')
    output_pdf = os.path.join(os.path.dirname(__file__), 'chinese_output.pdf')
    
    print(f"Converting Chinese HTML {input_html} to {output_pdf}...")
    
    try:
        HtmlConverter.convert(input_html, output_pdf)
        print("✅ Conversion successful!")
        if os.path.exists(output_pdf):
            print(f"File created at: {output_pdf}")
            print(f"File size: {os.path.getsize(output_pdf)} bytes")
        else:
            print("❌ PDF file was not created")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chinese_html_conversion()
