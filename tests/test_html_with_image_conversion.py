import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.html_converter import HtmlConverter

def test_html_with_image_conversion():
    """
    Test conversion of HTML file containing images and complex styling.
    """
    input_html = os.path.join(os.path.dirname(__file__), 'html_with_image.html')
    output_pdf = os.path.join(os.path.dirname(__file__), 'html_with_image_output.pdf')
    
    print(f"Testing HTML with image conversion: {input_html} → {output_pdf}")
    
    try:
        # Convert the HTML with image
        HtmlConverter.convert(input_html, output_pdf)
        print("✅ Conversion successful!")
        
        if os.path.exists(output_pdf):
            print(f"File created at: {output_pdf}")
            print(f"File size: {os.path.getsize(output_pdf)} bytes")
            # Try to open and check if it's a valid PDF
            with open(output_pdf, 'rb') as f:
                header = f.read(4)
                if header == b'%PDF':
                    print("✅ Valid PDF file generated")
                else:
                    print("❌ Not a valid PDF file")
        else:
            print("❌ PDF file not created")
            
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_html_with_image_conversion()
