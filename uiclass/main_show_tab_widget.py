import time
import json
from threading import Thread
from PyQt5.QtWidgets import QTabWidget, QTextEdit, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.show_action_tab import ShowActionTab
from uiclass.show_case_tab import ShowCaseTab
from uiclass.video_label import VideoLabel
from GlobalVar import GloVar, RobotOther, WindowStatus, RecordAction, SleepAction, Logger, MotionAction, RobotArmAction

class MainShowTabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, video_tab='video'):
        super(MainShowTabWidget, self).__init__(parent)
        self.parent = parent
        # self.setTabPosition(self.South)
        # tab1
        self.video_tab = VideoTab(self)  # 1
        self.video_tab.signal[str].connect(self.recv_video_tab_signal)
        self.addTab(self.video_tab, video_tab)

    # 视频标签控件接收函数(接收到信息后需要进行的操作)
    def recv_video_tab_signal(self, info_str):
        self.signal.emit(info_str)


class VideoTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(VideoTab, self).__init__(parent)
        self.parent = parent
        self.initUI()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout(self)

        self.video_label = VideoLabel(self)
        self.video_label.signal[str].connect(self.recv_video_label_signal)

        self.h_layout.addStretch(1)
        self.h_layout.addWidget(self.video_label)
        self.h_layout.addStretch(1)

        self.general_layout.addStretch(1)
        self.general_layout.addLayout(self.h_layout)
        self.general_layout.addStretch(1)

        self.setLayout(self.general_layout)


    # 接收到video_label的信息
    def recv_video_label_signal(self, signal_str):
        if signal_str.startswith('reset_video_label_size>local_video'):
            self.video_label_adaptive(self.video_label.local_video_width, self.video_label.local_video_height)
        elif signal_str.startswith('reset_video_label_size>live_video'):
            self.video_label_adaptive(self.video_label.real_time_video_width, self.video_label.real_time_video_height)
        # 获取到的坐标信息
        elif signal_str.startswith('position_info>'):
            # 只传有效信息
            self.signal.emit(signal_str.split('position_info>')[1])
        else:
            pass


    # 视频标签自适应
    def video_label_adaptive(self, video_width, video_height):
        # video_label高度和VideoTab的高度大致相同(留点余量)
        # video_label宽度为VideoTab的宽度大致相同(留点余量)
        self.video_label.video_label_size_width  = int((self.width() - 60))
        self.video_label.video_label_size_height = int((self.height() - 60))
        # 更改label_video大小以确保视频展示不失比例
        # 真实视频比例
        video_size_scale = float(video_height / video_width)
        # 临界比例(根据页面网格布局得到, 不可随便修改)
        limit_size_scale = float(self.video_label.video_label_size_height / self.video_label.video_label_size_width)
        if video_size_scale >= limit_size_scale:
            self.video_label.video_label_size_height = self.video_label.video_label_size_height
            self.video_label.video_label_size_width = int((self.video_label.video_label_size_height / video_height) * video_width)
        else:
            self.video_label.video_label_size_width = self.video_label.video_label_size_width
            self.video_label.video_label_size_height = int((self.video_label.video_label_size_width / video_width) * video_height)
        self.video_label.setFixedSize(self.video_label.video_label_size_width, self.video_label.video_label_size_height)
        # 计算视频和label_video之间比例因子(框选保存图片需要用到)
        self.video_label.x_unit = float(video_width / self.video_label.video_label_size_width)
        self.video_label.y_unit = float(video_height / self.video_label.video_label_size_height)
        # 重新计算框选的车机屏幕大小(可以适应不同大小屏幕)
        if sum(self.video_label.box_screen_size) > 0:
            self.video_label.box_screen_size[0] = int(self.video_label.width()  * self.video_label.box_screen_scale[0])
            self.video_label.box_screen_size[1] = int(self.video_label.height() * self.video_label.box_screen_scale[1])
            self.video_label.box_screen_size[2] = int(self.video_label.width()  * (self.video_label.box_screen_scale[2] - self.video_label.box_screen_scale[0]))
            self.video_label.box_screen_size[3] = int(self.video_label.height() * (self.video_label.box_screen_scale[3] - self.video_label.box_screen_scale[1]))


    def resizeEvent(self, event):
        # 实时流窗口缩放
        if self.video_label.video_play_flag is False:
            self.video_label_adaptive(self.video_label.real_time_video_width, self.video_label.real_time_video_height)
        # 本地视频窗口缩放
        elif self.video_label.video_play_flag is True:
            self.video_label_adaptive(self.video_label.local_video_width, self.video_label.local_video_height)
        # 和gif图缩放
        else:
            self.video_label_adaptive(self.video_label.local_video_width, self.video_label.local_video_height)