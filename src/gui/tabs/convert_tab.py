"""
PDF转换标签页 - 支持PDF转Word和图片
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QMessageBox, 
    QProgressBar, QComboBox, QGroupBox, QRadioButton, 
    QButtonGroup, QSpinBox
)
from PyQt6.QtCore import Qt
import os
import webbrowser
from src.core.pdf_converter import PdfConverter
from src.gui.utils import Worker
from src.gui.styles import BUTTON_PRIMARY, GROUP_BOX


class ConvertTab(QWidget):
    """PDF转换标签页"""
    
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
        self.input_path.setPlaceholderText("选择要转换的PDF文件...")
        self.input_path.setReadOnly(True)
        btn_browse = QPushButton("浏览")
        btn_browse.setMinimumWidth(80)
        btn_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(btn_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 转换类型选择
        type_group = QGroupBox("转换类型")
        type_group.setStyleSheet(GROUP_BOX)
        type_layout = QVBoxLayout()
        
        self.radio_word = QRadioButton("转换为Word文档 (.docx)")
        self.radio_image = QRadioButton("转换为图片")
        self.radio_word.setChecked(True)
        
        type_layout.addWidget(self.radio_word)
        type_layout.addWidget(self.radio_image)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # 图片转换选项
        self.image_options_group = QGroupBox("图片选项")
        self.image_options_group.setStyleSheet(GROUP_BOX)
        image_options_layout = QVBoxLayout()
        
        # 图片格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("图片格式:"))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["PNG", "JPG", "JPEG"])
        format_layout.addWidget(self.combo_format)
        format_layout.addStretch()
        image_options_layout.addLayout(format_layout)
        
        # DPI设置
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("分辨率 (DPI):"))
        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(100, 600)
        self.spin_dpi.setValue(200)
        self.spin_dpi.setSingleStep(50)
        dpi_layout.addWidget(self.spin_dpi)
        dpi_layout.addStretch()
        image_options_layout.addLayout(dpi_layout)
        
        self.image_options_group.setLayout(image_options_layout)
        self.image_options_group.setVisible(False)
        layout.addWidget(self.image_options_group)
        
        # 连接信号
        self.radio_word.toggled.connect(self.on_type_changed)
        self.radio_image.toggled.connect(self.on_type_changed)
        
        # 输出目录选择
        output_group = QGroupBox("输出目录")
        output_group.setStyleSheet(GROUP_BOX)
        output_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("选择输出目录...")
        self.output_dir.setReadOnly(True)
        btn_browse_output = QPushButton("浏览")
        btn_browse_output.setMinimumWidth(80)
        btn_browse_output.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_dir)
        output_layout.addWidget(btn_browse_output)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 打开文件夹选项
        self.open_folder_check = QCheckBox("完成后打开文件夹")
        self.open_folder_check.setChecked(True)
        layout.addWidget(self.open_folder_check)
        
        # 转换按钮
        self.btn_convert = QPushButton("开始转换")
        self.btn_convert.clicked.connect(self.start_convert)
        self.btn_convert.setMinimumHeight(40)
        self.btn_convert.setStyleSheet(BUTTON_PRIMARY)
        layout.addWidget(self.btn_convert)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_type_changed(self):
        """转换类型改变时更新界面"""
        self.image_options_group.setVisible(self.radio_image.isChecked())
    
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
    
    def start_convert(self):
        input_file = self.input_path.text()
        output_dir = self.output_dir.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        if not output_dir:
            QMessageBox.warning(self, "错误", "请选择输出目录。")
            return
        
        # 确定转换类型
        if self.radio_word.isChecked():
            # 转换为Word
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.docx")
            
            self.btn_convert.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            open_folder = self.open_folder_check.isChecked()
            
            self.worker = Worker(PdfConverter.to_word, input_file, output_file)
            self.worker.finished.connect(lambda s, m: self.on_convert_finished(s, m, output_file, open_folder))
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.start()
        else:
            # 转换为图片
            image_format = self.combo_format.currentText().lower()
            dpi = self.spin_dpi.value()
            
            self.btn_convert.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            open_folder = self.open_folder_check.isChecked()
            
            self.worker = Worker(
                PdfConverter.to_images, 
                input_file, 
                output_dir, 
                image_format, 
                dpi
            )
            self.worker.finished.connect(lambda s, m: self.on_convert_finished(s, m, output_dir, open_folder))
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.start()
    
    def on_convert_finished(self, success, message, output_path, open_folder):
        self.btn_convert.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("成功")
            msg.setText("转换成功！")
            msg.setDetailedText(f"输出路径: {output_path}")
            msg.exec()
            
            if open_folder:
                webbrowser.open(output_path)
        else:
            QMessageBox.critical(self, "错误", f"转换失败: {message}")
