from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QRadioButton, 
    QButtonGroup, QMessageBox, QProgressBar, QCheckBox
)
from PyQt6.QtCore import Qt
import os
from src.core.pdf_splitter import PdfSplitter
from src.gui.utils import Worker
import webbrowser

class SplitPdfTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input File Selection
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("选择要分割的PDF文件...")
        self.input_path.setReadOnly(True)
        btn_browse_input = QPushButton("浏览PDF")
        btn_browse_input.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(btn_browse_input)
        layout.addLayout(input_layout)

        # Output Directory Selection
        output_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("选择输出目录...")
        self.output_dir.setReadOnly(True)
        btn_browse_output = QPushButton("浏览目录")
        btn_browse_output.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_dir)
        output_layout.addWidget(btn_browse_output)
        layout.addLayout(output_layout)

        # Split Options
        options_layout = QVBoxLayout()
        self.radio_single = QRadioButton("分割为单页")
        self.radio_range = QRadioButton("提取特定页码")
        self.radio_single.setChecked(True)
        
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("例如：1-5, 8, 10-12")
        self.range_input.setEnabled(False)
        
        self.radio_range.toggled.connect(lambda: self.range_input.setEnabled(self.radio_range.isChecked()))
        
        options_layout.addWidget(self.radio_single)
        options_layout.addWidget(self.radio_range)
        options_layout.addWidget(self.range_input)
        
        # Open Folder Option
        self.open_folder_check = QCheckBox("转换后打开文件夹")
        self.open_folder_check.setChecked(True)  # Default to checked
        options_layout.addWidget(self.open_folder_check)
        
        layout.addLayout(options_layout)

        # Split Button
        self.btn_split = QPushButton("分割PDF")
        self.btn_split.clicked.connect(self.start_split)
        self.btn_split.setMinimumHeight(40)
        layout.addWidget(self.btn_split)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
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
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.input_path.setText(file_path)
            if not self.output_dir.text():
                self.output_dir.setText(os.path.dirname(file_path))

    def browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir.setText(dir_path)

    def start_split(self):
        input_file = self.input_path.text()
        output_dir = self.output_dir.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "Error", "Please select a valid PDF file.")
            return
        if not output_dir:
            QMessageBox.warning(self, "Error", "Please select an output directory.")
            return

        split_mode = "single" if self.radio_single.isChecked() else "range"
        page_ranges = self.range_input.text() if split_mode == "range" else None

        if split_mode == "range" and not page_ranges:
            QMessageBox.warning(self, "Error", "Please enter page ranges.")
            return

        # Get open folder option
        open_folder = self.open_folder_check.isChecked()
        
        self.btn_split.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)  # Set to percentage mode
        
        self.worker = Worker(PdfSplitter.split, input_file, output_dir, split_mode, page_ranges)
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
            msg.setWindowTitle("Success")
            msg.setText("PDF split successfully!")
            msg.setDetailedText(f"Output directory: {output_dir}")
            msg.exec()
            
            # Open folder if requested
            if open_folder:
                webbrowser.open(output_dir)
        else:
            QMessageBox.critical(self, "Error", f"Split failed: {message}")
