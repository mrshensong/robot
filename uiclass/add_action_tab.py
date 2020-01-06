import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QCheckBox, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt
from GlobalVar import RobotArmAction, MotionAction

# 动作添加控件
class AddActionTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddActionTab, self).__init__(parent)
        self.parent = parent
        self.info_dict = {MotionAction.des_text    : None,
                          MotionAction.action_type : RobotArmAction.uArm_click,
                          MotionAction.speed       : 150,
                          MotionAction.points      : None,
                          MotionAction.leave       : 1,
                          MotionAction.trigger     : 0}
        self.initUI()


    # 初始化
    def initUI(self):
        self.general_layout = QVBoxLayout()
        # 创建一个表单布局
        self.from_layout = QFormLayout()
        self.button_layout = QHBoxLayout()
        # 设置标签右对齐, 不设置是默认左对齐
        self.from_layout.setLabelAlignment(Qt.AlignCenter)
        items = [RobotArmAction.uArm_click,
                 RobotArmAction.uArm_double_click,
                 RobotArmAction.uArm_long_click,
                 RobotArmAction.uArm_slide]

        # 设置表单内容
        # 动作描述
        self.des_text = QLineEdit(self)
        self.des_text.setPlaceholderText('动作描述(选填)')
        # 动作选择
        self.com_box = QComboBox(self)
        self.com_box.addItems(items)
        self.com_box.currentIndexChanged.connect(self.connect_com_box)
        # 动作速度
        self.speed_text = QLineEdit(self)
        self.speed_text.setPlaceholderText('动作速度(选填)')
        # 坐标
        self.points = QLineEdit(self)
        self.points.setPlaceholderText('自动获取(不填)')
        # 是否收回
        self.leave_check_box = QCheckBox(self)
        self.leave_check_box.setCheckState(Qt.Checked)
        # 是否触发相机录像标记
        self.camera_trigger_check_box = QCheckBox(self)
        self.camera_trigger_check_box.setCheckState(Qt.Unchecked)
        # 表单布局
        self.from_layout.addRow('描述: ', self.des_text)
        self.from_layout.addRow('动作: ', self.com_box)
        self.from_layout.addRow('速度: ', self.speed_text)
        self.from_layout.addRow('坐标: ', self.points)
        self.from_layout.addRow('收回: ', self.leave_check_box)
        self.from_layout.addRow('触发: ', self.camera_trigger_check_box)

        # 获取坐标
        self.get_points_button = QPushButton('获取坐标', self)
        self.get_points_button.clicked.connect(self.connect_get_points)
        # 确定按钮
        self.sure_button = QPushButton('确定', self)
        self.sure_button.clicked.connect(self.connect_sure)
        # 两个button横向布局
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.get_points_button)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.sure_button)
        self.button_layout.addStretch(1)

        self.general_layout.addLayout(self.from_layout)
        self.general_layout.addLayout(self.button_layout)

        self.setLayout(self.general_layout)
        # 设置最小尺寸
        self.setMinimumWidth(300)


    def connect_com_box(self):
        self.signal.emit('action_tab_action>'+self.com_box.currentText())


    def connect_get_points(self):
        # 发送获取坐标事件信息(即隐藏控件)
        self.signal.emit('action_tab_get_points>')


    def connect_sure(self):
        self.info_dict[MotionAction.des_text] = self.des_text.text() if self.des_text.text() != '' else self.com_box.currentText()
        self.info_dict[MotionAction.action_type] = self.com_box.currentText()
        self.info_dict[MotionAction.speed] = self.speed_text.text() if self.speed_text.text() != '' else '150'
        # 坐标信息需要通过主窗口传递过来
        # self.info_dict[add_action_window.points] = None
        self.info_dict[MotionAction.leave] = '1' if self.leave_check_box.checkState()==Qt.Checked else '0'
        self.info_dict[MotionAction.trigger] = '1' if self.camera_trigger_check_box.checkState()==Qt.Checked else '0'
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('action_tab_sure>' + signal)