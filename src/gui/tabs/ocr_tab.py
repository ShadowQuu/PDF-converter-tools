"""
PDF OCR标签页 - 文字识别功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, 
    QProgressBar, QGroupBox, QTextEdit, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
import os
import webbrowser
from src.core.pdf_ocr import PdfOCR
from src.gui.utils import Worker
from src.gui.styles import BUTTON_PRIMARY, GROUP_BOX


class OcrTab(QWidget):
    """PDF OCR标签页"""
    
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
        self.input_path.setPlaceholderText("选择要识别的PDF文件...")
        self.input_path.setReadOnly(True)
        btn_browse = QPushButton("浏览")
        btn_browse.setMinimumWidth(80)
        btn_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(btn_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 识别设置
        settings_group = QGroupBox("识别设置")
        settings_group.setStyleSheet(GROUP_BOX)
        settings_layout = QVBoxLayout()
        
        # 语言选择
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("识别语言:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["中文简体", "英文"])
        lang_layout.addWidget(self.combo_lang)
        lang_layout.addStretch()
        settings_layout.addLayout(lang_layout)
        
        # 页码选择
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("指定页码 (可选):"))
        self.spin_page = QSpinBox()
        self.spin_page.setRange(0, 9999)
        self.spin_page.setValue(0)
        self.spin_page.setSpecialValueText("全部页面")
        page_layout.addWidget(self.spin_page)
        page_layout.addStretch()
        settings_layout.addLayout(page_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 识别按钮
        self.btn_recognize = QPushButton("开始识别")
        self.btn_recognize.clicked.connect(self.start_recognize)
        self.btn_recognize.setMinimumHeight(40)
        self.btn_recognize.setStyleSheet(BUTTON_PRIMARY)
        layout.addWidget(self.btn_recognize)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # 结果显示
        result_group = QGroupBox("识别结果")
        result_group.setStyleSheet(GROUP_BOX)
        result_layout = QVBoxLayout()
        
        self.text_result = QTextEdit()
        self.text_result.setPlaceholderText("识别结果将显示在这里...")
        self.text_result.setMinimumHeight(200)
        result_layout.addWidget(self.text_result)
        
        # 保存按钮
        btn_save = QPushButton("保存为文本文件")
        btn_save.clicked.connect(self.save_text)
        result_layout.addWidget(btn_save)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            self.input_path.setText(file_path)
    
    def get_lang_code(self):
        """获取语言代码"""
        lang_map = {
            "中文简体": "ch_sim",
            "英文": "en"
        }
        return lang_map.get(self.combo_lang.currentText(), "ch_sim")
    
    def start_recognize(self):
        input_file = self.input_path.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        
        self.btn_recognize.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.text_result.clear()
        
        lang = self.get_lang_code()
        page_num = self.spin_page.value() if self.spin_page.value() > 0 else None
        
        self.worker = Worker(PdfOCR.extract_text, input_file, page_num, lang)
        self.worker.finished.connect(self.on_recognize_finished)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
    
    def on_recognize_finished(self, success, result):
        self.btn_recognize.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            if isinstance(result, dict):
                # 多页结果
                text = ""
                for page_name, page_text in result.items():
                    text += f"\n{'='*50}\n{page_name}\n{'='*50}\n\n"
                    text += page_text + "\n"
                self.text_result.setText(text)
            else:
                # 单页结果
                self.text_result.setText(result)
            
            QMessageBox.information(self, "成功", "文字识别完成！")
        else:
            QMessageBox.critical(self, "错误", f"识别失败: {result}")
    
    def save_text(self):
        text = self.text_result.toPlainText()
        if not text:
            QMessageBox.warning(self, "错误", "没有可保存的内容。")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文本文件", "", "文本文件 (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "成功", "文件保存成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
