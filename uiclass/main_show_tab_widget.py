import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QScrollArea, QTextEdit, QFrame
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from uiclass.video_label import VideoLabel
from GlobalVar import IconPath, GloVar


class MainShowTabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, camera_width, camera_height):
        super(MainShowTabWidget, self).__init__(parent)
        self.parent = parent
        # 标签位置放在底部
        # self.setTabPosition(self.South)
        # 视频页
        self.video_tab = VideoTab(self, camera_width=camera_width, camera_height=camera_height)  # 1
        self.video_tab.signal[str].connect(self.recv_video_tab_signal)
        # 照片页
        self.picture_tab = PictureTab(self)
        # 报告页
        self.report_tab = ReportTab(self)
        # text页面
        self.text_tab = TextTab(self)

        self.addTab(self.video_tab, 'video')
        self.addTab(self.picture_tab, 'picture')
        self.addTab(self.report_tab, 'report')
        self.addTab(self.text_tab, 'text')

    # 视频标签控件接收函数(接收到信息后需要进行的操作)
    def recv_video_tab_signal(self, info_str):
        self.signal.emit(info_str)


# 视频tab
class VideoTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, camera_width, camera_height):
        super(VideoTab, self).__init__(parent)
        self.parent = parent
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.initUI()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.video_label_h_layout = QHBoxLayout(self)

        self.video_label = VideoLabel(self, camera_width=self.camera_width, camera_height=self.camera_height)
        self.video_label.signal[str].connect(self.recv_video_label_signal)

        # 创建一个滚动区域
        self.video_scroll_area = QScrollArea()
        self.video_scroll_area.setWidget(self.video_label)
        self.video_scroll_area.setAlignment(Qt.AlignCenter)
        # 隐藏横竖向滚动条
        # self.video_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.video_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.video_label_h_layout.addWidget(self.video_scroll_area)

        self.general_layout.addLayout(self.video_label_h_layout)

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
        self.video_label.video_label_size_width  = int(self.video_scroll_area.width() - 2)
        self.video_label.video_label_size_height = int(self.video_scroll_area.height() - 2)
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
        # 重新计算框选的车机屏幕大小(可以适应不同大小屏幕, 通过判断框选比例来决定是否出现框选框, 如果box_screen_scale不为0, 就画出矩形框)
        if sum(self.video_label.box_screen_scale) > 0:
            # 车机是否框选了标志
            GloVar.add_action_button_flag = True
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
        # 打开文件按钮
        self.open_file_button = QToolButton()
        self.open_file_button.setEnabled(True)
        self.open_file_button.setToolTip('open_file')
        self.open_file_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_open_file + ')}')
        self.open_file_button.clicked.connect(self.connect_open_file)
        # 放大按钮
        self.zoom_button = QToolButton()
        self.zoom_button.setEnabled(False)
        self.zoom_button.setToolTip('zoom')
        self.zoom_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_zoom_picture + ')}')
        self.zoom_button.clicked.connect(self.connect_zoom_button)
        # 原图按钮
        self.original_size_button = QToolButton()
        self.original_size_button.setEnabled(False)
        self.original_size_button.setToolTip('original_size')
        self.original_size_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_original_size_picture + ')}')
        self.original_size_button.clicked.connect(self.connect_original_size_button)
        # 缩小按钮
        self.zoom_out_button = QToolButton()
        self.zoom_out_button.setEnabled(False)
        self.zoom_out_button.setToolTip('zoom_out')
        self.zoom_out_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_zoom_out_picture + ')}')
        self.zoom_out_button.clicked.connect(self.connect_zoom_out_button)
        # 显示图片路径
        self.picture_path_label = QLabel(self)
        self.picture_path_label.setText('None')
        # 显示照片尺寸
        self.picture_size_label = QLabel(self)
        self.picture_size_label.setText('size: [0:0], zoom: [1.0X]')

        self.button_h_layout.addWidget(self.open_file_button)
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

        # 创建一个滚动区域
        self.picture_scroll_area = QScrollArea()
        self.picture_scroll_area.setWidget(self.picture_label)

        self.picture_h_layout.addWidget(self.picture_scroll_area)

        self.general_layout.addLayout(self.button_h_layout)
        self.general_layout.addLayout(self.picture_h_layout)

        self.setLayout(self.general_layout)


    # 打开文件
    def connect_open_file(self):
        pass


    # 放大操作
    def connect_zoom_button(self):
        current_zoom_scale = round((self.picture_zoom_scale + 0.5), 1)
        width = int(self.picture_size_width * current_zoom_scale)
        height = int(self.picture_size_height * current_zoom_scale)
        # 不用判断(可以无限放大)
        self.picture_zoom_scale = current_zoom_scale
        self.picture_label.setFixedSize(width, height)
        self.picture_size_label.setText('size: [%d:%d], zoom: [%.1fX]' % (self.picture_size_width, self.picture_size_height, self.picture_zoom_scale))


    # 缩小操作
    def connect_zoom_out_button(self):
        current_zoom_scale = round((self.picture_zoom_scale - 0.5), 1)
        width = int(self.picture_size_width * current_zoom_scale)
        height = int(self.picture_size_height * current_zoom_scale)
        # 需要判断(不能小于0)
        if current_zoom_scale > 0.0:
            self.picture_zoom_scale = current_zoom_scale
            self.picture_label.setFixedSize(width, height)
            self.picture_size_label.setText('size: [%d:%d], zoom: [%.1fX]' % (self.picture_size_width, self.picture_size_height, self.picture_zoom_scale))


    # 原图操作
    def connect_original_size_button(self):
        self.picture_zoom_scale = 1.0
        self.picture_label.setFixedSize(self.picture_size_width, self.picture_size_height)
        self.picture_size_label.setText('size: [%d:%d], zoom: [1.0X]' % (self.picture_size_width, self.picture_size_height))


    # 图片展示操作
    def show_picture(self):
        self.zoom_button.setEnabled(True)
        self.zoom_out_button.setEnabled(True)
        self.original_size_button.setEnabled(True)
        image = cv2.imdecode(np.fromfile(self.picture_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        size = image.shape
        self.picture_size_width = int(size[1])
        self.picture_size_height = int(size[0])
        if self.picture_size_width < self.picture_scroll_area.width() and self.picture_size_height < self.picture_scroll_area.height():
            # widget居中显示
            self.picture_scroll_area.setAlignment(Qt.AlignCenter)
        elif self.picture_size_width < self.picture_scroll_area.width() and self.picture_size_height >= self.picture_scroll_area.height():
            # 居中靠上
            self.picture_scroll_area.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        elif self.picture_size_width >= self.picture_scroll_area.width() and self.picture_size_height < self.picture_scroll_area.height():
            # 居中中靠左
            self.picture_scroll_area.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        elif self.picture_size_width >= self.picture_scroll_area.width() and self.picture_size_height >= self.picture_scroll_area.height():
            # 居上靠左
            self.picture_scroll_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.picture_label.setFixedSize(self.picture_size_width, self.picture_size_height)
        self.picture_label.setPixmap(QPixmap(self.picture_path))
        self.picture_path_label.setText(str(self.picture_path))
        self.picture_size_label.setText('size: [%d:%d], zoom: [1.0X]' % (self.picture_size_width, self.picture_size_height))
        self.picture_zoom_scale = 1.0


# 报告tab
class ReportTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ReportTab, self).__init__(parent)
        self.parent = parent
        self.report_path = None
        self.initUI()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.title_h_layout = QHBoxLayout(self)
        # self.line =
        # 显示html路径
        self.html_path_label = QLabel(self)
        self.html_path_label.setMaximumHeight(25)
        self.html_path_label.setText('None')
        # 打开文件按钮
        self.open_file_button = QToolButton()
        self.open_file_button.setEnabled(True)
        self.open_file_button.setToolTip('open_file')
        self.open_file_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_open_file + ')}')
        self.open_file_button.clicked.connect(self.connect_open_file)
        # 使用QFrame画出一条隔离线
        self.h_line_frame = QFrame(self)
        self.h_line_frame.setFrameShape(QFrame.HLine)
        # html展示
        self.html_show_text = QWebEngineView()
        # title行布局
        self.title_h_layout.setSpacing(0)
        self.title_h_layout.addWidget(self.open_file_button)
        self.title_h_layout.addStretch(1)
        self.title_h_layout.addWidget(self.html_path_label)
        self.title_h_layout.addStretch(1)

        self.general_layout.addLayout(self.title_h_layout)
        self.general_layout.addWidget(self.h_line_frame)
        self.general_layout.addWidget(self.html_show_text)

        self.setLayout(self.general_layout)


    # 打开文件
    def connect_open_file(self):
        pass


    # html展示操作
    def show_html(self):
        # self.setHtml(html)
        # 加载本地html文件
        self.html_show_text.load(QUrl('file:///' + self.report_path))


# 文本tab
class TextTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(TextTab, self).__init__(parent)
        self.parent = parent
        self.text_path = None
        self.initUI()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.text_h_layout = QHBoxLayout(self)
        self.title_h_layout = QHBoxLayout(self)
        # 显示文本路径
        self.text_path_label = QLabel(self)
        self.text_path_label.setText('None')

        # 打开文件按钮
        self.open_file_button = QToolButton()
        self.open_file_button.setEnabled(True)
        self.open_file_button.setToolTip('open_file')
        self.open_file_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_open_file + ')}')
        self.open_file_button.clicked.connect(self.connect_open_file)

        # 编辑文本按钮
        self.edit_text_button = QToolButton()
        self.edit_text_button.setEnabled(False)
        self.edit_text_button.setToolTip('edit')
        self.edit_text_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_edit_text + ')}')
        self.edit_text_button.clicked.connect(self.connect_edit_text)

        # 保存文本按钮
        self.save_text_button = QToolButton()
        self.save_text_button.setEnabled(False)
        self.save_text_button.setToolTip('save')
        self.save_text_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_save_text + ')}')
        self.save_text_button.clicked.connect(self.connect_save_text)

        # title行布局
        self.title_h_layout.addWidget(self.open_file_button)
        self.title_h_layout.addWidget(self.edit_text_button)
        self.title_h_layout.addWidget(self.save_text_button)
        self.title_h_layout.addStretch(1)
        self.title_h_layout.addWidget(self.text_path_label)
        self.title_h_layout.addStretch(1)

        # text展示
        self.text_show_text = QTextEdit(self)
        self.text_show_text.setReadOnly(True)
        self.text_h_layout.addWidget(self.text_show_text)

        self.general_layout.addLayout(self.title_h_layout)
        self.general_layout.addLayout(self.text_h_layout)

        self.setLayout(self.general_layout)


    # 打开文件
    def connect_open_file(self):
        pass


    # 编辑文本
    def connect_edit_text(self):
        pass


    # 保存文本
    def connect_save_text(self):
        pass


    # text展示操作
    def show_text(self):
        with open(self.text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        self.text_path_label.setText(self.text_path)
        # self.text_show_text.setText(text)
        # 展示纯文本(不会渲染html)
        self.text_show_text.setPlainText(text)