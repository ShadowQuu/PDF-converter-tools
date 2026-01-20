from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QMessageBox, QLabel, QProgressBar, QCheckBox
)
from src.gui.widgets.file_list import FileListWidget
from src.core.pdf_merger import PdfMerger
from src.gui.utils import Worker
import os
import webbrowser

class MergePdfTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        btn_add = QPushButton("添加PDF")
        btn_add.clicked.connect(self.add_pdfs)
        
        btn_remove = QPushButton("移除选中")
        btn_remove.clicked.connect(self.remove_pdfs)
        
        btn_clear = QPushButton("清空所有")
        btn_clear.clicked.connect(self.clear_all)
        
        btn_move_up = QPushButton("上移")
        btn_move_up.clicked.connect(self.move_up)
        
        btn_move_down = QPushButton("下移")
        btn_move_down.clicked.connect(self.move_down)

        toolbar_layout.addWidget(btn_add)
        toolbar_layout.addWidget(btn_remove)
        toolbar_layout.addWidget(btn_clear)
        toolbar_layout.addWidget(btn_move_up)
        toolbar_layout.addWidget(btn_move_down)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Instruction Label
        layout.addWidget(QLabel("提示：双击文件名可以重命名作为书签标题。"))

        # File List
        self.file_list = FileListWidget(allowed_extensions=['.pdf'])
        layout.addWidget(self.file_list)

        # Open Folder Option
        self.open_folder_check = QCheckBox("转换后打开文件夹")
        self.open_folder_check.setChecked(True)  # Default to checked
        layout.addWidget(self.open_folder_check)
        
        # Merge Button
        self.btn_merge = QPushButton("合并PDF")
        self.btn_merge.clicked.connect(self.start_merge)
        self.btn_merge.setMinimumHeight(40)
        layout.addWidget(self.btn_merge)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if files:
            self.file_list.add_files(files)

    def remove_pdfs(self):
        self.file_list.remove_selected_files()

    def clear_all(self):
        self.file_list.clear()
        
    def move_up(self):
        row = self.file_list.currentRow()
        if row > 0:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row - 1, item)
            self.file_list.setCurrentRow(row - 1)

    def move_down(self):
        row = self.file_list.currentRow()
        if row < self.file_list.count() - 1 and row != -1:
            item = self.file_list.takeItem(row)
            self.file_list.insertItem(row + 1, item)
            self.file_list.setCurrentRow(row + 1)

    def start_merge(self):
        # Get files with their display text (which serves as bookmark title)
        files_with_titles = self.file_list.get_files_with_titles()
        
        if len(files_with_titles) < 2:
            QMessageBox.warning(self, "Error", "Please add at least two PDF files to merge.")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "", "PDF Files (*.pdf)"
        )
        
        if output_file:
            self.btn_merge.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 100)  # Set to percentage mode
            
            # Get open folder option
            open_folder = self.open_folder_check.isChecked()
            
            self.worker = Worker(PdfMerger.merge, files_with_titles, output_file)
            self.worker.finished.connect(lambda success, message: self.on_merge_finished(success, message, output_file, open_folder))
            self.worker.progress.connect(self.update_progress)
            self.worker.start()
    
    def update_progress(self, value):
        """Update progress bar value"""
        self.progress_bar.setValue(value)

    def on_merge_finished(self, success, message, output_file, open_folder):
        self.btn_merge.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText("PDFs merged successfully!")
            msg.setDetailedText(f"Output file: {output_file}")
            msg.exec()
            
            # Open folder if requested
            if open_folder:
                webbrowser.open(os.path.dirname(output_file))
        else:
            QMessageBox.critical(self, "Error", f"Merge failed: {message}")
