import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    print("Testing imports...")
    try:
        from src.core.html_converter import HtmlConverter
        print("✅ HtmlConverter imported")
    except ImportError as e:
        print(f"❌ HtmlConverter import failed: {e}")

    try:
        from src.core.image_converter import ImageConverter
        print("✅ ImageConverter imported")
    except ImportError as e:
        print(f"❌ ImageConverter import failed: {e}")

    try:
        from src.core.pdf_merger import PdfMerger
        print("✅ PdfMerger imported")
    except ImportError as e:
        print(f"❌ PdfMerger import failed: {e}")

    try:
        from src.core.pdf_splitter import PdfSplitter
        print("✅ PdfSplitter imported")
    except ImportError as e:
        print(f"❌ PdfSplitter import failed: {e}")

    try:
        from src.core.pdf_security import PdfSecurity
        print("✅ PdfSecurity imported")
    except ImportError as e:
        print(f"❌ PdfSecurity import failed: {e}")

    try:
        from src.gui.main_window import MainWindow
        print("✅ MainWindow imported")
    except ImportError as e:
        print(f"❌ MainWindow import failed: {e}")

if __name__ == "__main__":
    test_imports()
