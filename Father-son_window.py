import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal


class MainWindow(QMainWindow):

    my_signal = pyqtSignal(str)

    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        # 设置主窗口的标题及大小
        self.setWindowTitle('主窗口')
        self.resize(400, 300)
        # 创建按钮
        self.btn = QPushButton(self)
        self.btn.setText('弹出对话框')
        self.btn.clicked.connect(self.show_dialog)
        # 自定义信号绑定
        self.my_signal[str].connect(self.test)
        # 创建对话框对象
        self.dialog = Dialog(self)

    def show_dialog(self):
        self.dialog.show()
        self.dialog.exec()

    def test(self):
        self.btn.setText('我改变了')


class Dialog(QDialog):

    my_signal = pyqtSignal(str)

    def __init__(self, parent):
        super(Dialog, self).__init__(parent)
        self.parent = parent
        # 设置对话框的标题及大小
        self.setWindowTitle('对话框')
        self.resize(200, 200)
        self.setWindowModality(Qt.ApplicationModal)
        self.btn = QPushButton(self)
        self.btn.setText('改变主窗口按钮的名称')
        self.btn.clicked.connect(self.sent1)
        # 自定义信号绑定
        self.my_signal[str].connect(self.sent2)

    def sent1(self):
        self.my_signal.emit('1')


    def sent2(self):
        self.parent.my_signal.emit('1')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())