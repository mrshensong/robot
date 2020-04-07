import os
import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import AssertAction, GloVar, MergePath, IconPath


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
        # 缩略图标签
        self.thumbnail_size = (100, 100)
        self.initUI()

    # 初始化
    def initUI(self):
        # 创建一个表单布局
        self.from_layout = QFormLayout()
        # 设置标签右对齐, 不设置是默认左对齐
        self.from_layout.setLabelAlignment(Qt.AlignCenter)
        # 设置表单内容
        # 是否开始录制视频
        self.start_select_assert_template = QCheckBox(self)
        self.start_select_assert_template.setCheckState(Qt.Unchecked)
        self.start_select_assert_template.stateChanged.connect(self.connect_select_assert_template)
        # 视频名称
        self.template_name_edit = QLineEdit(self)
        template_name = MergePath([GloVar.project_picture_path, 'assert', AssertAction.assert_template_name]).merged_path
        self.template_name_edit.setPlaceholderText(template_name)
        self.template_name_edit.setEnabled(False)
        # 表单布局
        self.from_layout.addRow('框选预期模板: ', self.start_select_assert_template)
        self.from_layout.addRow('预期模板名字: ', self.template_name_edit)
        # 缩略图
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFixedSize(self.thumbnail_size[0], self.thumbnail_size[0])
        # 载入图片
        self.reload_thumbnail(IconPath.Icon_picture)
        self.thumbnail_h_layout = QHBoxLayout()
        self.thumbnail_h_layout.addStretch(1)
        self.thumbnail_h_layout.addWidget(self.thumbnail_label)
        self.thumbnail_h_layout.addStretch(1)
        # 确定按钮
        self.sure_button = QPushButton('确定', self)
        self.sure_button.clicked.connect(self.connect_sure)
        # 确定button横向布局(处于中间)
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.sure_button)
        self.button_layout.addStretch(1)

        self.general_layout = QVBoxLayout()
        self.general_layout.addLayout(self.from_layout)
        self.general_layout.addLayout(self.thumbnail_h_layout)
        self.general_layout.addLayout(self.button_layout)

        self.setLayout(self.general_layout)
        # 设置最小尺寸
        self.setMinimumWidth(300)

    # 重新载入缩略图
    def reload_thumbnail(self, image):
        origin_image = QImage(image)
        origin_width = origin_image.width()
        origin_height = origin_image.height()
        max_num = max(origin_width, origin_height)
        if max_num > self.thumbnail_size[0]:
            scale = self.thumbnail_size[0] / max_num
        else:
            scale = 1.0
        new_size = QSize(origin_width * scale, origin_height * scale)
        pix_map = QPixmap.fromImage(origin_image.scaled(new_size, Qt.IgnoreAspectRatio))
        self.thumbnail_label.setPixmap(pix_map)

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
