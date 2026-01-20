from PyQt6.QtCore import QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(int)  # progress percentage

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # Pass progress callback to the function
            result = self.func(*self.args, progress_callback=self.update_progress, **self.kwargs)
            self.finished.emit(True, "Operation completed successfully.")
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def update_progress(self, value):
        """Update progress and emit signal"""
        self.progress.emit(value)
