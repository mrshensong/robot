from PyQt5.QtWidgets import QTabWidget, QMessageBox, QFrame
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.show_action_tab import ShowActionTab
from uiclass.show_case_tab import ShowCaseTab
from uiclass.show_script_tab import ShowScriptTab
from GlobalVar import GloVar, WindowStatus, RecordAction, SleepAction, Logger, MotionAction

class ShowTabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, action_tab='action', case_tab='case', text_tab='edit'):
        super(ShowTabWidget, self).__init__(parent)
        self.parent = parent
        self.setTabPosition(self.South)
        # tab1
        self.action_tab = ShowActionTab(self)  # 1
        self.action_tab.signal[str].connect(self.recv_action_tab_signal)
        # tab2
        self.case_tab = ShowCaseTab(self)
        self.case_tab.signal[str].connect(self.recv_case_tab_signal)
        # tab3
        self.script_tab   = ShowScriptTab(self)
        # QTabWidget添加tab
        self.addTab(self.case_tab, case_tab)
        self.addTab(self.action_tab, action_tab)
        self.addTab(self.script_tab, text_tab)
        # 调整背景颜色
        # self.setStyleSheet('background-color:#DDDDDD;')
        self.setContentsMargins(0, 0, 0, 0)
        # 准备添加一个底部横线
        # self.bottom_h_line = QFrame(self)
        # self.bottom_h_line.setFrameShape(QFrame.HLine)

    # 接收从action_tab窗口传来的信号
    def recv_action_tab_signal(self, signal_str):
        # 添加action控件时候, 设置动作标志位
        if signal_str.startswith('action_tab_action>'):
            self.signal.emit(signal_str)
        # 更新action脚本
        elif signal_str.startswith('write_script_tag>'):
            script_text = signal_str.split('write_script_tag>')[1]
            script_title = script_text.split('"')[1] if script_text else '空白'
            script_title = '空白' if script_title == '' else script_title
            self.script_tab.script_edit.setText(script_text)
            self.script_tab.script_title.setText(script_title)
        # 保存case
        elif signal_str.startswith('save_case>'):
            script_text = signal_str.split('save_case>')[1]
            script_title = script_text.split('"')[1] if script_text else '空白'
            self.script_tab.script_edit.setText(script_text)
            self.script_tab.script_title.setText(script_title)
            # 在case_tab加入新保存的case
            self.case_tab.connect_import_button(case_file=self.action_tab.case_absolute_name)
            self.case_tab.list_widget.setCurrentRow(0)
            # self.case_tab.case_control_list[0].click()
        # 执行action
        elif signal_str.startswith('play_actions>'):
            self.signal.emit(signal_str)
        # 框选模板(case中录像action的模板图片)
        elif signal_str.startswith('draw_frame>'):
            self.signal.emit(signal_str)


    # 接收从case_tab窗口传来的信号
    def recv_case_tab_signal(self, signal_str):
        # 双击case后将case中的action展示出来
        if signal_str.startswith('case_transform_to_action>'):
            # 设置当前tab页面
            self.setCurrentWidget(self.action_tab)
            # 如果还有actions未保存(判断是否需要将当前actions保存为case)
            if GloVar.actions_saved_to_case is False:
                QMessageBox.warning(self, "警告!action页还有未保存的actions!", "请先保存actions后,再次打开case!", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                Logger('[当前有未保存的actions, 不能打开case!]')
            else: # action_tab界面当前所有actions都已经保存完, 可以打开当前双击的case
                self.action_tab.clear_all_items()
                dict_info_list = eval(signal_str.split('case_transform_to_action>')[1])
                # list中第一个参数为case文件名, 第二个参数为case完整路径, 后面的为动作信息
                self.action_tab.case_file_name = dict_info_list[0]
                self.action_tab.case_absolute_name = dict_info_list[1]
                Logger('[打开的case路径为]: %s' % dict_info_list[1])
                # 遍历case中的action
                for id in range(2, len(dict_info_list)):
                    # 判断是action/record/sleep控件
                    if MotionAction.points in dict_info_list[id]:
                        # 有points元素为action控件
                        # 将字典中的'(0, 0)'转为元祖(0, 0)
                        dict_info_list[id]['points'] = eval(dict_info_list[id]['points'])
                        self.action_tab.add_action_item(dict_info_list[id], new_control_flag=False)
                    # 为record或者sleep控件
                    else:
                        # 为record控件
                        if RecordAction.record_status in dict_info_list[id]:
                            self.action_tab.add_record_item(dict_info_list[id], new_control_flag=False)
                        # 为sleep控件
                        elif SleepAction.sleep_time in dict_info_list[id]:
                            self.action_tab.add_sleep_item(dict_info_list[id], new_control_flag=False)
                self.action_tab.des_text.setText(self.action_tab.case_file_name)
                WindowStatus.action_tab_status = '%s' % self.action_tab.case_absolute_name
        # 执行单个case
        elif signal_str.startswith('play_single_case>'):
            self.signal.emit(signal_str)
        # 开始执行case命令
        elif signal_str.startswith('ready_execute_case>'):
            self.signal.emit(signal_str)
        # 测试结束命令
        elif signal_str.startswith('test_finished>'):
            self.signal.emit(signal_str)