from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QTabWidget, 
    QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt
import os
from src.core.pdf_security import PdfSecurity
from src.gui.utils import Worker

class SecurityTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_encrypt_tab(), "加密PDF")
        self.tabs.addTab(self.create_decrypt_tab(), "解密PDF")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_encrypt_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Input
        input_layout = QHBoxLayout()
        self.enc_input = QLineEdit()
        self.enc_input.setPlaceholderText("选择要加密的PDF...")
        btn_browse = QPushButton("浏览")
        btn_browse.clicked.connect(lambda: self.browse_file(self.enc_input))
        input_layout.addWidget(self.enc_input)
        input_layout.addWidget(btn_browse)
        layout.addLayout(input_layout)

        # Password
        self.enc_password = QLineEdit()
        self.enc_password.setPlaceholderText("输入用户密码")
        self.enc_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.enc_password)

        # Encrypt Button
        btn_encrypt = QPushButton("加密PDF")
        btn_encrypt.clicked.connect(self.start_encrypt)
        layout.addWidget(btn_encrypt)
        
        # Progress Bar
        self.enc_progress = QProgressBar()
        self.enc_progress.setValue(0)
        self.enc_progress.setFormat("进度: %p%")
        layout.addWidget(self.enc_progress)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_decrypt_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Input
        input_layout = QHBoxLayout()
        self.dec_input = QLineEdit()
        self.dec_input.setPlaceholderText("选择要解密的PDF...")
        btn_browse = QPushButton("浏览")
        btn_browse.clicked.connect(lambda: self.browse_file(self.dec_input))
        input_layout.addWidget(self.dec_input)
        input_layout.addWidget(btn_browse)
        layout.addLayout(input_layout)

        # Password
        self.dec_password = QLineEdit()
        self.dec_password.setPlaceholderText("输入密码（如果知道的话）")
        self.dec_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.dec_password)

        # Decrypt Button
        btn_decrypt = QPushButton("解密PDF")
        btn_decrypt.clicked.connect(self.start_decrypt)
        layout.addWidget(btn_decrypt)
        
        # Remove Permissions Button
        btn_remove_perms = QPushButton("移除权限限制（无需密码）")
        btn_remove_perms.clicked.connect(self.start_remove_permissions)
        layout.addWidget(btn_remove_perms)
        
        # Progress Bar
        self.dec_progress = QProgressBar()
        self.dec_progress.setValue(0)
        self.dec_progress.setFormat("进度: %p%")
        layout.addWidget(self.dec_progress)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            line_edit.setText(file_path)

    def start_encrypt(self):
        input_file = self.enc_input.text()
        password = self.enc_password.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        if not password:
            QMessageBox.warning(self, "错误", "请输入密码。")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "保存加密PDF", "", "PDF文件 (*.pdf)"
        )
        
        if output_file:
            self.worker = Worker(PdfSecurity.encrypt, input_file, output_file, password)
            self.worker.finished.connect(lambda s, m: self.on_finished(s, m, "加密"))
            self.worker.progress.connect(self.enc_progress.setValue)
            self.enc_progress.setValue(0)  # 重置进度条
            self.worker.start()

    def start_decrypt(self):
        input_file = self.dec_input.text()
        password = self.dec_password.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "保存解密PDF", "", "PDF文件 (*.pdf)"
        )
        
        if output_file:
            self.worker = Worker(PdfSecurity.decrypt, input_file, output_file, password)
            self.worker.finished.connect(lambda s, m: self.on_finished(s, m, "解密"))
            self.worker.progress.connect(self.dec_progress.setValue)
            self.dec_progress.setValue(0)  # 重置进度条
            self.worker.start()
    
    def start_remove_permissions(self):
        input_file = self.dec_input.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "保存移除权限后的PDF", "", "PDF文件 (*.pdf)"
        )
        
        if output_file:
            self.worker = Worker(PdfSecurity.remove_permissions, input_file, output_file)
            self.worker.finished.connect(lambda s, m: self.on_finished(s, m, "移除权限"))
            self.worker.progress.connect(self.dec_progress.setValue)
            self.dec_progress.setValue(0)  # 重置进度条
            self.worker.start()

    def on_finished(self, success, message, action):
        if success:
            if action == "移除权限":
                QMessageBox.information(self, "成功", f"{action}成功！权限限制已移除。")
            else:
                QMessageBox.information(self, "成功", f"{action}成功！")
        else:
            QMessageBox.critical(self, "错误", f"{action}失败：{message}")
