"""
PDF编辑标签页 - 基本文本编辑功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, 
    QProgressBar, QGroupBox, QTextEdit, QSpinBox, QTabWidget
)
from PyQt6.QtCore import Qt
import os
import webbrowser
from src.core.pdf_editor import PdfEditor
from src.gui.utils import Worker
from src.gui.styles import BUTTON_PRIMARY, GROUP_BOX


class EditorTab(QWidget):
    """PDF编辑标签页"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_extract_tab(), "提取文字")
        self.tabs.addTab(self.create_replace_tab(), "替换文字")
        layout.addWidget(self.tabs)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_extract_tab(self):
        """创建提取文字标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 输入文件选择
        input_group = QGroupBox("输入文件")
        input_group.setStyleSheet(GROUP_BOX)
        input_layout = QHBoxLayout()
        self.extract_input = QLineEdit()
        self.extract_input.setPlaceholderText("选择PDF文件...")
        self.extract_input.setReadOnly(True)
        btn_browse = QPushButton("浏览")
        btn_browse.setMinimumWidth(80)
        btn_browse.clicked.connect(self.browse_extract_input)
        input_layout.addWidget(self.extract_input)
        input_layout.addWidget(btn_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 页码选择
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("指定页码 (可选):"))
        self.extract_page = QSpinBox()
        self.extract_page.setRange(0, 9999)
        self.extract_page.setValue(0)
        self.extract_page.setSpecialValueText("全部页面")
        page_layout.addWidget(self.extract_page)
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # 提取按钮
        self.btn_extract = QPushButton("提取文字")
        self.btn_extract.clicked.connect(self.start_extract)
        self.btn_extract.setMinimumHeight(40)
        self.btn_extract.setStyleSheet(BUTTON_PRIMARY)
        layout.addWidget(self.btn_extract)
        
        # 进度条
        self.extract_progress = QProgressBar()
        self.extract_progress.setVisible(False)
        self.extract_progress.setRange(0, 100)
        layout.addWidget(self.extract_progress)
        
        # 结果显示
        result_group = QGroupBox("提取结果")
        result_group.setStyleSheet(GROUP_BOX)
        result_layout = QVBoxLayout()
        
        self.extract_result = QTextEdit()
        self.extract_result.setPlaceholderText("提取的文字将显示在这里...")
        self.extract_result.setMinimumHeight(200)
        result_layout.addWidget(self.extract_result)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_replace_tab(self):
        """创建替换文字标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 输入文件选择
        input_group = QGroupBox("输入文件")
        input_group.setStyleSheet(GROUP_BOX)
        input_layout = QHBoxLayout()
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("选择PDF文件...")
        self.replace_input.setReadOnly(True)
        btn_browse = QPushButton("浏览")
        btn_browse.setMinimumWidth(80)
        btn_browse.clicked.connect(self.browse_replace_input)
        input_layout.addWidget(self.replace_input)
        input_layout.addWidget(btn_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 页码选择
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("页码:"))
        self.replace_page = QSpinBox()
        self.replace_page.setRange(1, 9999)
        self.replace_page.setValue(1)
        page_layout.addWidget(self.replace_page)
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # 替换内容
        replace_group = QGroupBox("替换内容")
        replace_group.setStyleSheet(GROUP_BOX)
        replace_layout = QVBoxLayout()
        
        replace_layout.addWidget(QLabel("查找文字:"))
        self.old_text = QLineEdit()
        self.old_text.setPlaceholderText("输入要替换的文字")
        replace_layout.addWidget(self.old_text)
        
        replace_layout.addWidget(QLabel("替换为:"))
        self.new_text = QLineEdit()
        self.new_text.setPlaceholderText("输入新文字")
        replace_layout.addWidget(self.new_text)
        
        replace_group.setLayout(replace_layout)
        layout.addWidget(replace_group)
        
        # 输出文件
        output_group = QGroupBox("输出文件")
        output_group.setStyleSheet(GROUP_BOX)
        output_layout = QHBoxLayout()
        self.replace_output = QLineEdit()
        self.replace_output.setPlaceholderText("选择输出文件路径...")
        self.replace_output.setReadOnly(True)
        btn_browse_output = QPushButton("浏览")
        btn_browse_output.setMinimumWidth(80)
        btn_browse_output.clicked.connect(self.browse_replace_output)
        output_layout.addWidget(self.replace_output)
        output_layout.addWidget(btn_browse_output)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 替换按钮
        self.btn_replace = QPushButton("执行替换")
        self.btn_replace.clicked.connect(self.start_replace)
        self.btn_replace.setMinimumHeight(40)
        self.btn_replace.setStyleSheet(BUTTON_PRIMARY)
        layout.addWidget(self.btn_replace)
        
        # 进度条
        self.replace_progress = QProgressBar()
        self.replace_progress.setVisible(False)
        self.replace_progress.setRange(0, 100)
        layout.addWidget(self.replace_progress)
        
        widget.setLayout(layout)
        return widget
    
    def browse_extract_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.extract_input.setText(file_path)
    
    def browse_replace_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.replace_input.setText(file_path)
            # 自动设置默认输出文件名
            if not self.replace_output.text():
                base_name = os.path.splitext(file_path)[0]
                self.replace_output.setText(f"{base_name}_edited.pdf")
    
    def browse_replace_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.replace_output.setText(file_path)
    
    def start_extract(self):
        input_file = self.extract_input.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        
        self.btn_extract.setEnabled(False)
        self.extract_progress.setVisible(True)
        self.extract_progress.setValue(0)
        self.extract_result.clear()
        
        page_num = self.extract_page.value() if self.extract_page.value() > 0 else None
        
        self.worker = Worker(PdfEditor.extract_text, input_file, page_num)
        self.worker.finished.connect(self.on_extract_finished)
        self.worker.progress.connect(self.extract_progress.setValue)
        self.worker.start()
    
    def on_extract_finished(self, success, result):
        self.btn_extract.setEnabled(True)
        self.extract_progress.setVisible(False)
        
        if success:
            if isinstance(result, dict):
                # 多页结果
                text = ""
                for page_name, page_text in result.items():
                    text += f"\n{'='*50}\n{page_name}\n{'='*50}\n\n"
                    text += page_text + "\n"
                self.extract_result.setText(text)
            else:
                # 单页结果
                self.extract_result.setText(result)
            
            QMessageBox.information(self, "成功", "文字提取完成！")
        else:
            QMessageBox.critical(self, "错误", f"提取失败: {result}")
    
    def start_replace(self):
        input_file = self.replace_input.text()
        output_file = self.replace_output.text()
        old_text = self.old_text.text()
        new_text = self.new_text.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        if not output_file:
            QMessageBox.warning(self, "错误", "请选择输出文件路径。")
            return
        if not old_text:
            QMessageBox.warning(self, "错误", "请输入要替换的文字。")
            return
        
        self.btn_replace.setEnabled(False)
        self.replace_progress.setVisible(True)
        self.replace_progress.setValue(0)
        
        page_num = self.replace_page.value()
        
        self.worker = Worker(
            PdfEditor.replace_text, 
            input_file, 
            output_file, 
            page_num, 
            old_text, 
            new_text
        )
        self.worker.finished.connect(self.on_replace_finished)
        self.worker.progress.connect(self.replace_progress.setValue)
        self.worker.start()
    
    def on_replace_finished(self, success, message):
        self.btn_replace.setEnabled(True)
        self.replace_progress.setVisible(False)
        
        if success:
            QMessageBox.information(self, "成功", "文字替换完成！")
        else:
            QMessageBox.critical(self, "错误", f"替换失败: {message}")
