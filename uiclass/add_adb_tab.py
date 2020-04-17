import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from GlobalVar import *


# adb添加控件
class AddADBTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddADBTab, self).__init__(parent)
        self.parent = parent
        self.info_dict = {ADBAction.adb_desc: '',
                          ADBAction.adb_command: ''}
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
        # adb描述设置
        self.adb_desc_edit = QLineEdit(self)
        self.adb_desc_edit.setPlaceholderText('请输入adb描述')
        # adb命令
        self.adb_command_edit = QTextEdit(self)
        self.adb_command_edit.setPlaceholderText('请输入adb命令...')
        # 表单布局
        self.from_layout.addRow('adb描述: ', self.adb_desc_edit)
        self.from_layout.addRow('adb命令: ', self.adb_command_edit)
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
        adb_desc = self.adb_desc_edit.text()
        adb_command = self.adb_command_edit.toPlainText()
        self.info_dict[ADBAction.adb_desc] = 'adb描述' if adb_desc == '' else adb_desc
        self.info_dict[ADBAction.adb_command] = '' if adb_desc == '' else adb_command
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('adb_tab_sure>' + signal)
