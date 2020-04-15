import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from GlobalVar import BreakAction


# break添加控件
class AddBreakTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddBreakTab, self).__init__(parent)
        self.parent = parent
        self.info_dict = {BreakAction.break_action: BreakAction.break_out}
        self.initUI()

    # 初始化
    def initUI(self):
        self.general_layout = QVBoxLayout()
        # 创建一个表单布局
        self.from_layout = QFormLayout()
        self.button_layout = QHBoxLayout()
        # 设置标签右对齐, 不设置是默认左对齐
        self.from_layout.setLabelAlignment(Qt.AlignCenter)
        # 设置表单内容
        # 睡眠时间设置
        self.break_name_show = QLineEdit(self)
        self.break_name_show.setReadOnly(True)
        self.break_name_show.setText(BreakAction.break_out)
        # 表单布局
        self.from_layout.addRow('动作name: ', self.break_name_show)

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
        # 设置最小尺寸
        self.setMinimumWidth(300)

    def connect_sure(self):
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('break_tab_sure>' + signal)
