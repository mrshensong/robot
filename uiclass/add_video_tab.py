import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import icon_path, uArm_action, add_action_window, video_action

# 动作添加控件
class AddVideoTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddVideoTab, self).__init__(parent)
        self.parent = parent
        self.info_dict = {add_action_window.des_text    : None,
                          add_action_window.action_type : uArm_action.uArm_click,
                          add_action_window.speed       : 150,
                          add_action_window.points      : None,
                          add_action_window.leave       : 1}
        self.initUI()


    # 初始化
    def initUI(self):
        self.general_layout = QVBoxLayout()
        #创建一个表单布局
        self.from_layout = QFormLayout()
        self.button_layout = QHBoxLayout()
        #设置标签右对齐, 不设置是默认左对齐
        self.from_layout.setLabelAlignment(Qt.AlignCenter)
        # 设置表单内容
        # 是否开始录制视频
        self.start_record_video = QCheckBox(self)
        self.start_record_video.setCheckState(Qt.Unchecked)
        # 是否停止录制视频
        self.stop_record_video = QCheckBox(self)
        self.stop_record_video.setCheckState(Qt.Unchecked)
        # 表单布局
        self.from_layout.addRow('开始录制视频: ', self.start_record_video)
        self.from_layout.addRow('停止录制视频: ', self.stop_record_video)

        # 确定按钮
        self.sure_button = QPushButton('确定', self)
        self.sure_button.clicked.connect(self.connect_sure)
        # 确定button横向布局(处于中间)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.sure_button)
        self.button_layout.addStretch(1)

        self.general_layout.addLayout(self.from_layout)
        self.general_layout.addLayout(self.button_layout)

        self.setLayout(self.general_layout)
        # 设置字体
        QFontDialog.setFont(self, QFont('Times New Roman', 11))
        # 设置最小尺寸
        self.setMinimumWidth(300)


    def connect_com_box(self):
        pass
        # self.signal.emit('action>'+self.com_box.currentText())


    def connect_get_points(self):
        pass
        # self.setHidden(True)


    def connect_sure(self):
        pass
        # self.info_dict[add_action_window.des_text] = self.des_text.text() if self.des_text.text() != '' else self.com_box.currentText()
        # self.info_dict[add_action_window.action_type] = self.com_box.currentText()
        # self.info_dict[add_action_window.speed] = self.speed_text.text() if self.speed_text.text() != '' else '150'
        # # 坐标信息需要通过主窗口传递过来
        # # self.info_dict[add_action_window.points] = None
        # self.info_dict[add_action_window.leave] = '1' if self.leave_check_box.checkState()==Qt.Checked else '0'
        # self.info_dict[add_action_window.trigger] = '1' if self.camera_trigger_check_box.checkState()==Qt.Checked else '0'
        # signal = json.dumps(self.info_dict)
        # # 发送开头sure标志-->判断是确认按钮按下
        # self.signal.emit('sure>' + signal)
        # self.close()


    def closeEvent(self, event):
        pass
        # # 如果取消则恢复默认
        # add_action_window.add_action_flag = False
        # uArm_action.uArm_action_type = None
        # self.info_dict = {add_action_window.des_text    : None,
        #                   add_action_window.action_type : uArm_action.uArm_click,
        #                   add_action_window.points      : None,
        #                   add_action_window.leave       : 1}
        # self.des_text.setText('')
        # self.des_text.setPlaceholderText('请输入动作描述(可不写)')
        # self.com_box.setCurrentText(uArm_action.uArm_click)
        # self.speed_text.setText('')
        # self.speed_text.setPlaceholderText('请输入动作速度(可不写)')
        # self.points.setText('')
        # self.leave_check_box.setCheckState(Qt.Checked)
        # self.close()