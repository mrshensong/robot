import os
import json
from threading import Thread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import AssertAction, Logger, Profile, GloVar, MergePath
from uiclass.controls import SelectTemplateControl


# assert添加控件
class AddAssertTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent=None, case_name=None):
        super(AddAssertTab, self).__init__(parent)
        self.parent = parent
        # case名字
        self.case_name = case_name
        # 断言状态
        self.info_dict = {AssertAction.assert_template_name: 'assert_template_name'}
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
        # 是否开始录制视频
        self.start_select_assert_template = QCheckBox(self)
        self.start_select_assert_template.setCheckState(Qt.Unchecked)
        self.start_select_assert_template.stateChanged.connect(self.connect_select_assert_template)
        # 视频名称
        self.template_name_edit = QLineEdit(self)
        template_name = MergePath([GloVar.project_picture_path, 'assert', self.case_name, AssertAction.assert_template_name]).merged_path
        self.template_name_edit.setPlaceholderText(template_name)
        self.template_name_edit.setEnabled(False)
        # 表单布局
        self.from_layout.addRow('框选预期模板: ', self.start_select_assert_template)
        self.from_layout.addRow('预期模板名字: ', self.template_name_edit)
        # 缩略图
        self.thumbnail_label = QLabel()
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

    # 开始选中断言模板
    def connect_select_assert_template(self):
        if self.start_select_assert_template.checkState() == Qt.Checked:
            self.signal.emit(GloVar.assert_template + '>')

    # 按下确认按钮
    def connect_sure(self):
        self.info_dict[AssertAction.assert_template_name] = self.template_name_edit.text()
        # 整理数据
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('assert_tab_sure>' + signal)
