from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.action_tab import Action_Tab
from uiclass.case_tab import Case_Tab

class TabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, action_tab='action', case_tab='case', text_tab='edit'):
        super(TabWidget, self).__init__(parent)
        self.parent = parent
        self.setTabPosition(self.South)
        # tab1
        self.action_tab = Action_Tab(self)  # 1
        self.action_tab.signal[str].connect(self.recv_action_tab_signal)
        # tab2
        self.case_tab = Case_Tab(self)
        self.case_tab.signal[str].connect(self.recv_case_tab_signal)
        # tab3
        self.text_tab   = QTextEdit(self)
        # self.text_tab.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.text_tab.setWordWrapMode(QTextOption.NoWrap)
        self.text_tab.setStyleSheet('background-color:lightGreen')
        self.text_tab.setFont(QFont('Times New Roman', 13))
        self.addTab(self.action_tab, action_tab)
        self.addTab(self.case_tab, case_tab)
        self.addTab(self.text_tab, text_tab)


    # 接收从action_tab窗口传来的信号
    def recv_action_tab_signal(self, signal_str):
        if signal_str.startswith('action>'):
            self.signal.emit(signal_str)
        elif signal_str.startswith('script_tag>'):
            self.text_tab.setText(signal_str.split('script_tag>')[1])
        elif signal_str.startswith('execute>'):
            self.signal.emit(signal_str)
        elif signal_str.startswith('case_transform_to_action>'):
            dict_info_list = eval(signal_str.split('case_transform_to_action>')[1])
            print(dict_info_list)
            for id in range(len(dict_info_list)):
                self.action_tab.add_item(dict_info_list[id])


    # 接收从case_tab窗口传来的信号
    def recv_case_tab_signal(self, signal_str):
        # 双击case后将case中的action展示出来
        if signal_str.startswith('case_transform_to_action>'):
            signal_str = signal_str.replace('description', 'des_text')
            signal_str = signal_str.replace('type', 'action')
            signal_str = signal_str.replace('position', 'points')
            dict_info_list = eval(signal_str.split('case_transform_to_action>')[1])
            for id in range(len(dict_info_list)):
                dict_info_list[id]['points'] = eval(dict_info_list[id]['points'])
                self.action_tab.add_item(dict_info_list[id])