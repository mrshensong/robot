import time
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker

# 定时器
class Timer(QThread):

    # timeSignal = Communicate()
    timeSignal = pyqtSignal(str)

    def __init__(self, frequent=30):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.mutex = QMutex()


    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            # self.timeSignal.signal.emit("1")
            self.timeSignal.emit("1")
            time.sleep(1 / self.frequent)


    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True


    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped


    def set_fps(self, fps):
        self.frequent = fps