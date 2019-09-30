import os
import json
import time
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import icon_path, add_action_window, uArm_action, logger, gloVar, robot_other, window_status, profile
from uiclass.controls import Action_Control, Add_Action_Control

class Action_Tab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(Action_Tab, self).__init__(parent)
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
        self.add_action_window = Add_Action_Control(self)
        self.add_action_window.signal[str].connect(self.recv_add_action_window_signal)
        # 是否全部选中状态(False:没有全部选中, True:全部选中)
        self.select_all_flag = False
        # 当前所有action需要保存的文件名(或者打开case时现实的case文件名)
        self.case_file_name = ''
        self.case_absolute_name = ''
        # tab初始化
        self.action_tab_init()


    def action_tab_init(self):
        self.add_button = QToolButton()
        self.add_button.setToolTip('add')
        self.add_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_add + ')}')
        self.add_button.clicked.connect(self.connect_add_action_button)
        self.delete_button = QToolButton()
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_delete + ')}')
        self.delete_button.clicked.connect(self.connect_delete_selected_items)
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('select_all')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_select + ')}')
        self.select_all_button.clicked.connect(self.connect_select_all_items)
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('execute')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_execute + ')}')
        self.execute_button.clicked.connect(self.connect_execute_selected_actions)
        self.save_script_tag_button = QToolButton()
        self.save_script_tag_button.setToolTip('save_tag')
        self.save_script_tag_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_save + ')}')
        self.save_script_tag_button.clicked.connect(self.connect_save_script_tag)

        h_box = QHBoxLayout()
        h_box.addWidget(self.add_button)
        h_box.addWidget(self.delete_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addWidget(self.save_script_tag_button)
        h_box.addStretch(1)
        # self.list_widget = QListWidget(self.tab1)
        self.list_widget = QListWidget()
        v_box = QVBoxLayout()
        v_box.addLayout(h_box)
        v_box.addWidget(self.list_widget)
        self.setLayout(v_box)
        # self.tab1.setLayout(v_box)


    # 展示添加动作子窗口(add_button)
    def connect_add_action_button(self):
        if gloVar.add_action_button_flag is True:
            add_action_window.add_action_flag = True
            # 默认是单击动作
            uArm_action.uArm_action_type = uArm_action.uArm_click
            self.add_action_window.show()
            self.add_action_window.exec()
        else:
            QMessageBox.about(self, "提示", "请先框选屏幕大小")
            return


    # 删除工具栏操作(delete_button)
    def connect_delete_selected_items(self):
        # 没有item的时候让button无效
        if self.index < 0:
            pass
        else:
            Thread(target=self.delete_selected_items, args=()).start()


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
        for i in range(len(self.list_widget)):
            if self.custom_control_list[index].check_box.checkState() == Qt.Checked:
                # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
                self.play_action(index)
                time.sleep(0.03)
            index += 1


    # 执行选中的actions(execute_button/单独起线程)
    def connect_execute_selected_actions(self):
        Thread(target=self.execute_selected_actions, args=()).start()


    # 保存标签工具栏操作(save_button)
    def connect_save_script_tag(self):
        if len(self.list_widget) > 0:
            script_path = profile(type='read', file=gloVar.config_file_path, section='param', option='script_path').path
            filename = QFileDialog.getSaveFileName(self, 'save script', script_path, 'script file(*.xml)')
            if filename[0]:
                current_path = '/'.join(filename[0].split('/')[:-1])
                if current_path != script_path:
                    profile(type='write', file=gloVar.config_file_path, section='param', option='script_path', value=current_path)
                with open(filename[0], 'w', encoding='utf-8') as f:
                    self.case_absolute_name = filename[0]
                    self.case_file_name = filename[0].split('/')[-1]
                    script_tag = self.merge_to_script(''.join(self.tag_list))
                    f.write(script_tag)
                    logger('[保存的脚本标签名为]: %s' %filename[0])
                    self.signal.emit('save_script_tag>' + script_tag)
                    robot_other.actions_saved_to_case = True
            else:
                logger('[取消保存脚本标签!]')
        else:
            logger('[没有要保存的脚本标签!]')


    # 执行单个动作的具体操作
    def play_action(self, id):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        while True:
            if gloVar.request_status == 'ok':
                gloVar.request_status = None
                self.signal.emit('execute>'+json.dumps(self.info_list[id]))
                break
            else:
                # 降低cpu负债率
                time.sleep(0.02)


    # 执行单个动作(新建线程/控件中的执行按钮)
    def execute_action(self, id):
        Thread(target=self.play_action, args=(id,)).start()


    # 删除单个动作(控件中的删除按钮)
    def delete_item(self, id):
        # 打印删除信息
        if self.info_list[id][add_action_window.des_text] == '':
            logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: 无描述信息'.format(self.str_decorate(id),
                                                                            self.str_decorate(self.info_list[id][add_action_window.action_type]),
                                                                            str(self.info_list[id][add_action_window.points])))
        else:
            logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: {}'.format(self.str_decorate(id),
                                                                      self.str_decorate(self.info_list[id][add_action_window.action_type]),
                                                                      str(self.info_list[id][add_action_window.points]),
                                                                      self.info_list[id][add_action_window.des_text]))
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
            robot_other.actions_saved_to_case = False
            self.signal.emit('script_tag>' + self.merge_to_script(''.join(self.tag_list)))
        else:
            self.signal.emit('script_tag>')
            robot_other.actions_saved_to_case = True
        if self.case_file_name == '':  # 空白新建action
            window_status.action_tab_status = '新建case-->>未保存!'
        else:  # case新增action
            window_status.action_tab_status = '%s有改动-->>未保存!'%self.case_absolute_name


    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)


    # 清除所有动作
    def clear_all_items(self):
        self.list_widget.clear()
        self.item_list = []
        self.custom_control_list = []
        self.info_list = []
        self.tag_list = []
        self.index = -1
        # 取消脚本页的脚本
        self.signal.emit('script_tag>')
        robot_other.actions_saved_to_case = True
        self.case_file_name = ''
        self.case_absolute_name = ''


    # 1.筛选出没有被选中的items, 并将他们的info保存到list 2.使用循环创建没有被选中的items
    def delete_selected_items(self):
        index = 0
        while True:
            if len(self.custom_control_list) < index+1:
                # 全部删除后需要复位全部选中按钮的状态
                self.select_all_flag = False
                self.select_all_button.setToolTip('select_all')
                self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_select + ')}')
                robot_other.actions_saved_to_case = True
                self.case_file_name = ''
                self.case_absolute_name = ''
                break
            else:
                if self.custom_control_list[index].check_box.checkState() == Qt.Checked:
                    # 模拟点击action中的单独delete按钮
                    self.custom_control_list[index].delete_botton.click()
                    time.sleep(0.03)
                else:
                    index += 1


    # 全部选中或者全部不选中items
    def select_or_un_select_all_items(self):
        if self.select_all_flag is False:
            for i in range(self.index + 1):
                self.custom_control_list[i].check_box.setCheckState(Qt.Checked)
            self.select_all_flag = True
            self.select_all_button.setToolTip('un_select_all')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_un_select + ')}')
            logger('[全部选中]-->所有动作')
        else:
            for i in range(self.index + 1):
                self.custom_control_list[i].check_box.setCheckState(Qt.Unchecked)
            self.select_all_flag = False
            self.select_all_button.setToolTip('select_all')
            self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_select + ')}')
            logger('[全不选中]-->所有动作')


    # 添加动作控件
    def add_item(self, info_dict, flag=True):
        # 给动作设置id
        self.index += 1
        # 通过字典中的坐标信息, 来设置需要在控件中显示的坐标信息(字符串类型)
        # 先将坐标元素转为字符串类型
        points = info_dict[add_action_window.points]
        if points:
            points_text = str(tuple(points))
        else: # 无实际意义(单纯为了不让代码出现警告)
            points_text = '(0.0, 0.0)'
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 80))
        obj = Action_Control(parent=None, id=self.index, type=info_dict[add_action_window.action_type])
        obj.id = self.index
        obj.des_line_edit.setText(info_dict[add_action_window.des_text])
        obj.points_line_edit.setText(points_text)
        obj.play_botton.clicked.connect(lambda : self.execute_action(obj.id))
        obj.delete_botton.clicked.connect(lambda : self.delete_item(obj.id))
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, obj)
        self.item_list.append(obj)
        self.custom_control_list.append(obj)
        self.info_list.append(info_dict)
        self.tag_list.append(self.generate_tag(info_dict))
        # 发送需要显示的脚本标签
        self.signal.emit('save_script_tag>' + self.merge_to_script(''.join(self.tag_list)))
        # 如果确实是添加动作(而非导入case中的动作)
        if flag is True:
            robot_other.actions_saved_to_case = False
            if self.case_file_name == '': # 空白新建action
                window_status.action_tab_status = '新建case-->>未保存!'
            else: # case新增action
                window_status.action_tab_status = '%s有改动-->>未保存!'%self.case_absolute_name
            # 打印新建动作信息
            if info_dict[add_action_window.des_text] == '':
                logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: 无描述信息'.format(self.str_decorate(obj.id),
                                                                                self.str_decorate(info_dict[add_action_window.action_type]),
                                                                                points_text))
            else:
                logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: {}'.format(self.str_decorate(obj.id),
                                                                             self.str_decorate(info_dict[add_action_window.action_type]),
                                                                             points_text,
                                                                             info_dict[add_action_window.des_text]))
        else: # 通过case文件打开actions
            robot_other.actions_saved_to_case = True


    # 接收从添加动作子窗口传来的信号
    def recv_add_action_window_signal(self, signal_str):
        # 按下确定按钮后, 添加控件
        if signal_str.startswith('sure>'):
            info_dict = json.loads(signal_str.split('>')[1])
            self.add_item(info_dict)
        elif signal_str.startswith('action>'):
            self.signal.emit(signal_str)
        else:
            pass


    # 添加动作时生成标签
    def generate_tag(self, info_dict):
        des_text = info_dict[add_action_window.des_text]
        action_type =   info_dict[add_action_window.action_type]
        points =   str(tuple(info_dict[add_action_window.points]))
        tag = '\t<action '+add_action_window.des_text+'="' + des_text + '">\n'+\
              '\t\t' + '<param name="'+add_action_window.action_type+'">' +action_type+ '</param>\n'+\
              '\t\t' + '<param name="'+add_action_window.points+'">' +points+ '</param>\n'+\
              '\t</action>\n'
        return tag


    # 将所有action合并成为script
    def merge_to_script(self, tag_string):
        script_start = '<case name="'+self.case_file_name+'">\n'
        script_end   = '</case>'
        return script_start + tag_string + script_end