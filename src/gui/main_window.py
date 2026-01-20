from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from src.gui.tabs.html_tab import HtmlToPdfTab
from src.gui.tabs.image_tab import ImageToPdfTab
from src.gui.tabs.merge_tab import MergePdfTab
from src.gui.tabs.split_tab import SplitPdfTab
from src.gui.tabs.security_tab import SecurityTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF转换工具")
        self.setMinimumSize(900, 700)
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Tabs for different features
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Initialize tabs
        self.init_tabs()
        
    def init_tabs(self):
        self.tabs.addTab(HtmlToPdfTab(), "HTML转PDF")
        self.tabs.addTab(ImageToPdfTab(), "图片转PDF")
        self.tabs.addTab(MergePdfTab(), "合并PDF")
        self.tabs.addTab(SplitPdfTab(), "分割PDF")
        self.tabs.addTab(SecurityTab(), "PDF安全")
