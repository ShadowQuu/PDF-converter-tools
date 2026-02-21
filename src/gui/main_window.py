from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
    QStatusBar, QMenuBar, QMenu, QMessageBox, QApplication
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, QSize
from src.gui.tabs.html_tab import HtmlToPdfTab
from src.gui.tabs.image_tab import ImageToPdfTab
from src.gui.tabs.merge_tab import MergePdfTab
from src.gui.tabs.split_tab import SplitPdfTab
from src.gui.tabs.security_tab import SecurityTab
from src.gui.tabs.convert_tab import ConvertTab
from src.gui.tabs.page_manager_tab import PageManagerTab
from src.gui.tabs.pdf_editor_tab import PdfEditorTab
from src.gui.styles import TAB_WIDGET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF转换工具 v3.0")
        self.setMinimumSize(1000, 800)
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs for different features
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_WIDGET)
        layout.addWidget(self.tabs)
        
        # Initialize tabs
        self.init_tabs()
        
        # Initialize status bar
        self.init_status_bar()
        
        # Initialize menu bar
        self.init_menu_bar()
        
    def init_tabs(self):
        self.tabs.addTab(HtmlToPdfTab(), "HTML转PDF")
        self.tabs.addTab(ImageToPdfTab(), "图片转PDF")
        self.tabs.addTab(ConvertTab(), "PDF转换")
        self.tabs.addTab(MergePdfTab(), "合并PDF")
        self.tabs.addTab(SplitPdfTab(), "分割PDF")
        self.tabs.addTab(PageManagerTab(), "页面管理")
        self.tabs.addTab(PdfEditorTab(), "PDF编辑器")
        self.tabs.addTab(SecurityTab(), "PDF安全")
        
        # Connect tab change to status bar update
        self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def init_status_bar(self):
        """Initialize the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - 选择一个功能开始使用")
    
    def init_menu_bar(self):
        """Initialize the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("文件(&F)")
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("退出程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于本程序")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Add separator and version info
        help_menu.addSeparator()
        
        shortcut_action = QAction("快捷键(&S)", self)
        shortcut_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcut_action)
    
    def on_tab_changed(self, index):
        """Update status bar when tab changes."""
        tab_names = [
            "HTML转PDF - 将HTML文件转换为PDF格式",
            "图片转PDF - 将图片文件转换为PDF格式",
            "PDF转换 - PDF转Word/图片",
            "合并PDF - 将多个PDF文件合并为一个",
            "分割PDF - 将PDF文件分割为多个部分",
            "页面管理 - 删除或提取PDF页面",
            "PDF编辑器 - 交互式PDF编辑（查看、高亮、批注、复制）",
            "PDF安全 - 加密或解密PDF文件"
        ]
        if 0 <= index < len(tab_names):
            self.status_bar.showMessage(tab_names[index])
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "关于PDF转换工具",
            "<h3>PDF转换工具 v3.0</h3>"
            "<p>一个功能强大的PDF处理工具，支持：</p>"
            "<ul>"
            "<li>HTML文件转PDF</li>"
            "<li>图片转PDF</li>"
            "<li>PDF转Word/图片</li>"
            "<li>PDF合并</li>"
            "<li>PDF分割</li>"
            "<li>页面管理（删除/提取）</li>"
            "<li>PDF编辑器（交互式编辑、高亮、批注、复制）</li>"
            "<li>PDF加密/解密</li>"
            "</ul>"
            "<p>© 2024 PDF Tool Project</p>"
        )
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        QMessageBox.information(
            self,
            "快捷键",
            "<h3>键盘快捷键</h3>"
            "<table>"
            "<tr><td><b>Ctrl+Q</b></td><td>退出程序</td></tr>"
            "</table>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Can add confirmation dialog here if needed
        event.accept()
