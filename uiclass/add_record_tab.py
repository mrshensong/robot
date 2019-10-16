import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QLineEdit, QPushButton
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import record_action, logger

# 动作添加控件
class AddRecordTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddRecordTab, self).__init__(parent)
        self.parent = parent
        # 视频录像状态
        self.info_dict = {record_action.record_status : '',
                          record_action.video_type: '',
                          record_action.video_name: ''}
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
        self.start_record_video = QCheckBox(self)
        self.start_record_video.setCheckState(Qt.Unchecked)
        self.start_record_video.stateChanged.connect(self.connect_start_record_video)
        # 是否停止录制视频
        self.stop_record_video = QCheckBox(self)
        self.stop_record_video.setCheckState(Qt.Unchecked)
        self.stop_record_video.stateChanged.connect(self.connect_stop_record_video)
        # 视频类型
        self.video_type_edit = QLineEdit(self)
        self.video_type_edit.setPlaceholderText('默认test')
        # 视频名称
        self.video_name_edit = QLineEdit(self)
        self.video_name_edit.setPlaceholderText('默认test.mp4(后缀可无)')
        # 表单布局
        self.from_layout.addRow('开始录制视频: ', self.start_record_video)
        self.from_layout.addRow('停止录制视频: ', self.stop_record_video)
        self.from_layout.addRow('设置视频类型: ', self.video_type_edit)
        self.from_layout.addRow('设置视频名称: ', self.video_name_edit)

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
        self.setFont(QFont('Times New Roman', 11))
        # 设置最小尺寸
        self.setMinimumWidth(300)


    def connect_start_record_video(self):
        if self.start_record_video.checkState() == Qt.Checked:
            self.stop_record_video.setCheckState(Qt.Unchecked)
            self.stop_record_video.setEnabled(False)
        elif self.start_record_video.checkState() == Qt.Unchecked:
            self.stop_record_video.setCheckState(Qt.Unchecked)
            self.stop_record_video.setEnabled(True)


    def connect_stop_record_video(self):
        if self.stop_record_video.checkState() == Qt.Checked:
            self.start_record_video.setCheckState(Qt.Unchecked)
            self.start_record_video.setEnabled(False)
        elif self.stop_record_video.checkState() == Qt.Unchecked:
            self.start_record_video.setCheckState(Qt.Unchecked)
            self.start_record_video.setEnabled(True)


    # 按下确认按钮
    def connect_sure(self):
        if self.video_type_edit.text() is '':
            self.info_dict[record_action.video_type] = 'test'
        else:
            self.info_dict[record_action.video_type] = self.video_type_edit.text()
        if self.video_name_edit.text() is '':
            self.info_dict[record_action.video_name] = 'test'
        else:
            if self.video_name_edit.text().endswith('.mp4') or self.video_name_edit.text().endswith('.MP4'):
                self.info_dict[record_action.video_name] = self.video_name_edit.text().split('.')[0]
            else:
                self.info_dict[record_action.video_name] = self.video_name_edit.text()
        if self.start_record_video.checkState() == Qt.Checked:
            self.info_dict[record_action.record_status] = record_action.record_start
        elif self.stop_record_video.checkState() == Qt.Checked:
            self.info_dict[record_action.record_status] = record_action.record_stop
        else:
            logger('[没有选择视频录像状态, 请重新选择!]')
            return
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('record_tab_sure>' + signal)