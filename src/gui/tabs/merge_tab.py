from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QMessageBox, QLabel, QProgressBar, QCheckBox,
    QGroupBox, QWidget
)
from src.gui.widgets.file_list import FileListWidget
from src.core.pdf_merger import PdfMerger
from src.gui.utils import Worker
import os
import webbrowser


class MergePdfTab(QWidget):
    """PDF合并标签页"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 文件列表面板
        file_group = QGroupBox("PDF文件列表")
        file_layout = QVBoxLayout()
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        btn_add = QPushButton("添加")
        btn_add.clicked.connect(self.add_pdfs)
        
        btn_remove = QPushButton("移除")
        btn_remove.clicked.connect(self.remove_pdfs)
        
        btn_clear = QPushButton("清空")
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
        
        file_layout.addLayout(toolbar_layout)
        
        # 提示标签
        hint_label = QLabel("💡 提示：双击文件名可以重命名作为书签标题")
        hint_label.setStyleSheet("color: #666; font-size: 12px;")
        file_layout.addWidget(hint_label)

        # 文件列表
        self.file_list = FileListWidget(allowed_extensions=['.pdf'])
        file_layout.addWidget(self.file_list)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 选项
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout()
        
        self.open_folder_check = QCheckBox("完成后打开文件夹")
        self.open_folder_check.setChecked(True)
        options_layout.addWidget(self.open_folder_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 合并按钮
        self.btn_merge = QPushButton("合并PDF")
        self.btn_merge.clicked.connect(self.start_merge)
        self.btn_merge.setMinimumHeight(40)
        self.btn_merge.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.btn_merge)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        layout.addStretch()
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
            QMessageBox.warning(self, "错误", "请至少添加两个PDF文件进行合并。")
            return
        
        # Validate all files exist before merging
        for path, _ in files_with_titles:
            if not os.path.exists(path):
                QMessageBox.warning(self, "错误", f"文件不存在：{os.path.basename(path)}")
                return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "保存合并后的PDF", "", "PDF文件 (*.pdf)"
        )
        
        if output_file:
            self.btn_merge.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
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
            msg.setWindowTitle("成功")
            msg.setText("PDF合并成功！")
            msg.setDetailedText(f"输出文件: {output_file}")
            msg.exec()
            
            # Open folder if requested
            if open_folder:
                webbrowser.open(os.path.dirname(output_file))
        else:
            QMessageBox.critical(self, "错误", f"合并失败: {message}")
