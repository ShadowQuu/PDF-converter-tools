from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QRadioButton, 
    QButtonGroup, QMessageBox, QProgressBar, QCheckBox,
    QGroupBox, QWidget
)
from PyQt6.QtCore import Qt
import os
from src.core.pdf_splitter import PdfSplitter
from src.gui.utils import Worker
import webbrowser
from typing import Optional


class SplitPdfTab(QWidget):
    """PDF分割标签页"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 输入文件选择
        input_group = QGroupBox("输入文件")
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("选择要分割的PDF文件...")
        self.input_path.setReadOnly(True)
        btn_browse_input = QPushButton("浏览")
        btn_browse_input.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(btn_browse_input)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 输出目录选择
        output_group = QGroupBox("输出目录")
        output_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("选择输出目录...")
        self.output_dir.setReadOnly(True)
        btn_browse_output = QPushButton("浏览")
        btn_browse_output.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_dir)
        output_layout.addWidget(btn_browse_output)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 分割选项
        options_group = QGroupBox("分割选项")
        options_layout = QVBoxLayout()
        
        self.radio_single = QRadioButton("分割为单页")
        self.radio_range = QRadioButton("提取特定页码")
        self.radio_average = QRadioButton("平均分割为N份")
        self.radio_outline = QRadioButton("按大纲拆分")
        self.radio_single.setChecked(True)
        
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("例如：1-5, 8, 10-12")
        self.range_input.setEnabled(False)
        
        self.average_input = QLineEdit()
        self.average_input.setPlaceholderText("例如：3")
        self.average_input.setEnabled(False)
        
        self.radio_range.toggled.connect(lambda: self.range_input.setEnabled(self.radio_range.isChecked()))
        self.radio_average.toggled.connect(lambda: self.average_input.setEnabled(self.radio_average.isChecked()))
        
        options_layout.addWidget(self.radio_single)
        options_layout.addWidget(self.radio_range)
        options_layout.addWidget(self.range_input)
        options_layout.addWidget(self.radio_average)
        options_layout.addWidget(self.average_input)
        options_layout.addWidget(self.radio_outline)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 打开文件夹选项
        self.open_folder_check = QCheckBox("转换后打开文件夹")
        self.open_folder_check.setChecked(True)
        layout.addWidget(self.open_folder_check)

        # 分割按钮
        self.btn_split = QPushButton("分割PDF")
        self.btn_split.clicked.connect(self.start_split)
        self.btn_split.setMinimumHeight(40)
        self.btn_split.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.btn_split)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        layout.addStretch()
        self.setLayout(layout)
        
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.input_path.setText(file_path)
                self.output_dir.setText(os.path.dirname(file_path))

    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.input_path.setText(file_path)
            if not self.output_dir.text():
                self.output_dir.setText(os.path.dirname(file_path))

    def browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir.setText(dir_path)

    def start_split(self):
        input_file = self.input_path.text()
        output_dir = self.output_dir.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        if not output_dir:
            QMessageBox.warning(self, "错误", "请选择输出目录。")
            return

        # 确定分割模式
        if self.radio_single.isChecked():
            split_mode = "single"
            page_ranges = None
            average_parts = None
        elif self.radio_range.isChecked():
            split_mode = "range"
            page_ranges = self.range_input.text()
            average_parts = None
            
            if not page_ranges:
                QMessageBox.warning(self, "错误", "请输入页码范围。")
                return
        elif self.radio_average.isChecked():
            split_mode = "average"
            page_ranges = None
            
            try:
                average_parts = int(self.average_input.text())
                if average_parts <= 0:
                    raise ValueError()
            except ValueError:
                QMessageBox.warning(self, "错误", "请输入有效的份数（大于0的整数）。")
                return
        elif self.radio_outline.isChecked():
            split_mode = "outline"
            page_ranges = None
            average_parts = None

        # 获取打开文件夹选项
        open_folder = self.open_folder_check.isChecked()
        
        self.btn_split.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = Worker(
            PdfSplitter.split, 
            input_file, 
            output_dir, 
            split_mode, 
            page_ranges, 
            average_parts
        )
        self.worker.finished.connect(lambda success, message: self.on_split_finished(success, message, output_dir, open_folder))
        self.worker.progress.connect(self.update_progress)
        self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)

    def on_split_finished(self, success, message, output_dir, open_folder):
        self.btn_split.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("成功")
            msg.setText("PDF分割成功！")
            msg.setDetailedText(f"输出目录: {output_dir}")
            msg.exec()
            
            # Open folder if requested
            if open_folder:
                webbrowser.open(output_dir)
        else:
            QMessageBox.critical(self, "错误", f"分割失败: {message}")
