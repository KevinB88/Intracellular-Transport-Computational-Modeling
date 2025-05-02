from PyQt6.QtCore import QObject, pyqtSignal
import traceback


class Worker(QObject):
    finished = pyqtSignal(object, str)  # result, function name
    error = pyqtSignal(str, str)        # error message, function name

    def __init__(self, fn, fn_name, kwargs):
        super().__init__()
        self.fn = fn
        self.fn_name = fn_name
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.fn(**self.kwargs)
            self.finished.emit(result, self.fn_name)
        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"{e}\n\n{tb}", self.fn_name)
