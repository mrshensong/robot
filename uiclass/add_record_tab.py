import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QCheckBox, QLineEdit, QPushButton
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import RecordAction, Logger

# 动作添加控件
class AddRecordTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddRecordTab, self).__init__(parent)
        self.parent = parent
        # 视频录像状态
        self.info_dict = {RecordAction.record_status : '',
                          RecordAction.video_type: '',
                          RecordAction.video_name: '',
                          RecordAction.standard_time: ''}
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
        self.video_type_edit.setPlaceholderText('默认(启动)')
        self.video_type_edit.setEnabled(False)
        # 视频名称
        self.video_name_edit = QLineEdit(self)
        self.video_name_edit.setPlaceholderText('默认(name)')
        self.video_name_edit.setEnabled(False)
        # 标准时间(用来判断测试时间是否在预期内)
        self.standard_time_edit = QLineEdit(self)
        self.standard_time_edit.setPlaceholderText('默认800(单位ms)')
        self.standard_time_edit.setEnabled(False)
        # 表单布局
        self.from_layout.addRow('开始录制视频: ', self.start_record_video)
        self.from_layout.addRow('停止录制视频: ', self.stop_record_video)
        self.from_layout.addRow('设置视频类型: ', self.video_type_edit)
        self.from_layout.addRow('设置视频名称: ', self.video_name_edit)
        self.from_layout.addRow('设置标准时间: ', self.standard_time_edit)

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
            self.video_type_edit.setEnabled(True)
            self.video_name_edit.setEnabled(True)
            self.standard_time_edit.setEnabled(True)
            RecordAction.current_video_type = '启动'
            RecordAction.current_video_name = 'name'
            RecordAction.current_standard_time = '800'
        elif self.start_record_video.checkState() == Qt.Unchecked:
            self.stop_record_video.setCheckState(Qt.Unchecked)
            self.stop_record_video.setEnabled(True)
            self.video_type_edit.setEnabled(False)
            self.video_name_edit.setEnabled(False)
            self.standard_time_edit.setEnabled(False)


    def connect_stop_record_video(self):
        if self.stop_record_video.checkState() == Qt.Checked:
            self.start_record_video.setCheckState(Qt.Unchecked)
            self.start_record_video.setEnabled(False)
            self.video_type_edit.setText(RecordAction.current_video_type)
            self.video_name_edit.setText(RecordAction.current_video_name)
            self.standard_time_edit.setText(RecordAction.current_standard_time)
        elif self.stop_record_video.checkState() == Qt.Unchecked:
            self.start_record_video.setCheckState(Qt.Unchecked)
            self.start_record_video.setEnabled(True)
            self.video_type_edit.clear()
            self.video_name_edit.clear()
            self.standard_time_edit.clear()


    # 按下确认按钮
    def connect_sure(self):
        if self.video_type_edit.text() != '':
            RecordAction.current_video_type = self.video_type_edit.text()
        self.info_dict[RecordAction.video_type] = RecordAction.current_video_type
        if self.video_name_edit.text() != '':
            RecordAction.current_video_name = self.video_name_edit.text()
        self.info_dict[RecordAction.video_name] = RecordAction.current_video_name
        if self.standard_time_edit.text() != '':
            RecordAction.current_standard_time = self.standard_time_edit.text()
        self.info_dict[RecordAction.standard_time] = RecordAction.current_standard_time
        if self.start_record_video.checkState() == Qt.Checked:
            self.info_dict[RecordAction.record_status] = RecordAction.record_start
        elif self.stop_record_video.checkState() == Qt.Checked:
            self.info_dict[RecordAction.record_status] = RecordAction.record_stop
        else:
            Logger('[没有选择视频录像状态, 请重新选择!]')
            return
        signal = json.dumps(self.info_dict)
        # 发送开头sure标志-->判断是确认按钮按下
        self.signal.emit('record_tab_sure>' + signal)