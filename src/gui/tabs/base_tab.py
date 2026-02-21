"""
Base tab class for PDF tool GUI tabs.
Provides common UI components and functionality shared across all tabs.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QMessageBox, QProgressBar, 
    QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.gui.utils import Worker
import os
import webbrowser
from typing import Optional, Callable, Any


class BaseTab(QWidget):
    """
    Base class for all PDF tool tabs.
    Provides common UI components like progress bar, open folder checkbox,
    and worker thread management.
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the base tab."""
        super().__init__(parent)
        self.worker: Optional[Worker] = None
        self.init_ui()
        
    def init_ui(self) -> None:
        """Initialize the UI. Override in subclasses."""
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(10)
        self.setLayout(self.main_layout)
        
    def create_file_selection_group(
        self, 
        label_text: str, 
        button_text: str, 
        file_mode: bool = True,
        file_filter: str = "",
        callback: Optional[Callable[[str], None]] = None
    ) -> tuple[QGroupBox, QLabel, QPushButton]:
        """
        Create a file/directory selection group.
        
        Args:
            label_text: Label text for the selection
            button_text: Text for the browse button
            file_mode: True for file selection, False for directory
            file_filter: File filter for file dialog (e.g., "PDF Files (*.pdf)")
            callback: Optional callback when selection changes
            
        Returns:
            Tuple of (group_box, path_label, browse_button)
        """
        group = QGroupBox(label_text)
        layout = QHBoxLayout()
        
        path_label = QLabel("未选择")
        path_label.setWordWrap(True)
        path_label.setStyleSheet("color: gray;")
        
        browse_btn = QPushButton(button_text)
        browse_btn.setMinimumWidth(100)
        
        if file_mode:
            browse_btn.clicked.connect(
                lambda: self._browse_file(path_label, file_filter, callback)
            )
        else:
            browse_btn.clicked.connect(
                lambda: self._browse_directory(path_label, callback)
            )
        
        layout.addWidget(path_label, stretch=1)
        layout.addWidget(browse_btn)
        group.setLayout(layout)
        
        return group, path_label, browse_btn
    
    def _browse_file(
        self, 
        label: QLabel, 
        file_filter: str,
        callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """Open file dialog and update label."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", file_filter
        )
        if file_path:
            label.setText(file_path)
            label.setStyleSheet("color: black;")
            label.setToolTip(file_path)
            if callback:
                callback(file_path)
    
    def _browse_directory(
        self, 
        label: QLabel,
        callback: Optional[Callable[[str], None]] = None
    ) -> None:
        """Open directory dialog and update label."""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            label.setText(dir_path)
            label.setStyleSheet("color: black;")
            label.setToolTip(dir_path)
            if callback:
                callback(dir_path)
    
    def create_open_folder_checkbox(self, default_checked: bool = True) -> QCheckBox:
        """
        Create the 'Open folder after conversion' checkbox.
        
        Args:
            default_checked: Whether the checkbox is checked by default
            
        Returns:
            The checkbox widget
        """
        checkbox = QCheckBox("完成后打开文件夹")
        checkbox.setChecked(default_checked)
        return checkbox
    
    def create_progress_bar(self) -> QProgressBar:
        """
        Create a progress bar with standard settings.
        
        Returns:
            The progress bar widget
        """
        progress_bar = QProgressBar()
        progress_bar.setVisible(False)
        progress_bar.setRange(0, 100)
        return progress_bar
    
    def create_action_button(self, text: str) -> QPushButton:
        """
        Create the main action button with standard styling.
        
        Args:
            text: Button text
            
        Returns:
            The button widget
        """
        btn = QPushButton(text)
        btn.setMinimumHeight(40)
        btn.setStyleSheet("""
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
                background-color: #BDBDBD;
            }
        """)
        return btn
    
    def start_worker(
        self,
        worker_func: Callable,
        *args: Any,
        finished_callback: Optional[Callable[[bool, str], None]] = None,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> None:
        """
        Start a worker thread with proper setup.
        
        Args:
            worker_func: Function to run in worker thread
            *args: Arguments for worker function
            finished_callback: Callback when worker finishes (success, message)
            progress_callback: Callback for progress updates (percentage)
        """
        self.worker = Worker(worker_func, *args)
        
        if finished_callback:
            self.worker.finished.connect(finished_callback)
        if progress_callback:
            self.worker.progress.connect(progress_callback)
            
        self.worker.start()
    
    def show_success_message(
        self, 
        title: str, 
        message: str, 
        detail: str
    ) -> None:
        """Show a success message box."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setDetailedText(detail)
        msg.exec()
    
    def show_error_message(self, title: str, message: str) -> None:
        """Show an error message box."""
        QMessageBox.critical(self, title, message)
    
    def show_warning_message(self, title: str, message: str) -> None:
        """Show a warning message box."""
        QMessageBox.warning(self, title, message)
    
    def open_folder(self, path: str) -> None:
        """
        Open a folder in the system file manager.
        
        Args:
            path: Path to folder (or file, in which case parent folder is opened)
        """
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if os.path.exists(path):
            webbrowser.open(path)
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Validate that a file exists and show error if not.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if file exists, False otherwise
        """
        if not file_path or not os.path.exists(file_path):
            self.show_error_message("错误", "请选择有效的文件。")
            return False
        return True
    
    def validate_directory(self, dir_path: str) -> bool:
        """
        Validate that a directory exists and show error if not.
        
        Args:
            dir_path: Path to validate
            
        Returns:
            True if directory exists, False otherwise
        """
        if not dir_path:
            self.show_error_message("错误", "请选择输出目录。")
            return False
        if not os.path.exists(dir_path):
            self.show_error_message("错误", "输出目录不存在。")
            return False
        return True
