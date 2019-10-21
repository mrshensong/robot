import json
import time
from threading import Thread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QToolButton, QListWidget, QMessageBox, QFileDialog, QListWidgetItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import IconPath, MotionAction, RobotArmAction, RecordAction, SleepAction, Logger, GloVar, RobotOther, WindowStatus, Profile
from uiclass.controls import ActionControl, RecordControl, SleepControl
from uiclass.add_tab_widget import AddTabWidget
from uiclass.list_widget import ListWidget

class ShowActionTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ShowActionTab, self).__init__(parent)
        self.parent = parent
        self.index = -1
        # 自定义控件列表
        self.custom_control_list = []
        # item列表
        self.item_list = []
        # 控件中的描述/坐标/动作类型等信息(元素为dict类型)
        self.info_list = []
        # 脚本标签
        self.tag_list = []
        # 添加动作窗口
        self.add_action_window = AddTabWidget(self)
        self.add_action_window.signal[str].connect(self.recv_add_action_window_signal)
        # 是否全部选中状态(False:没有全部选中, True:全部选中)
        self.select_all_flag = False
        # 当前所有action需要保存的文件名(或者打开case时现实的case文件名)
        self.case_file_name = ''
        self.case_absolute_name = ''
        """
        1.用来解决在一个list_widget中出现多次视频的问题(视频名后以序号区分)
        2.需要保存record_start的视频类型和名字(最近的record_stop需要共用同一个类型和名字)
        """
        # 用来计算当前list_widget中出现的视频次数编号-从零开始(根据序号来命名)
        self.video_numbers = -1
        # 当前action的视频类型
        self.current_video_type = 'test'
        # 当前action的视频名字
        self.current_video_name = 'test.mp4'
        # tab初始化
        self.action_tab_init()


    def action_tab_init(self):
        self.add_button = QToolButton()
        self.add_button.setToolTip('add')
        self.add_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_add + ')}')
        self.add_button.clicked.connect(self.connect_add_action_button)
        self.delete_button = QToolButton()
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_delete + ')}')
        self.delete_button.clicked.connect(self.connect_delete_selected_items)
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('select_all')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
        self.select_all_button.clicked.connect(self.connect_select_all_items)
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('execute')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_execute + ')}')
        self.execute_button.clicked.connect(self.connect_execute_selected_actions)
        self.save_script_tag_button = QToolButton()
        self.save_script_tag_button.setToolTip('save_tag')
        self.save_script_tag_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_save + ')}')
        self.save_script_tag_button.clicked.connect(self.connect_save_script_tag)

        h_box = QHBoxLayout()
        h_box.addWidget(self.add_button)
        h_box.addWidget(self.delete_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addWidget(self.save_script_tag_button)
        h_box.addStretch(1)
        # 原生QListWidget
        self.list_widget = QListWidget()
        # 自定义QListWidget & 接收位置交换信号
        # self.list_widget = ListWidget(None)
        # self.list_widget.signal[str].connect(self.item_position_exchange)
        # self.list_widget.setMovement(QListWidget.Free)
        # self.list_widget.setDragEnabled(True)
        # 将滚动条变细
        self.list_widget.verticalScrollBar().setStyleSheet("QScrollBar{width:10px;}")
        self.list_widget.horizontalScrollBar().setStyleSheet("QScrollBar{height:10px;}")
        # # 取消横向滚动条
        # self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # # 取消竖向滚动条
        # self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        v_box = QVBoxLayout()
        v_box.addLayout(h_box)
        v_box.addWidget(self.list_widget)
        self.setLayout(v_box)


    '''以下为五个按钮事件(添加/删除/全选/执行/保存)'''
    # 展示添加动作子窗口(add_button)
    def connect_add_action_button(self):
        if GloVar.add_action_button_flag is True:
            MotionAction.add_action_flag = True
            # 默认是单击动作
            RobotArmAction.uArm_action_type = RobotArmAction.uArm_click
            self.add_action_window.show()
            self.add_action_window.exec()
        else:
            QMessageBox.about(self, "提示", "请先框选屏幕大小")
            return


    # 1.筛选出没有被选中的items, 并将他们的info保存到list 2.使用循环创建没有被选中的items
    def delete_selected_items(self):
        index = 0
        while True:
            if len(self.custom_control_list) < index + 1:
                # 全部删除后需要复位全部选中按钮的状态
                self.select_all_flag = False
                self.select_all_button.setToolTip('select_all')
                self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_select + ')}')
                RobotOther.actions_saved_to_case = True
                self.case_file_name = ''
                self.case_absolute_name = ''
                break
            else:
                if self.custom_control_list[index].check_box.checkState() == Qt.Checked:
                    # 模拟点击action中的单独delete按钮
                    self.custom_control_list[index].delete_button.click()
                    time.sleep(0.03)
                else:
                    index += 1


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
            self.select_all_button.setToolTip('un_select_all')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_tab_widget_all_un_select + ')}')
            Logger('[全部选中]-->所有动作')
        else:
            for i in range(self.index + 1):
                self.custom_control_list[i].check_box.setCheckState(Qt.Unchecked)
            self.select_all_flag = False
            self.select_all_button.setToolTip('select_all')
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
        index = 0
        for i in range(len(self.item_list)):
            if self.custom_control_list[index].check_box.checkState() == Qt.Checked:
                # 判断是action/record/sleep控件
                if MotionAction.points in self.info_list[index]:
                    self.custom_control_list[index].play_action_item()
                # 为record或者sleep控件
                else:
                    # 为record控件
                    if RecordAction.record_status in self.info_list[index]:
                        self.custom_control_list[index].play_record_item()
                    # 为sleep控件
                    elif SleepAction.sleep_time in self.info_list[index]:
                        self.custom_control_list[index].play_sleep_item()
                time.sleep(0.02)
            index += 1


    # 执行选中的actions(execute_button/单独起线程)
    def connect_execute_selected_actions(self):
        Thread(target=self.execute_selected_actions, args=()).start()


    # 保存标签工具栏操作(save_button)
    def save_script_tag(self):
        if len(self.list_widget) > 0:
            script_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='script_path').path
            filename = QFileDialog.getSaveFileName(self, 'save script', script_path, 'script file(*.xml)')
            if filename[0]:
                current_path = '/'.join(filename[0].split('/')[:-1])
                if current_path != script_path:
                    Profile(type='write', file=GloVar.config_file_path, section='param', option='script_path', value=current_path)
                with open(filename[0], 'w', encoding='utf-8') as f:
                    self.case_absolute_name = filename[0]
                    self.case_file_name = filename[0].split('/')[-1]
                    script_tag = self.merge_to_script(''.join(self.tag_list))
                    f.write(script_tag)
                    Logger('[保存的脚本标签名为]: %s' % filename[0])
                    self.signal.emit('save_script_tag>' + script_tag)
                    RobotOther.actions_saved_to_case = True
            else:
                Logger('[取消保存脚本标签!]')
        else:
            Logger('[没有要保存的脚本标签!]')


    # 另起线程(保证主线程不受到破坏)
    def connect_save_script_tag(self):
        Thread(target=self.save_script_tag, args=()).start()


    # 清除所有动作
    def clear_all_items(self):
        self.list_widget.clear()
        self.item_list = []
        self.custom_control_list = []
        self.info_list = []
        self.tag_list = []
        self.index = -1
        # 取消脚本页的脚本
        self.signal.emit('save_script_tag>')
        RobotOther.actions_saved_to_case = True
        self.case_file_name = ''
        self.case_absolute_name = ''


    # 添加item(action/video/sleep可以共用)
    def add_item(self, item, obj, info_dict, flag, item_type):
        # item:条目对象/obj:控件对象/info_dict:传入的字典参数/flag:是否真正的新建控件(而非case导入)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, obj)
        self.item_list.append(item)
        self.custom_control_list.append(obj)
        self.info_list.append(info_dict)
        if item_type == 'action':
            self.tag_list.append(self.generate_action_tag(info_dict))
        elif item_type == 'record':
            self.tag_list.append(self.generate_record_tag(info_dict))
        elif item_type == 'sleep':
            self.tag_list.append(self.generate_sleep_tag(info_dict))
        # 发送需要显示的脚本标签
        self.signal.emit('save_script_tag>' + self.merge_to_script(''.join(self.tag_list)))
        if flag is True:
            RobotOther.actions_saved_to_case = False
            if self.case_file_name == '':  # 空白新建action
                WindowStatus.action_tab_status = '新建case-->>未保存!'
            else:  # case新增action
                WindowStatus.action_tab_status = '%s有改动-->>未保存!' % self.case_absolute_name
        else:
            RobotOther.actions_saved_to_case = True
        # 滚动条滚动到当前item
        self.list_widget.scrollToItem(item)


    # 添加action动作控件
    def add_action_item(self, info_dict, flag=True):
        # 给动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 120))
        obj = ActionControl(parent=None, id=self.index, info_dict=info_dict, flag=flag)
        obj.signal[str].connect(self.recv_action_control_signal)
        self.add_item(item, obj, info_dict, flag, item_type='action')


    # 添加video动作控件
    def add_record_item(self, info_dict, flag=True):
        # 只有record_start的时候才证明新增record动作
        if info_dict[RecordAction.record_status] == RecordAction.record_start:
            self.current_video_type = info_dict[RecordAction.video_type]
            self.current_video_name = info_dict[RecordAction.video_name]
        # 重置视频type和name
        info_dict[RecordAction.video_type] = self.current_video_type
        info_dict[RecordAction.video_name] = self.current_video_name
        # 给video动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 120))
        obj = RecordControl(parent=None, id=self.index, info_dict=info_dict, flag=flag)
        obj.signal[str].connect(self.recv_record_control_signal)
        self.add_item(item, obj, info_dict, flag, item_type='record')


    # 添加sleep动作控件
    def add_sleep_item(self, info_dict, flag=True):
        # 给video动作设置id
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 60))
        obj = SleepControl(parent=None, id=self.index, info_dict=info_dict, flag=flag)
        obj.signal[str].connect(self.recv_sleep_control_signal)
        self.add_item(item, obj, info_dict, flag, item_type='sleep')


    # 接收action控件传来的删除和执行信号
    def recv_action_control_signal(self, signal_str):
        if signal_str.startswith('action_delete_item>'):
            id = int(signal_str.split('action_delete_item>')[1])
            self.delete_item(id)
        elif signal_str.startswith('action_execute_item>'):
            id = int(signal_str.split('action_execute_item>')[1])
            self.signal.emit('action_execute_item>'+json.dumps(self.info_list[id]))


    # 接收record控件传来的删除和执行信号
    def recv_record_control_signal(self, signal_str):
        if signal_str.startswith('record_delete_item>'):
            id = int(signal_str.split('record_delete_item>')[1])
            self.delete_item(id)
        elif signal_str.startswith('record_execute_item>'):
            id = int(signal_str.split('record_execute_item>')[1])
            self.signal.emit('record_execute_item>' + json.dumps(self.info_list[id]))


    # 接收sleep控件传来的删除和执行信号
    def recv_sleep_control_signal(self, signal_str):
        if signal_str.startswith('sleep_delete_item>'):
            id = int(signal_str.split('sleep_delete_item>')[1])
            self.delete_item(id)
        elif signal_str.startswith('sleep_execute_item>'):
            id = int(signal_str.split('sleep_execute_item>')[1])
            self.signal.emit('sleep_execute_item>' + json.dumps(self.info_list[id]))



    # 接收从添加动作子窗口传来的信号
    def recv_add_action_window_signal(self, signal_str):
        # 按下action_tab页面确定按钮后, 添加控件
        if signal_str.startswith('action_tab_sure>'):
            info_dict = json.loads(signal_str.split('action_tab_sure>')[1])
            self.add_action_item(info_dict)
        # 按下video_tab页面确认按钮
        elif signal_str.startswith('record_tab_sure>'):
            info_dict = json.loads(signal_str.split('record_tab_sure>')[1])
            self.add_record_item(info_dict)
        # 按下sleep_tab页面确认按钮
        elif signal_str.startswith('sleep_tab_sure>'):
            info_dict = json.loads(signal_str.split('sleep_tab_sure>')[1])
            self.add_sleep_item(info_dict)
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
        # 发送需要显示的脚本标签
        if len(self.tag_list) > 0:
            RobotOther.actions_saved_to_case = False
            self.signal.emit('save_script_tag>' + self.merge_to_script(''.join(self.tag_list)))
        else:
            self.signal.emit('save_script_tag>')
            RobotOther.actions_saved_to_case = True
        if self.case_file_name == '':  # 空白新建action
            WindowStatus.action_tab_status = '新建case-->>未保存!'
        else:  # case新增action
            WindowStatus.action_tab_status = '%s有改动-->>未保存!' % self.case_absolute_name


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
        points =   str(tuple(info_dict[MotionAction.points]))
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
        video_type    = info_dict[RecordAction.video_type]
        video_name    = info_dict[RecordAction.video_name]
        tag = '\t<action ' + 'camera_video' + '="' + 'record' + '">\n' + \
              '\t\t' + '<param name="' + RecordAction.record_status + '">' + record_status + '</param>\n' + \
              '\t\t' + '<param name="' + RecordAction.video_type + '">' + video_type + '</param>\n' + \
              '\t\t' + '<param name="' + RecordAction.video_name + '">' + video_name + '</param>\n' + \
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
        script_end   = '</case>'
        return script_start + tag_string + script_end