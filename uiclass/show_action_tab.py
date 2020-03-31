import os
import json
import time
from threading import Thread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QToolButton, QListWidget, QMessageBox, QFileDialog, QListWidgetItem, QLineEdit
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import IconPath, MotionAction, RobotArmAction, RecordAction, AssertAction, SleepAction, Logger, GloVar, WindowStatus, Profile, RobotArmParam, BeautifyStyle
from uiclass.controls import ActionControl, RecordControl, AssertControl, SleepControl
from uiclass.add_tab_widget import AddTabWidget


class ShowActionTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ShowActionTab, self).__init__(parent)
        self.parent = parent
        # 样式美化
        style = BeautifyStyle.font_family + BeautifyStyle.font_size + BeautifyStyle.file_dialog_qss
        self.setStyleSheet(style)
        self.index = -1
        # 自定义控件列表
        self.custom_control_list = []
        # item列表
        self.item_list = []
        # 控件中的描述/坐标/动作类型等信息(元素为dict类型)
        self.info_list = []
        # 脚本标签
        self.tag_list = []
        # 是否全部选中状态(False:没有全部选中, True:全部选中)
        self.select_all_flag = False
        # 当前所有action需要保存的文件名(或者打开case时现实的case文件名)
        self.case_file_name = ''
        self.case_absolute_name = ''
        # 插入动作的index位置(不插入的话值为-1, 其他值则为插入地方)
        self.insert_item_index = -1
        # action插入位置变量
        self.insert_item_position = None
        # 插入选中位置上方
        self.insert_up_position = 'UP'
        # 插入选中位置下方
        self.insert_down_position = 'DOWN'
        """
        1.用来解决在一个list_widget中出现多次视频的问题(视频名后以序号区分)
        2.需要保存record_start的视频类型和名字(最近的record_stop需要共用同一个类型和名字)
        """
        # 用来计算当前list_widget中出现的视频次数编号-从零开始(根据序号来命名)
        self.video_numbers = -1
        # tab初始化
        self.action_tab_init()

    def action_tab_init(self):
        self.add_button = QToolButton()
        self.add_button.setToolTip('添加动作')
        self.add_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_add + ')}')
        self.add_button.clicked.connect(self.connect_add_action_button)
        self.insert_above_button = QToolButton()
        self.insert_above_button.setToolTip('上方插入动作')
        self.insert_above_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_insert_above + ')}')
        self.insert_above_button.clicked.connect(lambda : self.connect_insert_button(self.insert_up_position))
        self.insert_below_button = QToolButton()
        self.insert_below_button.setToolTip('下方插入动作')
        self.insert_below_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_insert_below + ')}')
        self.insert_below_button.clicked.connect(lambda : self.connect_insert_button(self.insert_down_position))
        self.delete_button = QToolButton()
        self.delete_button.setToolTip('批量删除动作')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_delete + ')}')
        self.delete_button.clicked.connect(self.connect_delete_selected_items)
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('全部选中')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
        self.select_all_button.clicked.connect(self.connect_select_all_items)
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('批量执行动作')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_execute + ')}')
        self.execute_button.clicked.connect(self.connect_execute_selected_actions)
        self.save_script_tag_button = QToolButton()
        self.save_script_tag_button.setToolTip('保存为case')
        self.save_script_tag_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_save + ')}')
        self.save_script_tag_button.clicked.connect(self.connect_save_script_tag)
        self.draw_frame_button = QToolButton()
        self.draw_frame_button.setShortcut('q')
        self.draw_frame_button.setToolTip('框选视频对比模板')
        self.draw_frame_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_draw_frame + ')}')
        self.draw_frame_button.clicked.connect(self.connect_draw_frame)
        self.des_text = QLineEdit()
        self.des_text.setStyleSheet('background-color:transparent')
        self.des_text.setReadOnly(True)
        self.des_text.setText('空白')

        h_box = QHBoxLayout()
        h_box.setSpacing(5)
        h_box.addWidget(self.add_button)
        h_box.addWidget(self.insert_above_button)
        h_box.addWidget(self.insert_below_button)
        h_box.addWidget(self.delete_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addWidget(self.save_script_tag_button)
        h_box.addWidget(self.draw_frame_button)
        # h_box.addWidget(self.des_text)
        h_box.addStretch(1)
        # 原生QListWidget
        self.list_widget = QListWidget()
        # 将滚动条变细
        self.list_widget.verticalScrollBar().setStyleSheet("QScrollBar{width:10px;}")
        self.list_widget.horizontalScrollBar().setStyleSheet("QScrollBar{height:10px;}")
        # # 取消横向滚动条
        # self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # # 取消竖向滚动条
        # self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        v_box = QVBoxLayout()
        v_box.setSpacing(0)
        v_box.setContentsMargins(0, 0, 0, 0)
        v_box.addWidget(self.des_text)
        v_box.addSpacing(3)
        v_box.addLayout(h_box)
        v_box.addSpacing(3)
        v_box.addWidget(self.list_widget)
        self.setLayout(v_box)

    '''以下为按钮事件(添加/上方插入/删除/全选/执行/保存)'''
    # 展示添加动作子窗口(add_button)
    def connect_add_action_button(self):
        if GloVar.add_action_button_flag is True:
            MotionAction.add_action_flag = True
            GloVar.add_action_window_opened_flag = True
            # 默认是单击动作
            RobotArmAction.uArm_action_type = RobotArmAction.uArm_click
            # 添加动作窗口
            if self.case_absolute_name is not None and self.case_absolute_name != '':
                case_name = os.path.split(self.case_absolute_name)[1].split('.')[0]
            else:
                case_name = '默认(name)'
            self.add_action_window = AddTabWidget(self, case_name=case_name)
            self.add_action_window.signal[str].connect(self.recv_add_action_window_signal)
            self.add_action_window.show()
            self.add_action_window.exec()
        else:
            QMessageBox.about(self, "提示", "请先框选屏幕大小")
            return

    # 插入动作触发函数
    def connect_insert_button(self, insert_position):
        self.insert_item_position = insert_position
        item_num = len(self.item_list)
        insert_index = -1
        if item_num < 1:
            QMessageBox.about(self, "警告", "插入动作位置未知/请选中插入位置")
            return
        else:
            for i in range(item_num):
                if self.custom_control_list[i].check_box.checkState() == Qt.Checked:
                    insert_index = i
                    break
                else:
                    insert_index = -1
        if insert_index == -1:
            QMessageBox.about(self, "警告", "插入动作位置未知/请选中插入位置")
            return
        # 插入标志位
        self.insert_item_index = insert_index
        # 调出动作窗口
        self.connect_add_action_button()

    # 1.筛选出没有被选中的items, 并将他们的info保存到list 2.使用循环创建没有被选中的items
    def delete_selected_items(self):
        # (从后面开始删除)先删除后面的(每次循环递减一个)
        index = len(self.custom_control_list) - 1
        # 通过判断剩余item数量, 来确定是否需要更改‘全选’按键状态
        exist_items_count = index + 1
        # 获取到第一个删除项的下一项info(重写这一项就不会出现文本框选中现象, 不然会出现文本框选中现象)
        get_rewrite_info_flag = False
        # 重写case名字
        rewrite_info = None
        while True:
            if exist_items_count < 1:
                # 全部删除后需要复位全部选中按钮的状态
                self.select_all_flag = False
                self.select_all_button.setToolTip('全部选中')
                self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
                GloVar.actions_saved_to_case = True
                self.case_file_name = ''
                self.case_absolute_name = ''
                break
            # 遍历完item后退出
            elif index < 0:
                break
            # 未遍历完item, 判断是否选中
            else:
                if self.custom_control_list[index].check_box.checkState() == Qt.Checked:
                    if index < (len(self.custom_control_list)-1) and get_rewrite_info_flag is False:
                        get_rewrite_info_flag = True
                        # 获取当前选中项的下一项info
                        rewrite_info = self.info_list[index + 1]
                    # 模拟点击action中的单独delete按钮(稳定)
                    self.custom_control_list[index].delete_button.click()
                    exist_items_count -= 1
            index -= 1
        # 全部删除后需要复位全部选中按钮的状态
        self.select_all_flag = False
        self.select_all_button.setToolTip('全部选中')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
        # 处理出现的选中文本框
        if rewrite_info is not None:
            time.sleep(0.01)
            try:
                current_row = self.info_list.index(rewrite_info)
                if 'action_type' in rewrite_info:
                    text = self.custom_control_list[current_row].des_line_edit.text()
                    self.custom_control_list[current_row].des_line_edit.setText(text)
                elif 'record_status' in rewrite_info:
                    text = self.custom_control_list[current_row].video_type_and_name_text.text()
                    self.custom_control_list[current_row].video_type_and_name_text.setText(text)
                elif 'assert_template' in rewrite_info:
                    text = self.custom_control_list[current_row].template_path_text.text()
                    self.custom_control_list[current_row].template_path_text.setText(text)
                elif 'sleep_time' in rewrite_info:
                    text = self.custom_control_list[current_row].sleep_des_text.text()
                    self.custom_control_list[current_row].sleep_des_text.setText(text)
            except:
                pass

    # 删除工具栏操作(delete_button)
    def connect_delete_selected_items(self):
        # 没有item的时候让button无效
        if self.index < 0:
            pass
        else:
            Thread(target=self.delete_selected_items, args=()).start()

    # 全部选中或者全部不选中items
    def select_or_un_select_all_items(self):
        if self.select_all_flag is False:
            for i in range(self.index + 1):
                self.custom_control_list[i].check_box.setCheckState(Qt.Checked)
            self.select_all_flag = True
            self.select_all_button.setToolTip('全不选中')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_un_select + ')}')
            Logger('[全部选中]-->所有动作')
        else:
            for i in range(self.index + 1):
                self.custom_control_list[i].check_box.setCheckState(Qt.Unchecked)
            self.select_all_flag = False
            self.select_all_button.setToolTip('全部选中')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
            Logger('[全不选中]-->所有动作')

    # 选择/不选择(所有)工具栏操作(select_all_button)
    def connect_select_all_items(self):
        # 没有item的时候让button无效
        if self.index < 0:
            pass
        else:
            Thread(target=self.select_or_un_select_all_items, args=()).start()

    # 执行选中actions的具体操作
    def execute_selected_actions(self):
        if GloVar.request_status is None:
            Logger('[当前还有正在执行的动作, 请稍后执行!]')
            return
        GloVar.post_info_list = []
        GloVar.post_info_list.append('start>actions')
        index = 0
        for i in range(len(self.item_list)):
            if self.custom_control_list[index].check_box.checkState() == Qt.Checked:
                # 判断是action/record/sleep控件
                if MotionAction.points in self.info_list[index]:
                    self.info_list[index]['execute_action'] = 'motion_action'
                    self.info_list[index]['base'] = (RobotArmParam.base_x_point, RobotArmParam.base_y_point, RobotArmParam.base_z_point)
                    GloVar.post_info_list.append(self.info_list[index])
                # 为record或者sleep控件
                else:
                    # 为record控件
                    if RecordAction.record_status in self.info_list[index]:
                        self.info_list[index]['execute_action'] = 'record_action'
                        # 添加视频存放根目录
                        self.info_list[index]['video_path'] = GloVar.project_video_path
                        GloVar.post_info_list.append(self.info_list[index])
                    elif AssertAction.assert_template_name in self.info_list[index]:
                        self.info_list[index]['execute_action'] = 'assert_action'
                        GloVar.post_info_list.append(self.info_list[index])
                    # 为sleep控件
                    elif SleepAction.sleep_time in self.info_list[index]:
                        self.info_list[index]['execute_action'] = 'sleep_action'
                        GloVar.post_info_list.append(self.info_list[index])
            index += 1
        GloVar.post_info_list.append('stop')
        # 将GloVar.post_info_list传递出去
        self.signal.emit('play_actions>')

    # 执行选中的actions(execute_button/单独起线程)
    def connect_execute_selected_actions(self):
        # 每执行一次都需要获取当前时间(作为文件夹)
        GloVar.current_time = time.strftime('%H-%M-%S', time.localtime(time.time()))
        Thread(target=self.execute_selected_actions, args=()).start()

    # 保存标签工具栏操作(save_button)
    def connect_save_script_tag(self):
        script_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='script_path').value
        if len(self.case_absolute_name) > 0:
            xml_file = self.case_absolute_name
        else:
            filename = QFileDialog.getSaveFileName(self, '保存case', script_path, 'script file(*.xml)', options=QFileDialog.DontUseNativeDialog)
            xml_file = filename[0]
            if xml_file:
                if xml_file.endswith('.xml'):
                    xml_file = xml_file
                else:
                    xml_file = xml_file + '.xml'
            else:
                Logger('[取消保存脚本标签!]')
                return
        current_path = '/'.join(xml_file.split('/')[:-1])
        if current_path != script_path:
            Profile(type='write', file=GloVar.config_file_path, section='param', option='script_path', value=current_path)
        with open(xml_file, 'w', encoding='utf-8') as f:
            self.case_absolute_name = xml_file
            self.case_file_name = xml_file.split('/')[-1]
            script_tag = self.merge_to_script(''.join(self.tag_list))
            f.write(script_tag)
            Logger('[保存的脚本标签名为]: %s' % xml_file)
            # 保存case命令
            self.signal.emit('save_case>' + script_tag)
            WindowStatus.action_tab_status = '%s>已保存!' % self.case_absolute_name
            self.des_text.setText(self.case_file_name)
            GloVar.actions_saved_to_case = True

    # 框选模板
    def connect_draw_frame(self):
        # 发出框选模板信号
        self.signal.emit('draw_frame>')

    # 清除所有动作
    def clear_all_items(self):
        self.list_widget.clear()
        self.item_list = []
        self.custom_control_list = []
        self.info_list = []
        self.tag_list = []
        self.index = -1
        # 取消脚本页的脚本
        self.signal.emit('write_script_tag>')
        self.des_text.setText('空白')
        WindowStatus.action_tab_status = '空白!'
        GloVar.actions_saved_to_case = True
        self.case_file_name = ''
        self.case_absolute_name = ''

    # 添加item(action/video/sleep可以共用)
    def add_item(self, item, obj, info_dict, new_control_flag, item_type):
        # item:条目对象/obj:控件对象/info_dict:传入的字典参数/new_control_flag:是否真正的新建控件(而非case导入)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, obj)
        self.item_list.append(item)
        self.custom_control_list.append(obj)
        self.info_list.append(info_dict)
        if item_type == 'action':
            self.tag_list.append(self.generate_action_tag(info_dict))
        elif item_type == 'record':
            self.tag_list.append(self.generate_record_tag(info_dict))
        elif item_type == 'assert':
            self.tag_list.append(self.generate_assert_tag(info_dict))
        elif item_type == 'sleep':
            self.tag_list.append(self.generate_sleep_tag(info_dict))
        # 发送需要显示的脚本标签
        self.signal.emit('write_script_tag>' + self.merge_to_script(''.join(self.tag_list)))
        if new_control_flag is True:
            GloVar.actions_saved_to_case = False
            if self.case_file_name == '':  # 空白新建action
                WindowStatus.action_tab_status = '新case>未保存!'
                self.des_text.setText('空白')
            else:  # case新增action
                WindowStatus.action_tab_status = '%s>有改动!' % self.case_absolute_name
                self.des_text.setText(self.case_file_name)
        else:
            GloVar.actions_saved_to_case = True
        # 滚动条滚动到当前item
        self.list_widget.scrollToItem(item)

    # 插入item(action/video/sleep可以共用)
    def insert_item(self, item, obj, info_dict, item_type):
        # 上方插入
        if self.insert_item_position == self.insert_up_position:
            self.list_widget.insertItem(self.insert_item_index, item)
            self.list_widget.setItemWidget(item, obj)
            self.item_list.insert(self.insert_item_index, item)
            self.custom_control_list.insert(self.insert_item_index, obj)
            self.info_list.insert(self.insert_item_index, info_dict)
            if item_type == 'action':
                self.tag_list.insert(self.insert_item_index, self.generate_action_tag(info_dict))
            elif item_type == 'record':
                self.tag_list.insert(self.insert_item_index, self.generate_record_tag(info_dict))
            elif item_type == 'sleep':
                self.tag_list.insert(self.insert_item_index, self.generate_sleep_tag(info_dict))
            # 重新拍每个custom_control_list的id
            for index in range(self.insert_item_index, self.index + 1):
                self.custom_control_list[index].id = index
        # 下方插入
        elif self.insert_item_position == self.insert_down_position:
            self.list_widget.insertItem(self.insert_item_index + 1, item)
            self.list_widget.setItemWidget(item, obj)
            self.item_list.insert(self.insert_item_index + 1, item)
            self.custom_control_list.insert(self.insert_item_index + 1, obj)
            self.info_list.insert(self.insert_item_index + 1, info_dict)
            if item_type == 'action':
                self.tag_list.insert(self.insert_item_index + 1, self.generate_action_tag(info_dict))
            elif item_type == 'record':
                self.tag_list.insert(self.insert_item_index + 1, self.generate_record_tag(info_dict))
            elif item_type == 'sleep':
                self.tag_list.insert(self.insert_item_index + 1, self.generate_sleep_tag(info_dict))
            # 重新拍每个custom_control_list的id
            for index in range(self.insert_item_index + 1, self.index + 1):
                self.custom_control_list[index].id = index
        # 发送需要显示的脚本标签
        self.signal.emit('write_script_tag>' + self.merge_to_script(''.join(self.tag_list)))
        # 更新状态栏(case以及action信息)
        GloVar.actions_saved_to_case = False
        if self.case_file_name == '':  # 空白新建action
            WindowStatus.action_tab_status = '新case>未保存!'
            self.des_text.setText('空白')
        else:  # case新增action
            WindowStatus.action_tab_status = '%s>有改动!' % self.case_absolute_name
            self.des_text.setText(self.case_file_name)
        # 插入位置复位
        self.insert_item_index = -1
        self.insert_item_position = None
        # 滚动条滚动到当前item
        self.list_widget.scrollToItem(item)

    # 添加action动作控件
    def add_action_item(self, info_dict, new_control_flag=True):
        # 给动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 120))
        obj = ActionControl(parent=None, id=self.index, info_dict=info_dict, new_control_flag=new_control_flag)
        obj.signal[str].connect(self.recv_action_control_signal)
        self.add_item(item, obj, info_dict, new_control_flag, item_type='action')
        if len(self.case_absolute_name) > 0:
            self.connect_save_script_tag()

    # 插入action动作控件
    def insert_action_item(self, info_dict):
        # 给action动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 120))
        obj = ActionControl(parent=None, id=self.index, info_dict=info_dict)
        obj.signal[str].connect(self.recv_action_control_signal)
        self.insert_item(item, obj, info_dict, item_type='action')
        if len(self.case_absolute_name) > 0:
            self.connect_save_script_tag()

    # 添加record动作控件
    def add_record_item(self, info_dict, new_control_flag=True):
        # 给record动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 120))
        obj = RecordControl(parent=None, id=self.index, info_dict=info_dict, new_control_flag=new_control_flag)
        obj.signal[str].connect(self.recv_record_control_signal)
        self.add_item(item, obj, info_dict, new_control_flag, item_type='record')
        if len(self.case_absolute_name) > 0:
            self.connect_save_script_tag()

    # 插入record动作控件
    def insert_record_item(self, info_dict):
        # 给record动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 120))
        obj = RecordControl(parent=None, id=self.index, info_dict=info_dict)
        obj.signal[str].connect(self.recv_record_control_signal)
        self.insert_item(item, obj, info_dict, item_type='record')
        if len(self.case_absolute_name) > 0:
            self.connect_save_script_tag()

    # 添加assert断言动作
    def add_assert_item(self, info_dict, new_control_flag=True):
        # 给record动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 90))
        obj = AssertControl(parent=None, id=self.index, info_dict=info_dict, new_control_flag=new_control_flag)
        obj.signal[str].connect(self.recv_assert_control_signal)
        self.add_item(item, obj, info_dict, new_control_flag, item_type='assert')
        if len(self.case_absolute_name) > 0:
            self.connect_save_script_tag()

    # 插入assert断言动作
    def insert_assert_item(self, info_dict):
        pass

    # 添加sleep动作控件
    def add_sleep_item(self, info_dict, new_control_flag=True):
        # 给sleep动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 60))
        obj = SleepControl(parent=None, id=self.index, info_dict=info_dict, new_control_flag=new_control_flag)
        obj.signal[str].connect(self.recv_sleep_control_signal)
        self.add_item(item, obj, info_dict, new_control_flag, item_type='sleep')
        if len(self.case_absolute_name) > 0:
            self.connect_save_script_tag()

    # 插入sleep动作控件
    def insert_sleep_item(self, info_dict):
        # 给sleep动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 60))
        obj = SleepControl(parent=None, id=self.index, info_dict=info_dict)
        obj.signal[str].connect(self.recv_sleep_control_signal)
        self.insert_item(item, obj, info_dict, item_type='sleep')
        if len(self.case_absolute_name) > 0:
            self.connect_save_script_tag()

    # 接收action控件传来的删除和执行信号
    def recv_action_control_signal(self, signal_str):
        if signal_str.startswith('action_delete_item>'):
            id = int(signal_str.split('action_delete_item>')[1])
            self.delete_item(id)
        elif signal_str.startswith('action_execute_item>'):
            if GloVar.request_status is None:
                Logger('[当前还有正在执行的动作, 请稍后执行!]')
                return
            id = int(signal_str.split('action_execute_item>')[1])
            self.info_list[id]['execute_action'] = 'motion_action'
            self.info_list[id]['base'] = (RobotArmParam.base_x_point, RobotArmParam.base_y_point, RobotArmParam.base_z_point)
            GloVar.post_info_list = []
            GloVar.post_info_list.append('start')
            GloVar.post_info_list.append(self.info_list[id])
            GloVar.post_info_list.append('stop')
            self.signal.emit('play_actions>')

    # 接收record控件传来的删除和执行信号
    def recv_record_control_signal(self, signal_str):
        if signal_str.startswith('record_delete_item>'):
            id = int(signal_str.split('record_delete_item>')[1])
            self.delete_item(id)
        elif signal_str.startswith('record_execute_item>'):
            if GloVar.request_status is None:
                Logger('[当前还有正在执行的动作, 请稍后执行!]')
                return
            id = int(signal_str.split('record_execute_item>')[1])
            self.info_list[id]['execute_action'] = 'record_action'
            # 添加视频存放根目录
            self.info_list[id]['video_path'] = GloVar.project_video_path
            GloVar.post_info_list = []
            GloVar.post_info_list.append('start')
            GloVar.post_info_list.append(self.info_list[id])
            GloVar.post_info_list.append('stop')
            self.signal.emit('play_actions>')

    # 接收assert控件传来的删除和执行信号
    def recv_assert_control_signal(self, signal_str):
        if signal_str.startswith('assert_delete_item>'):
            id = int(signal_str.split('assert_delete_item>')[1])
            # 删除对应的断言模板图
            assert_template_picture = self.info_list[id][AssertAction.assert_template_name]
            if os.path.exists(assert_template_picture):
                os.remove(assert_template_picture)
            self.delete_item(id)
        elif signal_str.startswith('assert_execute_item>'):
            if GloVar.request_status is None:
                Logger('[当前还有正在执行的动作, 请稍后执行!]')
                return
            id = int(signal_str.split('assert_execute_item>')[1])
            self.info_list[id]['execute_action'] = 'assert_action'
            GloVar.post_info_list = []
            GloVar.post_info_list.append('start')
            GloVar.post_info_list.append(self.info_list[id])
            GloVar.post_info_list.append('stop')
            self.signal.emit('play_actions>')

    # 接收sleep控件传来的删除和执行信号
    def recv_sleep_control_signal(self, signal_str):
        if signal_str.startswith('sleep_delete_item>'):
            id = int(signal_str.split('sleep_delete_item>')[1])
            self.delete_item(id)
        elif signal_str.startswith('sleep_execute_item>'):
            if GloVar.request_status is None:
                Logger('[当前还有正在执行的动作, 请稍后执行!]')
                return
            id = int(signal_str.split('sleep_execute_item>')[1])
            self.info_list[id]['execute_action'] = 'sleep_action'
            GloVar.post_info_list = []
            GloVar.post_info_list.append('start')
            GloVar.post_info_list.append(self.info_list[id])
            GloVar.post_info_list.append('stop')
            self.signal.emit('play_actions>')

    # 接收从添加动作子窗口传来的信号
    def recv_add_action_window_signal(self, signal_str):
        # 按下action_tab页面确定按钮后, 添加控件
        if signal_str.startswith('action_tab_sure>'):
            info_dict = json.loads(signal_str.split('action_tab_sure>')[1])
            if self.insert_item_index == -1:
                self.add_action_item(info_dict)
            else:
                self.insert_action_item(info_dict)
            # 判断是否需要执行当前action
            if GloVar.robot_follow_action_flag is True:
                info_dict['execute_action'] = 'motion_action'
                info_dict['base'] = (RobotArmParam.base_x_point, RobotArmParam.base_y_point, RobotArmParam.base_z_point)
                GloVar.post_info_list = []
                GloVar.post_info_list.append('start')
                GloVar.post_info_list.append(info_dict)
                GloVar.post_info_list.append('stop')
                self.signal.emit('play_actions>')
        # 按下video_tab页面确认按钮
        elif signal_str.startswith('record_tab_sure>'):
            info_dict = json.loads(signal_str.split('record_tab_sure>')[1])
            if self.insert_item_index == -1:
                self.add_record_item(info_dict)
            else:
                self.insert_record_item(info_dict)
        # 按下assert_tab页面确认按钮
        elif signal_str.startswith('assert_tab_sure>'):
            info_dict = json.loads(signal_str.split('assert_tab_sure>')[1])
            if self.insert_item_index == -1:
                self.add_assert_item(info_dict)
            else:
                self.insert_assert_item(info_dict)
        # 按下sleep_tab页面确认按钮
        elif signal_str.startswith('sleep_tab_sure>'):
            info_dict = json.loads(signal_str.split('sleep_tab_sure>')[1])
            if self.insert_item_index == -1:
                self.add_sleep_item(info_dict)
            else:
                self.insert_sleep_item(info_dict)
        # 接收到框选模板信号
        elif signal_str.startswith(GloVar.result_template):
            self.signal.emit(signal_str)
        # 接收到断言模板
        elif signal_str.startswith(GloVar.assert_template):
            self.signal.emit(signal_str)
        # 切换动作信号(点击/双击/长按/滑动)
        elif signal_str.startswith('action_tab_action>'):
            self.signal.emit(signal_str)
        else:
            pass

    # 删除item
    def delete_item(self, id):
        self.list_widget.takeItem(id)
        self.item_list.pop(id)
        self.custom_control_list.pop(id)
        self.info_list.pop(id)
        self.tag_list.pop(id)
        for i in range(id, self.index):
            self.custom_control_list[i].id = i
        self.index -= 1
        # 自动保存
        self.connect_save_script_tag()
        # 发送需要显示的脚本标签
        if len(self.tag_list) > 0:
            GloVar.actions_saved_to_case = False
            self.signal.emit('write_script_tag>' + self.merge_to_script(''.join(self.tag_list)))
        else:
            self.signal.emit('write_script_tag>')
            self.case_file_name = ''
            self.case_absolute_name = ''
            GloVar.actions_saved_to_case = True
        if self.case_file_name == '':  # 空白新建action
            WindowStatus.action_tab_status = '空白!'
            self.des_text.setText('空白')
        else:  # case新增action
            WindowStatus.action_tab_status = '%s>有改动!' % self.case_absolute_name
            self.des_text.setText(self.case_file_name)

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    # 添加action动作时生成标签
    def generate_action_tag(self, info_dict):
        des_text = info_dict[MotionAction.des_text]
        action_type = info_dict[MotionAction.action_type]
        speed = str(info_dict[MotionAction.speed])
        leave = str(info_dict[MotionAction.leave])
        trigger = str(info_dict[MotionAction.trigger])
        points = str(tuple(info_dict[MotionAction.points]))
        tag = '\t<action '+MotionAction.des_text+'="' + des_text + '">\n'+\
              '\t\t' + '<param name="'+MotionAction.action_type+'">' +action_type+ '</param>\n'+\
              '\t\t' + '<param name="'+MotionAction.points+'">' +points+ '</param>\n'+\
              '\t\t' + '<param name="'+MotionAction.speed+'">' +speed+ '</param>\n'+\
              '\t\t' + '<param name="'+MotionAction.leave+'">' +leave+ '</param>\n'+\
              '\t\t' + '<param name="'+MotionAction.trigger+'">' +trigger+ '</param>\n'+\
              '\t</action>\n'
        return tag

    # 添加video动作时生成标签
    def generate_record_tag(self, info_dict):
        record_status = info_dict[RecordAction.record_status]
        video_type = info_dict[RecordAction.video_type]
        video_name = info_dict[RecordAction.video_name]
        standard_time = info_dict[RecordAction.standard_time]
        tag = '\t<action ' + 'camera_video' + '="' + 'record' + '">\n' + \
              '\t\t' + '<param name="' + RecordAction.record_status + '">' + record_status + '</param>\n' + \
              '\t\t' + '<param name="' + RecordAction.video_type + '">' + video_type + '</param>\n' + \
              '\t\t' + '<param name="' + RecordAction.video_name + '">' + video_name + '</param>\n' + \
              '\t\t' + '<param name="' + RecordAction.standard_time + '">' + standard_time + '</param>\n' + \
              '\t</action>\n'
        return tag

    # 添加assert动作生成标签
    def generate_assert_tag(self, info_dict):
        assert_template_path = str(info_dict[AssertAction.assert_template_name])
        tag = '\t<action ' + 'assert_template' + '="' + 'picture' + '">\n' + \
              '\t\t' + '<param name="' + AssertAction.assert_template_name + '">' + assert_template_path + '</param>\n' + \
              '\t</action>\n'
        return tag

    # 添加sleep动作时生成标签
    def generate_sleep_tag(self, info_dict):
        sleep_time = str(info_dict[SleepAction.sleep_time])
        tag = '\t<action ' + 'sleep' + '="' + 'time/s' + '">\n' + \
              '\t\t' + '<param name="' + SleepAction.sleep_time + '">' + sleep_time + '</param>\n' + \
              '\t</action>\n'
        return tag

    # 将所有action合并成为script
    def merge_to_script(self, tag_string):
        script_start = '<case name="'+self.case_file_name+'">\n'
        script_end = '</case>'
        return script_start + tag_string + script_end
