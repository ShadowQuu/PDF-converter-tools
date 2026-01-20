import sys
import traceback

print("Starting application...")

try:
    from PyQt6.QtWidgets import QApplication
    print("PyQt6 imported successfully")
    from src.gui.main_window import MainWindow
    print("MainWindow imported successfully")

    def main():
        print("Initializing QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("PDF Master Tool")
        
        print("Initializing MainWindow...")
        window = MainWindow()
        window.show()
        
        print("Entering event loop...")
        exit_code = app.exec()
        print(f"Event loop exited with code {exit_code}")
        sys.exit(exit_code)

    if __name__ == "__main__":
        main()

except Exception as e:
    print("An error occurred:")
    traceback.print_exc()
    input("Press Enter to exit...")
