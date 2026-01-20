import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.html_converter import HtmlConverter

def test_html_conversion():
    input_html = os.path.join(os.path.dirname(__file__), 'sample.html')
    output_pdf = os.path.join(os.path.dirname(__file__), 'output.pdf')
    
    print(f"Converting {input_html} to {output_pdf}...")
    
    try:
        HtmlConverter.convert(input_html, output_pdf)
        print("✅ Conversion successful!")
        if os.path.exists(output_pdf):
            print(f"File created at: {output_pdf}")
            # Clean up
            # os.remove(output_pdf)
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_conversion()
