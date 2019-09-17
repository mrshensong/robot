from PyQt5.QtCore import *


# 视频显示调用的定时线程
class Communicate(QObject):
    signal = pyqtSignal(str)