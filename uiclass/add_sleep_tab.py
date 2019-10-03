import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import icon_path, uArm_action, add_action_window, sleep_action

# 动作添加控件
class AddSleepTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddSleepTab, self).__init__(parent)
        self.parent = parent
        self.info_dict = {sleep_action.sleep_time    : None}
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
        # 睡眠时间设置
        self.sleep_time_edit = QLineEdit(self)
        self.sleep_time_edit.setPlaceholderText('请输入睡眠时间(单位:ms)')
        # 表单布局
        self.from_layout.addRow('睡眠时间: ', self.sleep_time_edit)

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


    def connect_sure(self):
        self.info_dict[sleep_action.sleep_time] = 1.0 if self.sleep_time_edit.text() == '' else float(self.sleep_time_edit.text())
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('sleep_tab_sure>' + signal)