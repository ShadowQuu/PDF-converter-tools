from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QMessageBox, QComboBox, QLabel, QProgressBar, QCheckBox,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from src.gui.widgets.file_list import FileListWidget
from src.core.image_converter import ImageConverter
from src.gui.utils import Worker
import os
import webbrowser

class ImageToPdfTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        btn_add = QPushButton("添加图片")
        btn_add.clicked.connect(self.add_images)
        
        btn_remove = QPushButton("移除选中")
        btn_remove.clicked.connect(self.remove_images)
        
        btn_clear = QPushButton("清空所有")
        btn_clear.clicked.connect(self.clear_all)

        toolbar_layout.addWidget(btn_add)
        toolbar_layout.addWidget(btn_remove)
        toolbar_layout.addWidget(btn_clear)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)

        # File List
        self.file_list = FileListWidget(allowed_extensions=['.jpg', '.jpeg', '.png', '.bmp'])
        layout.addWidget(self.file_list)

        # Settings
        settings_layout = QVBoxLayout()
        
        # Page Size and Orientation
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("页面大小:"))
        self.combo_size = QComboBox()
        self.combo_size.addItems(["适应图片"]) # Currently only supporting Fit to Image via img2pdf
        page_layout.addWidget(self.combo_size)
        
        page_layout.addWidget(QLabel("页面方向:"))
        self.combo_orientation = QComboBox()
        self.combo_orientation.addItems(["自动"]) # img2pdf handles this
        page_layout.addWidget(self.combo_orientation)
        page_layout.addStretch()
        
        # Conversion Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("转换模式:"))
        
        # Radio buttons for conversion mode
        self.radio_merge = QRadioButton("合并为单个PDF")
        self.radio_single = QRadioButton("每个图片生成一个PDF")
        self.radio_merge.setChecked(True)  # Default to merge mode
        
        mode_layout.addWidget(self.radio_merge)
        mode_layout.addWidget(self.radio_single)
        mode_layout.addStretch()
        
        # Open Folder Option
        self.open_folder_check = QCheckBox("转换后打开文件夹")
        self.open_folder_check.setChecked(True)  # Default to checked
        
        settings_layout.addLayout(page_layout)
        settings_layout.addLayout(mode_layout)
        settings_layout.addWidget(self.open_folder_check)
        
        layout.addLayout(settings_layout)

        # Convert Button
        self.btn_convert = QPushButton("图片转PDF")
        self.btn_convert.clicked.connect(self.start_conversion)
        self.btn_convert.setMinimumHeight(40)
        layout.addWidget(self.btn_convert)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        if files:
            self.file_list.add_files(files)

    def remove_images(self):
        self.file_list.remove_selected_files()

    def clear_all(self):
        self.file_list.clear()

    def start_conversion(self):
        files = self.file_list.get_all_files()
        if not files:
            QMessageBox.warning(self, "错误", "请至少添加一张图片。")
            return

        # Get conversion mode
        convert_mode = "merge" if self.radio_merge.isChecked() else "single"
        
        # For merge mode, ask for single output file
        # For single mode, ask for output directory
        if convert_mode == "merge":
            output_path, _ = QFileDialog.getSaveFileName(
                self, "保存PDF", "", "PDF文件 (*.pdf)"
            )
        else:
            output_path = QFileDialog.getExistingDirectory(
                self, "选择输出目录"
            )
        
        if output_path:
            self.btn_convert.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)  # Set to percentage mode
            
            # Get open folder option
            open_folder = self.open_folder_check.isChecked()
            
            self.worker = Worker(ImageConverter.convert, files, output_path, convert_mode=convert_mode)
            self.worker.finished.connect(lambda success, message: self.on_conversion_finished(success, message, output_path, open_folder))
            self.worker.progress.connect(self.update_progress)
            self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)

    def on_conversion_finished(self, success, message, output_file, open_folder):
        self.btn_convert.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            # Determine the folder to open based on whether output_file is a file or directory
            if os.path.isdir(output_file):
                open_folder_path = output_file
                msg_text = "图片已成功转换为多个PDF文件！"
                msg_detail = f"输出目录: {output_file}"
            else:
                open_folder_path = os.path.dirname(output_file)
                msg_text = "图片已成功合并为单个PDF文件！"
                msg_detail = f"输出文件: {output_file}"
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("成功")
            msg.setText(msg_text)
            msg.setDetailedText(msg_detail)
            msg.exec()
            
            # Open folder if requested
            if open_folder:
                webbrowser.open(open_folder_path)
        else:
            QMessageBox.critical(self, "错误", f"转换失败: {message}")
