from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFileDialog, QTabWidget, 
    QMessageBox, QProgressBar, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt
import os
from src.core.pdf_security import PdfSecurity
from src.gui.utils import Worker
from src.gui.styles import BUTTON_PRIMARY, BUTTON_SECONDARY, GROUP_BOX


class SecurityTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_encrypt_tab(), "加密PDF")
        self.tabs.addTab(self.create_decrypt_tab(), "解密PDF")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_encrypt_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Input file group
        input_group = QGroupBox("输入文件")
        input_group.setStyleSheet(GROUP_BOX)
        input_layout = QHBoxLayout()
        self.enc_input = QLineEdit()
        self.enc_input.setPlaceholderText("选择要加密的PDF...")
        btn_browse = QPushButton("浏览")
        btn_browse.setMinimumWidth(80)
        btn_browse.clicked.connect(lambda: self.browse_file(self.enc_input))
        input_layout.addWidget(self.enc_input)
        input_layout.addWidget(btn_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Password group
        password_group = QGroupBox("密码设置")
        password_group.setStyleSheet(GROUP_BOX)
        password_layout = QVBoxLayout()
        
        # Password row with show/hide button
        pwd_row1 = QHBoxLayout()
        pwd_label1 = QLabel("用户密码:")
        pwd_label1.setMinimumWidth(80)
        self.enc_password = QLineEdit()
        self.enc_password.setPlaceholderText("输入用户密码")
        self.enc_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_show_pwd1 = QPushButton("👁")
        self.btn_show_pwd1.setCheckable(True)
        self.btn_show_pwd1.setMinimumWidth(40)
        self.btn_show_pwd1.toggled.connect(lambda checked: self.toggle_password_visibility(self.enc_password, checked))
        pwd_row1.addWidget(pwd_label1)
        pwd_row1.addWidget(self.enc_password)
        pwd_row1.addWidget(self.btn_show_pwd1)
        
        # Confirm password row
        pwd_row2 = QHBoxLayout()
        pwd_label2 = QLabel("确认密码:")
        pwd_label2.setMinimumWidth(80)
        self.enc_password_confirm = QLineEdit()
        self.enc_password_confirm.setPlaceholderText("再次输入密码确认")
        self.enc_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_show_pwd2 = QPushButton("👁")
        self.btn_show_pwd2.setCheckable(True)
        self.btn_show_pwd2.setMinimumWidth(40)
        self.btn_show_pwd2.toggled.connect(lambda checked: self.toggle_password_visibility(self.enc_password_confirm, checked))
        pwd_row2.addWidget(pwd_label2)
        pwd_row2.addWidget(self.enc_password_confirm)
        pwd_row2.addWidget(self.btn_show_pwd2)
        
        password_layout.addLayout(pwd_row1)
        password_layout.addLayout(pwd_row2)
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)

        # Encrypt Button
        btn_encrypt = QPushButton("加密PDF")
        btn_encrypt.clicked.connect(self.start_encrypt)
        btn_encrypt.setMinimumHeight(40)
        btn_encrypt.setStyleSheet(BUTTON_PRIMARY)
        layout.addWidget(btn_encrypt)
        
        # Progress Bar
        self.enc_progress = QProgressBar()
        self.enc_progress.setVisible(False)
        self.enc_progress.setRange(0, 100)
        layout.addWidget(self.enc_progress)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_decrypt_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Input file group
        input_group = QGroupBox("输入文件")
        input_group.setStyleSheet(GROUP_BOX)
        input_layout = QHBoxLayout()
        self.dec_input = QLineEdit()
        self.dec_input.setPlaceholderText("选择要解密的PDF...")
        btn_browse = QPushButton("浏览")
        btn_browse.setMinimumWidth(80)
        btn_browse.clicked.connect(lambda: self.browse_file(self.dec_input))
        input_layout.addWidget(self.dec_input)
        input_layout.addWidget(btn_browse)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Password group
        password_group = QGroupBox("密码")
        password_group.setStyleSheet(GROUP_BOX)
        password_layout = QVBoxLayout()
        
        # Password row with show/hide button
        pwd_row = QHBoxLayout()
        pwd_label = QLabel("密码:")
        pwd_label.setMinimumWidth(80)
        self.dec_password = QLineEdit()
        self.dec_password.setPlaceholderText("输入密码（如果知道的话）")
        self.dec_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_show_pwd3 = QPushButton("👁")
        self.btn_show_pwd3.setCheckable(True)
        self.btn_show_pwd3.setMinimumWidth(40)
        self.btn_show_pwd3.toggled.connect(lambda checked: self.toggle_password_visibility(self.dec_password, checked))
        pwd_row.addWidget(pwd_label)
        pwd_row.addWidget(self.dec_password)
        pwd_row.addWidget(self.btn_show_pwd3)
        
        password_layout.addLayout(pwd_row)
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)

        # Decrypt Button
        btn_decrypt = QPushButton("解密PDF")
        btn_decrypt.clicked.connect(self.start_decrypt)
        btn_decrypt.setMinimumHeight(40)
        btn_decrypt.setStyleSheet(BUTTON_SECONDARY)
        layout.addWidget(btn_decrypt)
        
        # Remove Permissions Button
        btn_remove_perms = QPushButton("移除权限限制（无需密码）")
        btn_remove_perms.clicked.connect(self.start_remove_permissions)
        btn_remove_perms.setMinimumHeight(40)
        layout.addWidget(btn_remove_perms)
        
        # Progress Bar
        self.dec_progress = QProgressBar()
        self.dec_progress.setVisible(False)
        self.dec_progress.setRange(0, 100)
        layout.addWidget(self.dec_progress)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def toggle_password_visibility(self, line_edit, checked):
        """Toggle password visibility for a line edit."""
        if checked:
            line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )
        if file_path:
            line_edit.setText(file_path)

    def start_encrypt(self):
        input_file = self.enc_input.text()
        password = self.enc_password.text()
        password_confirm = self.enc_password_confirm.text()
        
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "错误", "请选择有效的PDF文件。")
            return
        if not password:
            QMessageBox.warning(self, "错误", "请输入密码。")
            return
        if password != password_confirm:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致，请重新输入。")
            self.enc_password_confirm.clear()
            return
        if len(password) < 4:
            QMessageBox.warning(self, "错误", "密码长度至少为4个字符。")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "保存加密PDF", "", "PDF文件 (*.pdf)"
        )
        
        if output_file:
            self.enc_progress.setVisible(True)
            self.enc_progress.setValue(0)
            self.worker = Worker(PdfSecurity.encrypt, input_file, output_file, password)
            self.worker.finished.connect(lambda s, m: self.on_finished(s, m, "加密"))
            self.worker.progress.connect(self.enc_progress.setValue)
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
            self.dec_progress.setVisible(True)
            self.dec_progress.setValue(0)
            self.worker = Worker(PdfSecurity.decrypt, input_file, output_file, password)
            self.worker.finished.connect(lambda s, m: self.on_finished(s, m, "解密"))
            self.worker.progress.connect(self.dec_progress.setValue)
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
            self.dec_progress.setVisible(True)
            self.dec_progress.setValue(0)
            self.worker = Worker(PdfSecurity.remove_permissions, input_file, output_file)
            self.worker.finished.connect(lambda s, m: self.on_finished(s, m, "移除权限"))
            self.worker.progress.connect(self.dec_progress.setValue)
            self.worker.start()

    def on_finished(self, success, message, action):
        self.enc_progress.setVisible(False)
        self.dec_progress.setVisible(False)
        if success:
            if action == "移除权限":
                QMessageBox.information(self, "成功", f"{action}成功！权限限制已移除。")
            else:
                QMessageBox.information(self, "成功", f"{action}成功！")
        else:
            QMessageBox.critical(self, "错误", f"{action}失败：{message}")
