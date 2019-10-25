import cv2
import numpy as np
import time
import json
from threading import Thread
from PyQt5.QtWidgets import QTabWidget, QTextEdit, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.show_action_tab import ShowActionTab
from uiclass.show_case_tab import ShowCaseTab
from uiclass.video_label import VideoLabel
from GlobalVar import GloVar, RobotOther, WindowStatus, RecordAction, SleepAction, Logger, MotionAction, RobotArmAction, IconPath

class MainShowTabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(MainShowTabWidget, self).__init__(parent)
        self.parent = parent
        # self.setTabPosition(self.South)
        # tab1
        self.video_tab = VideoTab(self)  # 1
        self.video_tab.signal[str].connect(self.recv_video_tab_signal)

        self.picture_tab = PictureTab(self)

        self.addTab(self.video_tab, 'video')
        self.addTab(self.picture_tab, 'picture')

    # 视频标签控件接收函数(接收到信息后需要进行的操作)
    def recv_video_tab_signal(self, info_str):
        self.signal.emit(info_str)


# 视频tab
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


# 照片tab
class PictureTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(PictureTab, self).__init__(parent)
        self.parent = parent
        self.picture_path = None
        self.picture_size_width = None
        self.picture_size_height = None
        self.picture_zoom_scale = 1.0
        self.initUI()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.picture_h_layout = QHBoxLayout(self)
        self.button_h_layout = QHBoxLayout(self)
        # 放大按钮
        self.zoom_button = QToolButton()
        self.zoom_button.setToolTip('zoom')
        self.zoom_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_zoom_picture + ')}')
        self.zoom_button.clicked.connect(self.connect_zoom_button)
        # 原图按钮
        self.original_size_button = QToolButton()
        self.original_size_button.setToolTip('original_size')
        self.original_size_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_original_size_picture + ')}')
        self.original_size_button.clicked.connect(self.connect_original_size_button)
        # 缩小按钮
        self.zoom_out_button = QToolButton()
        self.zoom_out_button.setToolTip('zoom_out')
        self.zoom_out_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_zoom_out_picture + ')}')
        self.zoom_out_button.clicked.connect(self.connect_zoom_out_button)
        # 显示图片路径
        self.picture_path_label = QLabel(self)
        self.picture_path_label.setText('None')
        # 显示照片尺寸
        self.picture_size_label = QLabel(self)
        self.picture_size_label.setText('size: [0:0], zoom: [1.0X]')

        self.button_h_layout.addWidget(self.zoom_button)
        self.button_h_layout.addWidget(self.original_size_button)
        self.button_h_layout.addWidget(self.zoom_out_button)
        self.button_h_layout.addStretch(1)
        self.button_h_layout.addWidget(self.picture_path_label)
        self.button_h_layout.addStretch(1)
        self.button_h_layout.addWidget(self.picture_size_label)

        # 填充图片标签
        self.picture_label = QLabel(self)
        self.picture_label.setScaledContents(True)

        self.picture_h_layout.addStretch(1)
        self.picture_h_layout.addWidget(self.picture_label)
        self.picture_h_layout.addStretch(1)

        self.general_layout.addLayout(self.button_h_layout)
        self.general_layout.addStretch(1)
        self.general_layout.addLayout(self.picture_h_layout)
        self.general_layout.addStretch(1)

        self.setLayout(self.general_layout)


    # 放大操作
    def connect_zoom_button(self):
        current_zoom_scale = round((self.picture_zoom_scale + 0.5), 1)
        width = int(self.picture_size_width * current_zoom_scale)
        height = int(self.picture_size_height * current_zoom_scale)
        if width < (self.width() - 50) and height < (self.height() - 50):
            self.picture_zoom_scale = current_zoom_scale
            self.picture_label.setFixedSize(width, height)
            self.picture_size_label.setText('size: [%d:%d], zoom: [%fX]' % (self.picture_size_width, self.picture_size_height, self.picture_zoom_scale))


    # 缩小操作
    def connect_zoom_out_button(self):
        current_zoom_scale = round((self.picture_zoom_scale - 0.5), 1)
        width = int(self.picture_size_width * current_zoom_scale)
        height = int(self.picture_size_height * current_zoom_scale)
        if current_zoom_scale > 0:
            self.picture_zoom_scale = current_zoom_scale
            self.picture_label.setFixedSize(width, height)
            self.picture_size_label.setText('size: [%d:%d], zoom: [%fX]' % (self.picture_size_width, self.picture_size_height, self.picture_zoom_scale))


    # 原图操作
    def connect_original_size_button(self):
        self.picture_zoom_scale = 1.0
        self.picture_label.setFixedSize(self.picture_size_width, self.picture_size_height)
        self.picture_size_label.setText('size: [%d:%d], zoom: [1.0X]' % (self.picture_size_width, self.picture_size_height))


    # 图片展示操作
    def show_picture(self):
        image = cv2.imdecode(np.fromfile(self.picture_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        size = image.shape
        self.picture_size_width = int(size[1])
        self.picture_size_height = int(size[0])
        if self.picture_size_width < (self.width() - 50) and self.picture_size_height < (self.height() - 50):
            self.picture_label.setFixedSize(self.picture_size_width, self.picture_size_height)
            self.zoom_button.setEnabled(True)
            self.zoom_out_button.setEnabled(True)
            self.original_size_button.setEnabled(True)
        else:
            # 真实照片比例
            picture_size_scale = float(self.picture_size_height / self.picture_size_width)
            # 临界比例(根据页面网格布局得到, 不可随便修改)
            limit_size_scale = float((self.height() - 50) / (self.width() - 50))
            if picture_size_scale >= limit_size_scale:
                picture_label_size_height = self.height() - 50
                picture_label_size_width = int(((self.height() - 50) / self.picture_size_height) * self.picture_size_width)
            else:
                picture_label_size_width = self.width() - 50
                picture_label_size_height = int(((self.width() - 50) / self.picture_size_width) * self.picture_size_height)
            self.picture_label.setFixedSize(picture_label_size_width, picture_label_size_height)
            self.zoom_button.setEnabled(False)
            self.zoom_out_button.setEnabled(False)
            self.original_size_button.setEnabled(False)
        self.picture_label.setPixmap(QPixmap(self.picture_path))
        self.picture_path_label.setText(str(self.picture_path))
        self.picture_size_label.setText('size: [%d:%d], zoom: [1.0X]' % (self.picture_size_width, self.picture_size_height))
        self.picture_zoom_scale = 1.0