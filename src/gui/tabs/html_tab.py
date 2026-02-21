from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QProgressBar, QMessageBox, QGroupBox,
    QCheckBox, QListWidget, QAbstractItemView, QListWidgetItem, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import os
import webbrowser
import re
from datetime import datetime
from pathlib import Path
from src.core.html_converter import HtmlConverter
from src.core.pdf_merger import PdfMerger
from src.gui.utils import Worker

# 跨平台桌面路径
DESKTOP_PATH = str(Path.home() / "Desktop")

class HtmlToPdfTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Add consistent spacing between widgets

        # File List Section
        file_group = QGroupBox("HTML文件")
        file_layout = QVBoxLayout()
        file_layout.setSpacing(8)  # Add spacing within the group
        
        # Toolbar for file operations
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)  # Add spacing between buttons
        
        btn_add = QPushButton("添加文件")
        btn_add.setMinimumWidth(100)
        btn_add.clicked.connect(self.add_files)
        
        btn_remove = QPushButton("移除选中")
        btn_remove.setMinimumWidth(120)
        btn_remove.clicked.connect(self.remove_files)
        
        btn_clear = QPushButton("清空所有")
        btn_clear.setMinimumWidth(100)
        btn_clear.clicked.connect(self.clear_files)
        
        toolbar_layout.addWidget(btn_add)
        toolbar_layout.addWidget(btn_remove)
        toolbar_layout.addWidget(btn_clear)
        toolbar_layout.addStretch()
        
        # File List Widget
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.file_list.setAcceptDrops(True)
        self.file_list.setMinimumHeight(200)  # Set minimum height for better usability
        self.file_list.setAlternatingRowColors(True)  # Add alternating row colors for better readability
        
        file_layout.addLayout(toolbar_layout)
        file_layout.addWidget(self.file_list)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Settings Section
        settings_group = QGroupBox("转换设置")
        settings_layout = QGridLayout()
        settings_layout.setSpacing(8)  # Add spacing within the grid
        settings_layout.setColumnStretch(1, 1)  # Make output directory field expand
        
        # Font Size Setting
        settings_layout.addWidget(QLabel("字体大小:"), 0, 0)
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["14px", "16px", "18px", "20px"])
        self.font_size_combo.setCurrentText("18px")  # Default to 18px for better readability
        self.font_size_combo.setMinimumWidth(100)
        settings_layout.addWidget(self.font_size_combo, 0, 1, 1, 2)  # Span two columns
        
        # Output Directory Setting
        settings_layout.addWidget(QLabel("输出目录:"), 1, 0)
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("选择输出目录...")
        btn_browse_dir = QPushButton("浏览")
        btn_browse_dir.setMinimumWidth(80)
        btn_browse_dir.clicked.connect(self.browse_output_dir)
        
        settings_layout.addWidget(self.output_dir, 1, 1)
        settings_layout.addWidget(btn_browse_dir, 1, 2)
        
        # Open Folder After Conversion Checkbox
        self.open_folder_check = QCheckBox("转换后打开文件夹")
        self.open_folder_check.setChecked(True)  # Default to checked
        settings_layout.addWidget(self.open_folder_check, 2, 0, 1, 3)  # Span three columns
        
        # Merge PDFs into one ebook option
        self.merge_pdfs_check = QCheckBox("合并为单一PDF电子书")
        self.merge_pdfs_check.setChecked(False)  # Default to unchecked
        settings_layout.addWidget(self.merge_pdfs_check, 3, 0, 1, 3)  # Span three columns
        
        # Ebook Name Setting
        settings_layout.addWidget(QLabel("电子书名称:"), 4, 0)
        self.ebook_name = QLineEdit()
        self.ebook_name.setPlaceholderText("输入电子书名称...")
        self.ebook_name.setText("merged_ebook")  # Default name
        settings_layout.addWidget(self.ebook_name, 4, 1, 1, 2)  # Span two columns
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Convert Button
        self.btn_convert = QPushButton("转换为PDF")
        self.btn_convert.clicked.connect(self.start_conversion)
        self.btn_convert.setMinimumHeight(40)
        layout.addWidget(self.btn_convert)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)  # Percentage progress
        layout.addWidget(self.progress_bar)

        layout.addStretch()
        self.setLayout(layout)

        # Enable Drag & Drop for the whole tab
        self.setAcceptDrops(True)
        
        # Set default output directory to desktop (cross-platform)
        self.output_dir.setText(DESKTOP_PATH)
        
        # 连接信号，实现自动生成日期范围名称
        self.merge_pdfs_check.stateChanged.connect(self.update_default_ebook_name)
        self.file_list.model().rowsInserted.connect(self.update_default_ebook_name)
        self.file_list.model().rowsRemoved.connect(self.update_default_ebook_name)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            
            files = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.html', '.htm')):
                    files.append(file_path)
            
            if files:
                self.add_files_to_list(files)
                # 如果输出目录是默认值或未设置，使用第一个HTML文件的目录作为默认输出目录
                if not self.output_dir.text() or self.output_dir.text() == DESKTOP_PATH:
                    self.output_dir.setText(os.path.dirname(files[0]))

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select HTML Files", "", "HTML Files (*.html *.htm)"
        )
        if files:
            self.add_files_to_list(files)
            # 如果输出目录是默认值或未设置，使用第一个HTML文件的目录作为默认输出目录
            if not self.output_dir.text() or self.output_dir.text() == DESKTOP_PATH:
                self.output_dir.setText(os.path.dirname(files[0]))

    def add_files_to_list(self, files):
        for file_path in files:
            # Check for duplicates
            duplicate = False
            for i in range(self.file_list.count()):
                if self.file_list.item(i).data(Qt.ItemDataRole.UserRole) == file_path:
                    duplicate = True
                    break
            
            if not duplicate:
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                item.setToolTip(file_path)
                self.file_list.addItem(item)

    def remove_files(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def clear_files(self):
        self.file_list.clear()

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir.setText(dir_path)

    def start_conversion(self):
        files = self.get_all_files()
        if not files:
            QMessageBox.warning(self, "错误", "请至少添加一个HTML文件。")
            return

        output_dir = self.output_dir.text()
        if not output_dir or not os.path.exists(output_dir):
            QMessageBox.warning(self, "错误", "请选择有效的输出目录。")
            return

        # Get conversion settings
        font_size = self.font_size_combo.currentText()
        open_folder = self.open_folder_check.isChecked()
        merge_pdfs = self.merge_pdfs_check.isChecked()
        
        # 直接获取电子书名称，不再在这里生成日期范围
        ebook_name = self.ebook_name.text() if merge_pdfs else None

        self.btn_convert.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Convert files in a thread
        self.worker = Worker(self.convert_files, files, output_dir, font_size, merge_pdfs, ebook_name)
        self.worker.finished.connect(lambda success, message: self.on_conversion_finished(success, message, output_dir, open_folder))
        self.worker.progress.connect(self.update_progress)
        self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)

    def get_all_files(self):
        files = []
        for i in range(self.file_list.count()):
            files.append(self.file_list.item(i).data(Qt.ItemDataRole.UserRole))
        return files
    
    def extract_date_from_filename(self, filename):
        """
        从文件名中提取日期，支持多种日期格式
        支持格式：[2021-11-12], [2021.11.28], [2021/11/28]等
        返回datetime对象，如果没有匹配到日期则返回None
        """
        # 定义日期正则表达式，支持多种分隔符
        date_pattern = r'\[(\d{4}[-/.]\d{2}[-/.]\d{2})\]'
        match = re.search(date_pattern, filename)
        if match:
            date_str = match.group(1)
            # 尝试解析日期，支持多种分隔符
            for sep in ['-', '.', '/']:
                try:
                    return datetime.strptime(date_str, f"%Y{sep}%m{sep}%d")
                except ValueError:
                    continue
        return None
    
    def generate_date_range(self, files):
        """
        从文件名列表中提取日期范围
        返回格式化的日期范围字符串，如"[2021.11.12-2025.08.29]"
        如果没有匹配到日期则返回None
        """
        dates = []
        
        # 从所有文件名中提取日期
        for file_path in files:
            filename = os.path.basename(file_path)
            date = self.extract_date_from_filename(filename)
            if date:
                dates.append(date)
        
        if not dates:
            return None
        
        # 计算最小和最大日期
        min_date = min(dates)
        max_date = max(dates)
        
        # 格式化日期范围，使用点分隔符
        return f"[{min_date.strftime('%Y.%m.%d')}-{max_date.strftime('%Y.%m.%d')}]"
    
    def update_default_ebook_name(self):
        """
        自动更新电子书默认名称
        当用户勾选合并选项或文件列表变化时调用
        """
        # 只有当勾选了合并选项时才更新
        if not self.merge_pdfs_check.isChecked():
            return
        
        # 获取所有文件
        files = self.get_all_files()
        if not files:
            return
        
        # 生成日期范围
        date_range = self.generate_date_range(files)
        if date_range:
            # 每次都更新电子书名称，无论用户是否修改过
            self.ebook_name.setText(date_range)

    def convert_files(self, files, output_dir, font_size, merge_pdfs=False, ebook_name="merged_ebook", progress_callback=None):
        """
        Convert multiple HTML files to PDF with progress updates.
        """
        total = len(files)
        converted_files = []  # Store paths of converted PDFs for merging
        
        for i, input_path in enumerate(files):
            try:
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.pdf")
                
                # Convert file
                HtmlConverter.convert(input_path, output_path, font_size)
                
                # Store tuple of (path, title) for bookmarks
                converted_files.append((output_path, base_name))
                
                # Update progress
                progress = int(((i + 1) / total) * 70)  # 70% for converting HTML files
                if progress_callback:
                    progress_callback(progress)
                
            except Exception as e:
                raise Exception(f"Failed to convert {os.path.basename(input_path)}: {str(e)}")
        
        # If merge option is selected, merge all converted PDFs into one
        if merge_pdfs and converted_files:
            try:
                # Generate output filename for merged PDF
                merged_output = os.path.join(output_dir, f"{ebook_name}.pdf")
                
                # Update progress to indicate merging has started
                if progress_callback:
                    progress_callback(75)  # 75% when starting merge
                
                # Merge the PDFs with bookmarks
                PdfMerger.merge(converted_files, merged_output, progress_callback)
                
            except Exception as e:
                raise Exception(f"Failed to merge PDFs: {str(e)}")
        
        return True

    def on_conversion_finished(self, success, message, output_dir, open_folder):
        self.btn_convert.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("成功")
            msg.setText("HTML文件转换为PDF成功！")
            if self.merge_pdfs_check.isChecked():
                msg.setText("HTML文件转换为PDF并合并成功！")
            msg.setDetailedText(f"输出目录: {output_dir}")
            msg.exec()
            
            # Open folder if requested
            if open_folder:
                webbrowser.open(output_dir)
        else:
            QMessageBox.critical(self, "错误", f"转换失败: {message}")
