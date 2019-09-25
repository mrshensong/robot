from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.action_tab import Action_Tab

class TabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, tab1='action', tab2='edit'):
        super(TabWidget, self).__init__(parent)
        self.parent = parent
        self.setTabPosition(self.South)

        self.action_tab = Action_Tab(self)  # 1
        self.action_tab.signal[str].connect(self.recv_action_tab_signal)
        self.text_tab   = QTextEdit()
        # self.text_tab.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.text_tab.setWordWrapMode(QTextOption.NoWrap)
        self.text_tab.setStyleSheet('background-color:lightGreen')
        self.text_tab.setFont(QFont('Times New Roman', 13))
        self.addTab(self.action_tab, tab1)
        self.addTab(self.text_tab, tab2)


    # 接收从子tab窗口传来的信号
    def recv_action_tab_signal(self, signal_str):
        if signal_str.startswith('action>'):
            self.signal.emit(signal_str)
        elif signal_str.startswith('script_tag>'):
            self.text_tab.setText(signal_str.split('script_tag>')[1])
        elif signal_str.startswith('execute>'):
            self.signal.emit(signal_str)