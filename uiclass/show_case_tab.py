import os
import time
import xml.etree.cElementTree as ET
from threading import Thread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QFileDialog, QToolButton, QListWidgetItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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
        self.import_button.setToolTip('import')
        self.import_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_import + ')}')
        self.import_button.clicked.connect(lambda: self.connect_import_button(None))
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('select_all')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
        self.select_all_button.clicked.connect(self.connect_select_all_items)
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('execute')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_execute + ')}')
        self.execute_button.clicked.connect(self.connect_execute_selected_items)
        h_box = QHBoxLayout()
        h_box.addWidget(self.import_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addStretch(1)
        self.list_widget = QListWidget()
        v_box = QVBoxLayout()
        v_box.addLayout(h_box)
        v_box.addWidget(self.list_widget)
        self.setLayout(v_box)


    # 连接导入case按钮
    def connect_import_button(self, path=None):
        # 通过选择框导入case
        if path is None:
            script_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='script_path').value
            case_folder = QFileDialog.getExistingDirectory(self, '选择case所在文件夹', script_path)
            if case_folder:
                # 将当前script路径保存到配置文件
                if case_folder != script_path:
                    Profile(type='write', file=GloVar.config_file_path, section='param', option='script_path', value=case_folder)
            else:
                case_folder = None
        # 直接通过参数导入case
        else:
            case_folder = path
            if case_folder is None:
                return
        # 保存当前case所在路径
        self.script_path = case_folder
        # 导入case的具体操作
        if case_folder is not None:
            self.clear_all_items()
            for home, dirs, files in os.walk(case_folder):
                for file in files:
                    # 判断脚本文件(通过后缀名)
                    (file_text, extension) = os.path.splitext(file)
                    if extension in ['.xml', '.XML']:
                        # 文件名列表, 包含完整路径
                        case_file = MergePath([home, file]).merged_path
                        # 将文件名传入
                        self.add_item(case_file)
            WindowStatus.case_tab_status = 'case路径>%s!' % case_folder
        else:
            Logger('没有选择case所在文件夹')


    def connect_select_all_items(self):
        # 没有item的时候让button无效
        if self.index < 0:
            pass
        else:
            Thread(target=self.select_or_un_select_all_items, args=()).start()


    # 执行选中的case
    def execute_selected_items(self):
        if GloVar.request_status is None:
            Logger('[当前还有正在执行的动作, 请稍后执行!]')
            return
        for i in range(self.index+1):
            if self.case_control_list[i].check_box.checkState() == Qt.Checked:
                while True:
                    if GloVar.request_status == 'ok':
                        GloVar.request_status = None
                        dict_info_list = self.read_script_tag(i)
                        self.play_single_case(dict_info_list)
                        self.signal.emit('play_single_case>')
                        break
                    else:
                        time.sleep(0.002)


    # 线程中执行选中的case
    def connect_execute_selected_items(self):
        Thread(target=self.execute_selected_items, args=()).start()


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