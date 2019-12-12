import os
import time
import xml.etree.cElementTree as ET
from threading import Thread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QFileDialog, QToolButton, QListWidgetItem, QSpinBox, QLabel
from PyQt5.QtCore import *
from GlobalVar import IconPath, Logger, GloVar, MergePath, WindowStatus, Profile, MotionAction, RecordAction, SleepAction, RobotArmParam
from uiclass.controls import CaseControl

class ShowCaseTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ShowCaseTab, self).__init__(parent)
        self.parent = parent
        self.index = -1
        # case控件列表
        self.case_control_list = []
        # item列表
        self.item_list = []
        # case文件列表
        self.case_file_list = []
        # 是否全部选中状态(False:没有全部选中, True:全部选中)
        self.select_all_flag = False
        # 当前打开的脚本路径
        self.script_path = None
        self.case_tab_init()


    def case_tab_init(self):
        self.import_button = QToolButton()
        self.import_button.setShortcut('o')
        self.import_button.setToolTip('import')
        self.import_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_import + ')}')
        self.import_button.clicked.connect(lambda : self.connect_import_button(None))
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('select_all')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
        self.select_all_button.clicked.connect(self.connect_select_all_items)
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('execute')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_execute + ')}')
        self.execute_button.clicked.connect(self.connect_execute_selected_items)
        # 切换按钮(是否需要产生报告)
        self.switch_button = QToolButton()
        self.switch_button.setMinimumWidth(40)
        self.switch_button.setToolTip('switch_off')
        self.switch_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
        self.switch_button.clicked.connect(self.connect_switch)
        # 次数标签
        self.execute_times_label = QLabel()
        self.execute_times_label.setText('次数:')
        self.execute_times_control = QSpinBox()
        self.execute_times_control.setRange(1, 10)
        self.execute_times_control.setValue(1)

        h_box = QHBoxLayout()
        h_box.addWidget(self.import_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addWidget(self.switch_button)
        h_box.addWidget(self.execute_times_label)
        h_box.addWidget(self.execute_times_control)
        h_box.addStretch(1)
        self.list_widget = QListWidget()
        v_box = QVBoxLayout()
        # 左上右下
        v_box.setContentsMargins(0, 5, 0, 0)
        v_box.addLayout(h_box)
        v_box.addWidget(self.list_widget)
        self.setLayout(v_box)


    # 连接导入case按钮
    def connect_import_button(self, case_file=None):
        if case_file is None:
            # 通过选择框导入case
            script_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='script_path').value
            files, ok = QFileDialog.getOpenFileNames(self, "选择case", script_path, "标签文件 (*.xml)")
            if ok:
                # 如果打开路径和配置文件路径不一样, 就将当前script路径保存到配置文件
                case_folder = os.path.split(files[0])[0]
                if case_folder != script_path:
                    Profile(type='write', file=GloVar.config_file_path, section='param', option='script_path', value=case_folder)
                # 清除所有case
                self.clear_all_items()
                # 文件按照时间排序(倒序排列)
                files = sorted(files, key=lambda file: os.path.getmtime(file), reverse=True)
                for file in files:
                    self.add_item(file)
                WindowStatus.case_tab_status = 'case路径>%s!' % case_folder
            else:
                Logger('没有选择case')
        else:
            files = self.case_file_list
            files.insert(0, case_file)
            self.clear_all_items()
            # 文件按照时间排序(倒序排列)
            files = sorted(files, key=lambda file: os.path.getmtime(file), reverse=True)
            for file in files:
                self.add_item(file)


    def connect_select_all_items(self):
        # 没有item的时候让button无效
        if self.index < 0:
            pass
        else:
            Thread(target=self.select_or_un_select_all_items, args=()).start()


    # 执行选中的case
    def execute_selected_items(self, execute_times):
        if GloVar.request_status is None:
            Logger('[当前还有正在执行的动作, 请稍后执行!]')
            return
        for i in range(self.index+1):
            if self.case_control_list[i].check_box.checkState() == Qt.Checked:
                # 根据执行次数执行
                for x in range(execute_times):
                    while True:
                        if GloVar.request_status == 'ok':
                            GloVar.request_status = None
                            dict_info_list = self.read_script_tag(i)
                            self.play_single_case(dict_info_list)
                            self.signal.emit('play_single_case>')
                            break
                        else:
                            time.sleep(0.002)
                        # 执行每一条case后cpu休息一秒钟
                        time.sleep(1)
        # 测试执行结束(改变标志位)
        while True:
            if GloVar.request_status == 'ok':
                self.signal.emit('test_finished>')
                break
            else:
                time.sleep(0.02)


    # 线程中执行选中的case
    def connect_execute_selected_items(self):
        # 每执行一次都需要获取当前时间(作为文件夹)
        GloVar.current_time = time.strftime('%H-%M-%S', time.localtime(time.time()))
        # 获取执行次数
        execute_times = self.execute_times_control.value()
        Thread(target=self.execute_selected_items, args=(execute_times,)).start()


    # 视频处理开关切换
    def connect_switch(self):
        # 打开开关
        if GloVar.video_process_switch == 'OFF':
            GloVar.video_process_switch = 'ON'
            self.switch_button.setToolTip('switch_off')
            self.switch_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
        # 关闭开关
        else:
            GloVar.video_process_switch = 'OFF'
            self.switch_button.setToolTip('switch_on')
            self.switch_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_switch_off + ')}')


    # 接受case控件发送的信号
    def recv_case_control_signal(self, signal_str):
        # 打开当前case(拆分为action)
        if signal_str.startswith('open_case>'):
            id = int(signal_str.split('>')[1])
            case_info_list = self.read_script_tag(id)
            self.signal.emit('case_transform_to_action>'+str(case_info_list))
        # 执行单个case
        elif signal_str.startswith('play_single_case>'):
            if GloVar.request_status is None:
                Logger('[当前还有正在执行的动作, 请稍后执行!]')
                return
            id = int(signal_str.split('>')[1])
            dict_info_list = self.read_script_tag(id)
            self.play_single_case(dict_info_list)
            self.signal.emit('play_single_case>')
        else:
            pass


    # 读取当前的script_xml文件(通过id可以获取到当前脚本文件)
    # 返回list为每个action的信息(字典形式)>>list第一个参数为case文件名, 后面参数为每个action的信息存储字典
    def read_script_tag(self, id):
        case_file = self.case_file_list[id]
        tree = ET.ElementTree(file=case_file)
        root = tree.getroot()
        dict_list, new_dict_info = [], []
        new_dict_info.append(root.attrib['name']) # 文件名
        new_dict_info.append(self.case_file_list[id]) # 完整路径
        for child_of_root in root:
            child_info_list = []
            if child_of_root.tag == 'action':
                child_info_list.append(child_of_root.attrib)
                for child_child_of_root in child_of_root:
                    dict_info = {child_child_of_root.attrib['name']: child_child_of_root.text}
                    child_info_list.append(dict_info)
                dict_list.append(child_info_list)
        for info in dict_list:
            dict_buffer = {}
            for dict_info in info:
                dict_buffer.update(dict_info)
            new_dict_info.append(dict_buffer)
        return new_dict_info


    # 执行单个case(参数为从xml中读出来的)
    def play_single_case(self, dict_info_list):
        # list中第一个参数为case文件名, 第二个参数为case完整路径, 后面的为动作信息(action展示需要用到)
        # self.action_tab.case_file_name = dict_info_list[0]
        # self.action_tab.case_absolute_name = dict_info_list[1]
        GloVar.post_info_list = []
        GloVar.post_info_list.append('start>'+dict_info_list[1])
        for id in range(2, len(dict_info_list)):
            # 判断是action控件
            if MotionAction.points in dict_info_list[id]:
                # info_dict长度大于2为action控件
                # 将字典中的'(0, 0)'转为元祖(0, 0)
                dict_info_list[id]['points'] = eval(dict_info_list[id]['points'])
                # 一个action字典中需要标明什么类型动作
                dict_info_list[id]['execute_action'] = 'motion_action'
                dict_info_list[id]['base'] = (RobotArmParam.base_x_point, RobotArmParam.base_y_point, RobotArmParam.base_z_point)
                GloVar.post_info_list.append(dict_info_list[id])
            # 为record或者sleep控件
            else:
                # 为record控件
                if RecordAction.record_status in dict_info_list[id]:
                    dict_info_list[id]['execute_action'] = 'record_action'
                    # 添加视频存放根目录
                    dict_info_list[id]['video_path'] = GloVar.project_video_path
                    GloVar.post_info_list.append(dict_info_list[id])
                # 为sleep控件
                elif SleepAction.sleep_time in dict_info_list[id]:
                    dict_info_list[id]['execute_action'] = 'sleep_action'
                    GloVar.post_info_list.append(dict_info_list[id])
        GloVar.post_info_list.append('stop')
        # 执行一条case
        # self.signal.emit('sleep_execute_item>' + json.dumps(GloVar.post_info_list))


    # 清除所有动作
    def clear_all_items(self):
        self.list_widget.clear()
        self.item_list = []
        self.case_control_list = []
        self.case_file_list = []
        self.index = -1


    # 全部选中或者全部不选中items
    def select_or_un_select_all_items(self):
        if self.select_all_flag is False:
            for i in range(self.index + 1):
                self.case_control_list[i].check_box.setCheckState(Qt.Checked)
            self.select_all_flag = True
            self.select_all_button.setToolTip('un_select_all')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_un_select + ')}')
            Logger('[全部选中]-->所有case')
        else:
            for i in range(self.index + 1):
                self.case_control_list[i].check_box.setCheckState(Qt.Unchecked)
            self.select_all_flag = False
            self.select_all_button.setToolTip('select_all')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
            Logger('[全不选中]-->所有case')


    # 添加动作控件
    def add_item(self, case_file):
        # 给动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 70))
        obj = CaseControl(parent=None, id=self.index, case_file=case_file)
        obj.signal[str].connect(self.recv_case_control_signal)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, obj)
        self.item_list.append(obj)
        self.case_control_list.append(obj)
        self.case_file_list.append(case_file)