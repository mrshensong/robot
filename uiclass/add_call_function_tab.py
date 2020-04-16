import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import *


# call_function添加控件
class AddCallFunctionTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddCallFunctionTab, self).__init__(parent)
        self.parent = parent
        self.info_dict = {CallFunctionAction.function_name: None}
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
        # 选择函数设置
        # LeadingPosition:左侧
        self.function_name_show = QLineEdit(self)
        self.function_name_show.setReadOnly(True)
        # 选择函数的action
        self.select_function = QAction(self.function_name_show)
        self.select_function.setIcon(QIcon(IconPath.Icon_select_function_icon))
        self.select_function.triggered.connect(self.connect_select_function)
        self.function_name_show.addAction(self.select_function, QLineEdit.TrailingPosition)
        # 添加提示文本
        self.function_name_show.setPlaceholderText('请选择函数.')
        # 表单布局
        self.from_layout.addRow('函数name: ', self.function_name_show)

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

    # 选择函数
    def connect_select_function(self):
        # 通过选择框导入case
        function_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='function_path').value
        file, ok = QFileDialog.getOpenFileName(self, "选择函数", function_path, "标签文件 (*.xml)",
                                                 options=QFileDialog.DontUseNativeDialog)
        if ok:
            # 如果打开路径和配置文件路径不一样, 就将当前script路径保存到配置文件
            function_folder = os.path.split(file)[0]
            function_name = os.path.split(file)[1]
            if function_folder != function_path:
                Profile(type='write', file=GloVar.config_file_path, section='param', option='function_path',
                        value=function_folder)
            self.function_name_show.setText(function_name)
            self.info_dict[CallFunctionAction.function_name] = function_name

    def connect_sure(self):
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('call_function_tab_sure>' + signal)
