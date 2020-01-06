from PyQt5.QtCore import pyqtSignal, QObject

# 发射控制台内容
class Stream(QObject):
    newText = pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))