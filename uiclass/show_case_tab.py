import os
import time
import xml.etree.cElementTree as ET
from threading import Thread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QFileDialog, QToolButton, QListWidgetItem, QSpinBox, QLabel, QLineEdit, QFrame
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import IconPath, Logger, GloVar, WindowStatus, Profile, MotionAction, RecordAction, AssertAction, SleepAction, RobotArmParam, BeautifyStyle
from uiclass.controls import CaseControl

class ShowCaseTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ShowCaseTab, self).__init__(parent)
        self.parent = parent
        # 样式美化
        style = BeautifyStyle.font_family + BeautifyStyle.font_size + BeautifyStyle.file_dialog_qss
        self.setStyleSheet(style)
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
        # 初始化
        self.case_tab_init()


    def case_tab_init(self):
        # 添加case
        self.add_button = QToolButton()
        self.add_button.setToolTip('添加case')
        self.add_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_add + ')}')
        self.add_button.clicked.connect(lambda : self.connect_import_button(None))
        # 批量删除case
        self.delete_button = QToolButton()
        self.delete_button.setToolTip('批量删除case')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_delete + ')}')
        self.delete_button.clicked.connect(self.connect_delete_selected_items)
        # 全部选中(不选中)
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('全部选中')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
        self.select_all_button.clicked.connect(self.connect_select_all_items)
        # 批量执行
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('批量执行case')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_execute + ')}')
        self.execute_button.clicked.connect(self.connect_execute_selected_items)
        # 切换按钮(是否需要产生报告)
        self.switch_button = QToolButton()
        self.switch_button.setMinimumWidth(40)
        self.switch_button.setToolTip('关闭处理报告功能')
        self.switch_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
        self.switch_button.clicked.connect(self.connect_switch)
        # 次数标签
        self.execute_times_label = QLabel()
        self.execute_times_label.setText('次数:')
        self.execute_times_control = QSpinBox()
        self.execute_times_control.setStyleSheet('QSpinBox {background-color:transparent}')
        self.execute_times_control.setRange(1, 10)
        self.execute_times_control.setValue(1)
        # case所在文件夹
        self.case_folder_text = QLineEdit()
        self.case_folder_text.setStyleSheet('background-color:transparent')
        self.case_folder_text.setReadOnly(True)
        self.case_folder_text.setText('空白')
        # 布局
        h_box = QHBoxLayout()
        h_box.setSpacing(5)
        h_box.addWidget(self.add_button)
        h_box.addWidget(self.delete_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addWidget(self.switch_button)
        h_box.addWidget(self.execute_times_label)
        h_box.addWidget(self.execute_times_control)
        h_box.addStretch(1)
        self.list_widget = QListWidget()
        self.list_widget.verticalScrollBar().setStyleSheet("QScrollBar{width:10px;}")
        self.list_widget.horizontalScrollBar().setStyleSheet("QScrollBar{height:10px;}")
        v_box = QVBoxLayout()
        v_box.setSpacing(0)
        # 左上右下
        v_box.setContentsMargins(0, 0, 0, 0)
        v_box.addWidget(self.case_folder_text)
        v_box.addSpacing(3)
        v_box.addLayout(h_box)
        v_box.addSpacing(3)
        v_box.addWidget(self.list_widget)
        self.setLayout(v_box)

    # 连接导入case按钮
    def connect_import_button(self, case_file=None):
        if case_file is None:
            # 通过选择框导入case
            script_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='script_path').value
            files, ok = QFileDialog.getOpenFileNames(self, "选择case", script_path, "标签文件 (*.xml)", options=QFileDialog.DontUseNativeDialog)
            if ok:
                # 如果打开路径和配置文件路径不一样, 就将当前script路径保存到配置文件
                case_folder = os.path.split(files[0])[0]
                if case_folder != script_path:
                    Profile(type='write', file=GloVar.config_file_path, section='param', option='script_path', value=case_folder)

                # 文件去重
                files = self.case_file_list + files
                files = list(set(files))
                # 文件按照时间排序(倒序排列)
                files = sorted(files, key=lambda file: os.path.getmtime(file), reverse=True)
                self.clear_all_items()
                for file in files:
                    self.add_item(file)
                self.case_file_list = files
                WindowStatus.case_tab_status = 'case路径>%s' % case_folder
                self.case_folder_text.setText(case_folder)
            else:
                Logger('没有选择case')
        else:
            # 插入第一个并去重
            files = self.case_file_list
            files.insert(0, case_file)
            files = list(set(files))
            self.clear_all_items()
            # 文件按照时间排序(倒序排列)
            files = sorted(files, key=lambda file: os.path.getmtime(file), reverse=True)
            for file in files:
                self.add_item(file)

    # 1.筛选出没有被选中的items, 并将他们的info保存到list 2.使用循环创建没有被选中的items
    def delete_selected_items(self):
        # (从后面开始删除)先删除后面的(每次循环递减一个)
        index = len(self.case_control_list) - 1
        # 通过判断剩余item数量, 来确定是否需要更改‘全选’按键状态
        exist_items_count = index + 1
        # 获取到第一个删除项的下一项case名字(重写这一项就不会出现文本框选中现象, 不然会出现文本框选中现象)
        get_rewrite_case_name_flag = False
        # 重写case名字
        rewrite_case_name = None
        # 使用循环删除掉选中的case
        while True:
            if exist_items_count < 1:
                # 全部删除后需要复位全部选中按钮的状态
                self.select_all_flag = False
                self.select_all_button.setToolTip('全部选中')
                self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
                break
            # 遍历完item后退出
            elif index < 0:
                break
            # 未遍历完item, 判断是否选中
            else:
                if self.case_control_list[index].check_box.checkState() == Qt.Checked:
                    if index < (len(self.case_control_list)-1) and get_rewrite_case_name_flag is False:
                        get_rewrite_case_name_flag = True
                        # 获取当前选中的下一项
                        rewrite_case_name = self.case_file_list[index + 1]
                    # 模拟点击case中的单独delete按钮(稳定)
                    self.case_control_list[index].delete_button.click()
                    exist_items_count -= 1
            index -= 1
        # 全部删除后需要复位全部选中按钮的状态
        self.select_all_flag = False
        self.select_all_button.setToolTip('全部选中')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
        # 处理出现的选中文本框
        if rewrite_case_name is not None:
            time.sleep(0.01)
            try: # 此处有可能产生异常(直接跳过即可)
                current_row = self.case_file_list.index(rewrite_case_name)
                text = self.case_control_list[current_row].case_name_edit.text()
                self.case_control_list[current_row].case_name_edit.setText(text)
            except:
                pass

    def connect_delete_selected_items(self):
        # 没有item的时候让button无效
        if self.index < 0:
            pass
        else:
            Thread(target=self.delete_selected_items, args=()).start()

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
        self.signal.emit('ready_execute_case>')
        time.sleep(0.3)
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
        # 测试执行结束(改变标志位, 触发数据处理函数)
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
            self.switch_button.setToolTip('关闭处理报告功能')
            self.switch_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
        # 关闭开关
        else:
            GloVar.video_process_switch = 'OFF'
            self.switch_button.setToolTip('开启处理报告功能')
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
        # 删除case
        elif signal_str.startswith('delete_case>'):
            id = int(signal_str.split('delete_case>')[1])
            self.delete_item(id)
        else:
            pass

    # 读取当前的script_xml文件(通过id可以获取到当前脚本文件)
    # 返回list为每个action的信息(字典形式)>>list第一个参数为case文件名, 后面参数为每个action的信息存储字典
    def read_script_tag(self, id):
        case_file = self.case_file_list[id]
        try:
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
        except:
            file_name = os.path.split(case_file)[1]
            new_dict_info = [file_name, case_file]
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
                elif AssertAction.assert_template_name in dict_info_list[id]:
                    dict_info_list[id]['execute_action'] = 'assert_action'
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
            self.select_all_button.setToolTip('全不选中')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_un_select + ')}')
            Logger('[全部选中]-->所有case')
        else:
            for i in range(self.index + 1):
                self.case_control_list[i].check_box.setCheckState(Qt.Unchecked)
            self.select_all_flag = False
            self.select_all_button.setToolTip('全部选中')
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
        self.item_list.append(item)
        self.case_control_list.append(obj)
        self.case_file_list.append(case_file)

    # 删除case
    def delete_item(self, id):
        self.list_widget.takeItem(id)
        self.item_list.pop(id)
        self.case_control_list.pop(id)
        self.case_file_list.pop(id)
        for i in range(id, self.index):
            self.case_control_list[i].id = i
        self.index -= 1
