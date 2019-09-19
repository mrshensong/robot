import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import icon_path, add_action_window, uArm_action, logger
from uiclass.custom_control import Custom_Control, Add_Action_Control

class Custom_TabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, tab1='action', tab2='edit'):
        super(Custom_TabWidget, self).__init__(parent)
        self.parent = parent
        self.setTabPosition(self.South)

        self.index = -1
        self.tab1 = QWidget()  # 1
        self.tab2 = QTextEdit()
        self.tab1_init()  # 2
        # self.tab2_init()
        self.addTab(self.tab1, tab1)
        self.addTab(self.tab2, tab2)
        # 自定义控件列表
        self.custom_control_list = []
        # item列表
        self.item_list = []
        # 控件中的描述/坐标/动作类型等信息(元素为dict类型)
        self.info_list = []
        # 添加动作窗口
        self.add_action_window = Add_Action_Control(self)
        self.add_action_window.signal[str].connect(self.recv_add_action_window_signal)


    def tab1_init(self):
        self.add_button = QToolButton()
        self.add_button.setToolTip('add')
        self.add_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_add + ')}')
        # self.add_button.clicked.connect(self.add_item)
        self.add_button.clicked.connect(self.open_child_window)
        self.delete_button = QToolButton()
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_delete + ')}')
        self.delete_button.clicked.connect(self.clear)
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('select_all')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_select + ')}')
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('execute')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_execute + ')}')
        h_box = QHBoxLayout()
        h_box.addWidget(self.add_button)
        h_box.addWidget(self.delete_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addStretch(1)

        self.list_widget = QListWidget(self.tab1)
        v_box = QVBoxLayout()
        v_box.addLayout(h_box)
        v_box.addWidget(self.list_widget)
        self.tab1.setLayout(v_box)


    # 展示添加动作子窗口
    def open_child_window(self):
        add_action_window.add_action_flag = True
        uArm_action.uArm_action_type = uArm_action.uArm_click
        self.add_action_window.show()
        self.add_action_window.exec()


    # 添加动作控件
    def add_item(self, info_dict):
        # 给动作设置id
        self.index += 1
        # 通过字典中的坐标信息, 来设置需要在控件中显示的坐标信息(字符串类型)
        # 先将坐标元素转为字符串类型
        points = info_dict[add_action_window.points]
        points = [str(x) for x in points]
        if len(info_dict[add_action_window.points]) == 2:
            points_text = ','.join(points)
        elif len(info_dict[add_action_window.points]) == 4:
            points_text = ','.join(points[:2]) +';' +','.join(points[2:])
        else: # 无实际意义(单纯为了不让代码出现警告)
            points_text = '0.0,0.0'
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 80))
        obj = Custom_Control(parent=None, id=self.index, type=info_dict[add_action_window.action])
        obj.id = self.index
        obj.des_line_edit.setText(info_dict[add_action_window.des_text])
        obj.points_line_edit.setText(points_text)
        obj.play_botton.clicked.connect(lambda : self.play_item(obj.id))
        obj.delete_botton.clicked.connect(lambda : self.delete_item(obj.id))
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, obj)
        # print('the totle item is : ', self.list_widget.count())
        self.item_list.append(obj)
        self.custom_control_list.append(obj)
        self.info_list.append(info_dict)
        # 打印新建动作信息
        if info_dict[add_action_window.des_text] == '':
            logger('新建-->id[%d]--动作[%s]-->: 无描述信息' %(obj.id, info_dict[add_action_window.action]))
        else:
            logger('新建-->id[%d]--动作[%s]-->: %s' %(obj.id, info_dict[add_action_window.action], info_dict[add_action_window.des_text]))


    # 播放动作
    def play_item(self, id):
        # print(self.info_list[id][add_action_window.des_text])
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit(json.dumps(self.info_list[id]))


    # 删除动作
    def delete_item(self, id):
        # 打印删除信息
        if self.info_list[id][add_action_window.des_text] == '':
            logger('删除-->id[%d]--动作[%s]-->: 无描述信息' %(id, self.info_list[id][add_action_window.action]))
        else:
            logger('删除-->id[%d]--动作[%s]-->: %s' %(id, self.info_list[id][add_action_window.action], self.info_list[id][add_action_window.des_text]))
        self.list_widget.takeItem(id)
        self.item_list.pop(id)
        self.custom_control_list.pop(id)
        self.info_list.pop(id)
        for i in range(id, self.index):
            self.custom_control_list[i].id = i
        self.index -= 1


    # 清除所有动作
    def clear(self):
        self.list_widget.clear()
        self.item_list = []
        self.custom_control_list = []
        self.index = -1


    # 接收从添加动作子窗口传来的信号
    def recv_add_action_window_signal(self, signal_str):
        # 确定按钮
        if signal_str.split('>')[0] == 'sure':
            info_dict = json.loads(signal_str.split('>')[1])
            self.add_item(info_dict)
        else:
            pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Custom_TabWidget(None)
    demo.show()
    sys.exit(app.exec_())