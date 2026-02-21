"""
PDF页面管理标签页 - 支持页面删除和提取
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, 
    QProgressBar, QGroupBox, QRadioButton, QTextEdit
)
from PyQt6.QtCore import Qt
import os
import webbrowser
from src.core.pdf_page_manager import PdfPageManager
from src.gui.utils import Worker
from src.gui.styles import BUTTON_PRIMARY, BUTTON_SECONDARY, GROUP_BOX


class PageManagerTab(QWidget):
    """PDF页面管理标签页"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 输入文件选择
        input_group = QGroupBox("输入文件")
        input_group.setStyleSheet(GROUP_BOX)
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("选择PDF文件...")
        self.input_path.setReadOnly(True)
        btn_browse = QPushButton("浏览")
        btn_browse.setMinimumWidth(80)
        btn_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(btn_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 操作类型选择
        operation_group = QGroupBox("操作类型")
        operation_group.setStyleSheet(GROUP_BOX)
        operation_layout = QVBoxLayout()
        
        self.radio_delete = QRadioButton("删除页面")
        self.radio_extract = QRadioButton("提取页面")
        self.radio_delete.setChecked(True)
        
        operation_layout.addWidget(self.radio_delete)
        operation_layout.addWidget(self.radio_extract)
        operation_group.setLayout(operation_layout)
        layout.addWidget(operation_group)
        
        # 页面范围输入
        pages_group = QGroupBox("页面设置")
        pages_group.setStyleSheet(GROUP_BOX)
        pages_layout = QVBoxLayout()
        
        pages_hint = QLabel("输入要处理的页码，格式：1,3,5-7 (表示第1、3、5、6、7页)")
        pages_hint.setStyleSheet("color: gray; font-size: 12px;")
        pages_layout.addWidget(pages_hint)
        
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("例如：1,3,5-7")
        pages_layout.addWidget(self.pages_input)
        
        pages_group.setLayout(pages_layout)
        layout.addWidget(pages_group)
        
        # 输出文件选择
        output_group = QGroupBox("输出文件")
        output_group.setStyleSheet(GROUP_BOX)
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("选择输出文件路径...")
        self.output_path.setReadOnly(True)
        btn_browse_output = QPushButton("浏览")
        btn_browse_output.setMinimumWidth(80)
        btn_browse_output.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(btn_browse_output)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 打开文件夹选项
        self.open_folder_check = QCheckBox("完成后打开文件夹")
        self.open_folder_check.setChecked(True)
        layout.addWidget(self.open_folder_check)
        
        # 操作按钮
        self.btn_execute = QPushButton("执行操作")
        self.btn_execute.clicked.connect(self.start_operation)
        self.btn_execute.setMinimumHeight(40)
        self.btn_execute.setStyleSheet(BUTTON_PRIMARY)
        layout.addWidget(self.btn_execute)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.input_path.setText(file_path)
            # 自动设置默认输出文件名
            if not self.output_path.text():
                base_name = os.path.splitext(file_path)[0]
                if self.radio_delete.isChecked():
                    self.output_path.setText(f"{base_name}_deleted.pdf")
                else:
                    self.output_path.setText(f"{base_name}_extracted.pdf")
    
    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.output_path.setText(file_path)
    
    def parse_page_ranges(self, text):
        """解析页码范围字符串"""
        pages = set()
        parts = text.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.update(range(start, end + 1))
            else:
                pages.add(int(part))
        
        return sorted(list(pages))
    
    def start_operation(self):
        input_file = self.input_path.text()
        output_file = self.output_path.text()
        pages_text = self.pages_input.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        if not output_file:
            QMessageBox.warning(self, "错误", "请选择输出文件路径。")
            return
        if not pages_text:
            QMessageBox.warning(self, "错误", "请输入要处理的页码。")
            return
        
        try:
            pages = self.parse_page_ranges(pages_text)
        except ValueError:
            QMessageBox.warning(self, "错误", "页码格式无效，请使用格式如：1,3,5-7")
            return
        
        self.btn_execute.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        open_folder = self.open_folder_check.isChecked()
        
        if self.radio_delete.isChecked():
            self.worker = Worker(PdfPageManager.delete_pages, input_file, output_file, pages)
        else:
            self.worker = Worker(PdfPageManager.extract_pages, input_file, output_file, pages)
        
        self.worker.finished.connect(lambda s, m: self.on_operation_finished(s, m, output_file, open_folder))
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
    
    def on_operation_finished(self, success, message, output_path, open_folder):
        self.btn_execute.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("成功")
            msg.setText("操作成功！")
            msg.setDetailedText(f"输出文件: {output_path}")
            msg.exec()
            
            if open_folder:
                webbrowser.open(os.path.dirname(output_path))
        else:
            QMessageBox.critical(self, "错误", f"操作失败: {message}")
