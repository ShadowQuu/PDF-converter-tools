from PyQt6.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import os

class FileListWidget(QListWidget):
    files_dropped = pyqtSignal(list)

    def __init__(self, allowed_extensions=None):
        super().__init__()
        self.allowed_extensions = allowed_extensions  # e.g., ['.jpg', '.png'] or ['.pdf']
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            
            files = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.is_valid_file(file_path):
                    files.append(file_path)
            
            if files:
                self.add_files(files)
                self.files_dropped.emit(files)
        else:
            super().dropEvent(event)

    def is_valid_file(self, file_path):
        if not os.path.isfile(file_path):
            return False
        if not self.allowed_extensions:
            return True
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.allowed_extensions

    def add_files(self, file_paths):
        for path in file_paths:
            # Check if file already exists in list to avoid duplicates
            # Directly check by path instead of by filename for accuracy
            is_duplicate = False
            for i in range(self.count()):
                if self.item(i).data(Qt.ItemDataRole.UserRole) == path:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                # Use filename as default text, but allow editing
                filename = os.path.basename(path)
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setToolTip(path)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.addItem(item)

    def get_all_files(self):
        files = []
        for i in range(self.count()):
            files.append(self.item(i).data(Qt.ItemDataRole.UserRole))
        return files

    def get_files_with_titles(self):
        """Returns list of tuples (path, title)"""
        files = []
        for i in range(self.count()):
            item = self.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            title = item.text()
            files.append((path, title))
        return files

    def remove_selected_files(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))
