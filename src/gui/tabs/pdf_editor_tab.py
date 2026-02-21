"""
交互式PDF编辑器标签页 - 类似Adobe Acrobat的PDF编辑体验
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QMessageBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit
)
from PyQt6.QtCore import Qt
import os
from src.gui.widgets.pdf_viewer import PDFViewerWidget
from src.gui.styles import BUTTON_PRIMARY, GROUP_BOX


class PdfEditorTab(QWidget):
    """交互式PDF编辑器标签页"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：PDF查看器
        self.pdf_viewer = PDFViewerWidget()
        splitter.addWidget(self.pdf_viewer)
        
        # 右侧：注释列表和属性面板
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # 注释列表
        lbl_annotations = QLabel("注释列表")
        right_layout.addWidget(lbl_annotations)
        
        self.tree_annotations = QTreeWidget()
        self.tree_annotations.setHeaderLabels(["类型", "内容", "页面"])
        self.tree_annotations.setColumnWidth(0, 80)
        self.tree_annotations.setColumnWidth(1, 150)
        self.tree_annotations.setColumnWidth(2, 60)
        right_layout.addWidget(self.tree_annotations)
        
        # 选中的文本显示
        lbl_selected = QLabel("选中的文本")
        right_layout.addWidget(lbl_selected)
        
        self.text_selected = QTextEdit()
        self.text_selected.setReadOnly(True)
        self.text_selected.setPlaceholderText("选中的文本将显示在这里...")
        self.text_selected.setMaximumHeight(100)
        right_layout.addWidget(self.text_selected)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.btn_copy = QPushButton("复制文本")
        self.btn_copy.clicked.connect(self.copy_selected_text)
        btn_layout.addWidget(self.btn_copy)
        
        self.btn_clear = QPushButton("清除选择")
        self.btn_clear.clicked.connect(self.clear_selection)
        btn_layout.addWidget(self.btn_clear)
        
        right_layout.addLayout(btn_layout)
        
        # 保存按钮
        self.btn_save = QPushButton("保存PDF")
        self.btn_save.setStyleSheet(BUTTON_PRIMARY)
        self.btn_save.clicked.connect(self.save_pdf)
        right_layout.addWidget(self.btn_save)
        
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)
        
        # 设置分割比例
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # 连接信号
        self.pdf_viewer.page_widget.annotation_added.connect(self.on_annotation_added)
        self.pdf_viewer.page_widget.text_selected.connect(self.on_text_selected)
    
    def on_annotation_added(self, annotation):
        """注释被添加时的处理"""
        item = QTreeWidgetItem()
        
        if annotation['type'] == 'highlight':
            item.setText(0, "高亮")
            item.setText(1, "高亮区域")
        elif annotation['type'] == 'underline':
            item.setText(0, "下划线")
            item.setText(1, "下划线区域")
        elif annotation['type'] == 'note':
            item.setText(0, "批注")
            item.setText(1, annotation.get('text', ''))
        
        item.setText(2, str(annotation['page'] + 1))
        self.tree_annotations.addTopLevelItem(item)
    
    def on_text_selected(self, text):
        """文本被选中时的处理"""
        self.text_selected.setText(text)
    
    def copy_selected_text(self):
        """复制选中的文本"""
        text = self.text_selected.toPlainText()
        if text:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "成功", "文本已复制到剪贴板！")
    
    def clear_selection(self):
        """清除选择"""
        self.text_selected.clear()
    
    def save_pdf(self):
        """保存PDF"""
        if not self.pdf_viewer.document:
            QMessageBox.warning(self, "错误", "请先打开PDF文件。")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存PDF文件", "", "PDF文件 (*.pdf)"
        )
        
        if file_path:
            self.pdf_viewer.save_pdf(file_path)
