from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.action_tab import Action_Tab
from uiclass.case_tab import Case_Tab
from GlobalVar import robot_other, logger

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
            # 设置当前tab页面
            self.setCurrentWidget(self.action_tab)
            # 如果还有actions未保存(判断是否需要将当前actions保存为case)
            if robot_other.actions_saved_to_case is False:
                reply = QMessageBox.question(self, 'action_tab页有actions未保存为case', '是否要将当前actions保存为case?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.action_tab.connect_save_script_tag()
                else:
                    self.action_tab.clear_all_items()
                    logger('[请重新打开case脚本!]')
                    self.setCurrentWidget(self.case_tab)
            else: # action_tab界面当前所有actions都已经保存完, 可以打开当前双击的case
                self.action_tab.clear_all_items()
                dict_info_list = eval(signal_str.split('case_transform_to_action>')[1])
                # list中第一个参数为case文件名, 后面的为动作信息
                self.action_tab.case_file_name = dict_info_list[0]
                for id in range(1, len(dict_info_list)):
                    # 将字典中的'(0, 0)'转为元祖(0, 0)
                    dict_info_list[id]['points'] = eval(dict_info_list[id]['points'])
                    self.action_tab.add_item(dict_info_list[id], flag=False)