from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ShowScriptTab(QTextEdit):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ShowScriptTab, self).__init__(parent)
        self.parent = parent
        self.setReadOnly(True)
        # self.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setStyleSheet('background-color:#C0D8F0')
        self.setFont(QFont('Times New Roman', 13))