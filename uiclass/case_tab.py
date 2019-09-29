import os
import json
import time
import xml.etree.cElementTree as ET
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import icon_path, add_action_window, uArm_action, logger, gloVar, merge_path, window_status, profile
from uiclass.controls import Case_Control

class Case_Tab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(Case_Tab, self).__init__(parent)
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
        self.case_tab_init()


    def case_tab_init(self):
        self.import_button = QToolButton()
        self.import_button.setToolTip('import')
        self.import_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_import + ')}')
        self.import_button.clicked.connect(self.connect_import_button)
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('select_all')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_select + ')}')
        self.select_all_button.clicked.connect(self.connect_select_all_items)
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('execute')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_execute + ')}')
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
    def connect_import_button(self):
        script_path = profile(type='read', file=gloVar.config_file_path, section='param', option='script_path').path
        case_folder = QFileDialog.getExistingDirectory(self, '选择case所在文件夹', script_path)
        if case_folder:
            if case_folder != script_path:
                profile(type='write', file=gloVar.config_file_path, section='param', option='script_path', value=case_folder)
            self.clear_all_items()
            for home, dirs, files in os.walk(case_folder):
                for file in files:
                    # 判断脚本文件(通过后缀名)
                    (file_text, extension) = os.path.splitext(file)
                    if extension in ['.xml', '.XML']:
                        # 文件名列表, 包含完整路径
                        case_file = merge_path([home, file]).merged_path
                        # 将文件名传入
                        self.add_item(case_file)
            window_status.case_tab_status = 'case所在文件夹-->>%s!'%case_folder
        else:
            logger('没有选择case所在文件夹')


    def connect_select_all_items(self):
        # 没有item的时候让button无效
        if self.index < 0:
            pass
        else:
            Thread(target=self.select_or_un_select_all_items, args=()).start()


    def connect_execute_selected_items(self):
        pass


    # 播放单个case
    def play_item(self, id):
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('execute>'+json.dumps(self.info_list[id]))


    # 接受case控件发送的信号
    def recv_case_control_signal(self, signal_str):
        # 打开当前case(拆分为action)
        if signal_str.startswith('open_case>'):
            id = int(signal_str.split('>')[1])
            case_info_list = self.read_script_tag(id)
            self.signal.emit('case_transform_to_action>'+str(case_info_list))
        else:
            pass


    # 读取当前的script_xml文件(通过id可以获取到当前脚本文件)
    # 返回list为每个action的信息(字典形式)>>list第一个参数为case文件名, 后面参数为每个action的信息存储字典
    def read_script_tag(self, id):
        case_file = self.case_file_list[id]
        logger('[打开的case路径为]: %s' %case_file)
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
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_un_select + ')}')
            logger('[全部选中]-->所有case')
        else:
            for i in range(self.index + 1):
                self.case_control_list[i].check_box.setCheckState(Qt.Unchecked)
            self.select_all_flag = False
            self.select_all_button.setToolTip('select_all')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_select + ')}')
            logger('[全不选中]-->所有case')


    # 添加动作控件
    def add_item(self, case_file):
        # case名
        case_name = case_file.split('/')[-1]
        # 给动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 70))
        obj = Case_Control(parent=None, id=self.index)
        obj.id = self.index
        obj.case_name_edit.setText(case_name)
        obj.play_botton.clicked.connect(lambda : self.play_item(obj.id))
        obj.signal[str].connect(self.recv_case_control_signal)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, obj)
        self.item_list.append(obj)
        self.case_control_list.append(obj)
        self.case_file_list.append(case_file)


    # 添加动作时生成标签
    def generate_tag(self, info_dict):
        des_text = info_dict[add_action_window.des_text]
        action_type = info_dict[add_action_window.action_type]
        points = str(tuple(info_dict[add_action_window.points]))
        tag = '\t<action ' + add_action_window.des_text + '="' + des_text + '">\n' + \
              '\t\t' + '<param name="' + add_action_window.action_type + '">' + action_type + '</param>\n' + \
              '\t\t' + '<param name="' + add_action_window.points + '">' + points + '</param>\n' + \
              '\t</action>\n'
        return tag