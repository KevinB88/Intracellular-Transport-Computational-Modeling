import sys
from PyQt5.QtCore import QObject, pyqtSignal


class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._buffer = ""

    def write(self, text):
        # Handle carriage return (\r) for overwrite-style updates
        if "\r" in text:
            self._buffer = text.split("\r")[-1]  # Keep only the last overwrite line
        elif text.endswith("\n"):
            self._buffer += text
            self.text_written.emit(self._buffer)
            self._buffer = ""
        else:
            self._buffer += text

    def flush(self):
        if self._buffer:
            self.text_written.emit(self._buffer)
            self._buffer = ""

# Usage: In controller.py or views.py
# sys.stdout = EmittingStream()  # Connect this to a QTextEdit's append method
