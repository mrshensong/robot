import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QScrollArea, QTextEdit, QFrame, QFileDialog, QTabBar
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from uiclass.video_label import VideoLabel
from GlobalVar import IconPath, GloVar, Profile, Logger


class MainShowTabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, camera_width, camera_height):
        super(MainShowTabWidget, self).__init__(parent)
        self.parent = parent
        self.setFont(QFont(GloVar.font, 13))
        self.setTabsClosable(True)
        # 样式设置
        style_sheet = 'QTabWidget:pane{ border: 1px; top: -1px;}\
                       QTabWidget:tab-bar{top: 0px; alignment:left;}\
                       QTabBar::tab{height: 25px; margin-right: 0px; margin-bottom:-3px; padding-left: 5px; padding-right: 5px;}\
                       QTabBar::tab:selected{border: 1px solid #7A7A7A; color: blue; background-color: white; border-bottom: 5px solid blue;}\
                       QTabBar::tab:!selected{border: 1px solid #7A7A7A;}\
                       QTabBar::tab:!selected:hover{border: 1px solid #7A7A7A; color: #0099CC;}\
                       QTabBar::close-button {image: url(' + IconPath.Icon_main_tab_widget_close_tab + '); subcontrol-position: bottom right;}\
                       QTabBar::close-button:hover {image: url(' + IconPath.Icon_main_tab_widget_close_tab_hover + ');}'
        self.setStyleSheet(style_sheet)
        # 关闭tab触发事件
        self.tabCloseRequested.connect(self.close_tab)
        # 标签位置放在底部
        # self.setTabPosition(self.South)
        # 视频页
        self.video_tab = VideoTab(self, camera_width=camera_width, camera_height=camera_height)  # 1
        self.video_tab.signal[str].connect(self.recv_video_tab_signal)
        # QTabWidget默认只有视频页
        self.addTab(self.video_tab, 'video')
        # 设置video栏不可关闭
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)
        # 设置自动不显示tab(tab数量小于2个的时候)
        self.tabBar().setAutoHide(True)

    # 视频标签控件接收函数(接收到信息后需要进行的操作)
    def recv_video_tab_signal(self, signal_str):
        self.signal.emit(signal_str)

    # 图片标签控件接收函数(接收到信息后需要进行的操作)
    def recv_picture_tab_signal(self, signal_str):
        self.signal.emit(signal_str)

    # 报告标签控件接收函数(接收到信息后需要进行的操作)
    def recv_report_tab_signal(self, signal_str):
        self.signal.emit(signal_str)

    # 文本标签控件接收函数(接收到信息后需要进行的操作)
    def recv_text_tab_signal(self, signal_str):
        self.signal.emit(signal_str)

    # 关闭标签页(需要判断)
    def close_tab(self, index):
        self.removeTab(index)
        # print('当前剩余tab: ', self.count())


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
        self.general_layout.setContentsMargins(0, 0, 0, 0)
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
        # 视频动作中的视频模板框选完成
        elif signal_str.startswith('draw_frame_finished>'):
            self.signal.emit(signal_str)
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
        self.signal.emit('resize>')
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

    def __init__(self, parent, picture_path):
        super(PictureTab, self).__init__(parent)
        self.parent = parent
        self.setFont(QFont(GloVar.font, 13))
        self.picture_path = picture_path
        self.picture_size_width = None
        self.picture_size_height = None
        self.picture_zoom_scale = 1.0
        self.initUI()
        self.show_picture()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.general_layout.setContentsMargins(0, 3, 0, 0)
        self.picture_h_layout = QHBoxLayout(self)
        self.button_h_layout = QHBoxLayout(self)
        # 打开文件按钮
        self.open_file_button = QToolButton()
        # 打开文件快捷键
        self.open_file_button.setShortcut('o')
        self.open_file_button.setEnabled(True)
        self.open_file_button.setToolTip('open_file(o)')
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
        self.picture_path_label.setFont(QFont(GloVar.font, 13))
        # 显示照片尺寸
        self.picture_size_label = QLabel(self)
        self.picture_size_label.setText('size: [0:0], zoom: [1.0X]')
        self.picture_size_label.setFont(QFont(GloVar.font, 13))

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


    # 打开文件(图片)
    def connect_open_file(self):
        file_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='file_path').value
        # 文件过滤
        file_filter = 'jpg(*.jpg);;png(*.png);;jpeg(*.jpeg);;bmp(*.bmp)'
        # 返回元祖(第一个元素文件路径, 第二个元素文件类型), 这里只需要第一个文件路径
        picture_path = QFileDialog.getOpenFileName(self, '选择需要打开的文件', file_path, file_filter)[0]
        if picture_path:
            Logger('打开文件: %s' % picture_path)
            # 展示照片
            self.picture_path = picture_path
            self.show_picture()
            current_file_path = os.path.split(picture_path)[0]
            # 将当前picture_path路径保存到配置文件
            if file_path != current_file_path:
                Profile(type='write', file=GloVar.config_file_path, section='param', option='file_path', value=current_file_path)
        else:
            Logger('取消打开文件!')


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

    def resizeEvent(self, event):
        self.signal.emit('resize>')


# 报告tab
class ReportTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, report_path):
        super(ReportTab, self).__init__(parent)
        self.parent = parent
        self.setFont(QFont(GloVar.font, 13))
        self.report_path = report_path
        self.initUI()
        self.show_html()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.general_layout.setContentsMargins(0, 3, 0, 0)
        self.title_h_layout = QHBoxLayout(self)
        self.report_h_layout = QHBoxLayout(self)
        # 显示html路径
        self.html_path_label = QLabel(self)
        self.html_path_label.setMaximumHeight(25)
        self.html_path_label.setText('None')
        self.html_path_label.setFont(QFont(GloVar.font, 13))
        # 打开文件按钮
        self.open_file_button = QToolButton()
        # 打开文件快捷键
        self.open_file_button.setShortcut('o')
        self.open_file_button.setEnabled(True)
        self.open_file_button.setToolTip('open_file(o)')
        self.open_file_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_open_file + ')}')
        self.open_file_button.clicked.connect(self.connect_open_file)
        # 使用QFrame画出一条顶部横隔离线
        self.top_h_line_frame = QFrame(self)
        self.top_h_line_frame.setFrameShape(QFrame.HLine)
        # 使用QFrame画出一条底部横隔离线
        self.bottom_h_line_frame = QFrame(self)
        self.bottom_h_line_frame.setFrameShape(QFrame.HLine)
        # 使用QFrame画出一条左边竖隔离线
        self.left_v_line_frame = QFrame(self)
        self.left_v_line_frame.setFrameShape(QFrame.VLine)
        # 使用QFrame画出一条左边竖隔离线
        self.right_v_line_frame = QFrame(self)
        self.right_v_line_frame.setFrameShape(QFrame.VLine)
        # html展示
        self.html_show_text = QWebEngineView()
        self.html_show_text.setStyleSheet('background-color:blue')
        # title行布局
        self.title_h_layout.setSpacing(0)
        self.title_h_layout.addWidget(self.open_file_button)
        self.title_h_layout.addStretch(1)
        self.title_h_layout.addWidget(self.html_path_label)
        self.title_h_layout.addStretch(1)
        # report布局
        self.report_h_layout.setSpacing(0)
        self.report_h_layout.addWidget(self.left_v_line_frame)
        self.report_h_layout.addWidget(self.html_show_text)
        self.report_h_layout.addWidget(self.right_v_line_frame)
        # 全局布局
        self.general_layout.setSpacing(0)
        self.general_layout.addLayout(self.title_h_layout)
        self.general_layout.addWidget(self.top_h_line_frame)
        self.general_layout.addLayout(self.report_h_layout)
        self.general_layout.addWidget(self.bottom_h_line_frame)
        self.setLayout(self.general_layout)


    # 打开文件
    def connect_open_file(self):
        file_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='file_path').value
        # 文件过滤
        file_filter = 'html(*.html)'
        # 返回元祖(第一个元素文件路径, 第二个元素文件类型), 这里只需要第一个文件路径
        report_path = QFileDialog.getOpenFileName(self, '选择需要打开的文件', file_path, file_filter)[0]
        if report_path:
            Logger('打开文件: %s' % report_path)
            # 展示报告
            self.report_path = report_path
            self.show_html()
            current_file_path = os.path.split(report_path)[0]
            # 将当前report_path路径保存到配置文件
            if file_path != current_file_path:
                Profile(type='write', file=GloVar.config_file_path, section='param', option='file_path', value=current_file_path)
        else:
            Logger('取消打开文件!')


    # html展示操作
    def show_html(self):
        # 展示文件路径
        self.html_path_label.setText(self.report_path)
        # 加载本地html文件
        self.html_show_text.load(QUrl('file:///' + self.report_path))

    def resizeEvent(self, event):
        self.signal.emit('resize>')


# 文本tab
class TextTab(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, text_path):
        super(TextTab, self).__init__(parent)
        self.parent = parent
        self.setFont(QFont(GloVar.font, 13))
        self.text_path = text_path
        self.initUI()
        self.show_text()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)
        self.general_layout.setContentsMargins(0, 3, 0, 0)
        self.text_h_layout = QHBoxLayout(self)
        self.title_h_layout = QHBoxLayout(self)
        # 显示文本路径
        self.text_path_label = QLabel(self)
        self.text_path_label.setText('None')
        self.text_path_label.setFont(QFont(GloVar.font, 13))

        # 打开文件按钮
        self.open_file_button = QToolButton()
        # 打开文件快捷键
        self.open_file_button.setShortcut('o')
        self.open_file_button.setEnabled(True)
        self.open_file_button.setToolTip('open_file(o)')
        self.open_file_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_open_file + ')}')
        self.open_file_button.clicked.connect(self.connect_open_file)

        # 编辑文本按钮
        self.edit_text_button = QToolButton()
        # 编辑快捷键
        self.edit_text_button.setShortcut('e')
        self.edit_text_button.setEnabled(False)
        self.edit_text_button.setToolTip('edit(e)')
        self.edit_text_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_main_tab_widget_edit_text + ')}')
        self.edit_text_button.clicked.connect(self.connect_edit_text)

        # 保存文本按钮
        self.save_text_button = QToolButton()
        # 保存快捷键
        self.save_text_button.setShortcut('ctrl+s')
        self.save_text_button.setEnabled(False)
        self.save_text_button.setToolTip('save(ctrl+s)')
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
        self.text_show_text.setFont(QFont('Times New Roman', 13))
        self.text_show_text.setReadOnly(True)
        self.text_h_layout.addWidget(self.text_show_text)

        self.general_layout.addLayout(self.title_h_layout)
        self.general_layout.addLayout(self.text_h_layout)

        self.setLayout(self.general_layout)


    # 打开文件
    def connect_open_file(self):
        file_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='file_path').value
        # 文件过滤
        file_filter = 'all file(*)'
        # 返回元祖(第一个元素文件路径, 第二个元素文件类型), 这里只需要第一个文件路径
        text_path = QFileDialog.getOpenFileName(self, '选择需要打开的文件', file_path, file_filter)[0]
        if text_path:
            text_type = text_path.split('.')[1]
            # 判断支持的类型
            if text_type in ['txt', 'py', 'xml', 'html', 'md', 'ini', 'TXT', 'PY', 'XML', 'HTML', 'MD', 'INI']:
                Logger('打开文件: %s' % text_path)
                # 展示文本
                self.text_path = text_path
                self.show_text()
                current_file_path = os.path.split(text_path)[0]
                # 将当前text_path路径保存到配置文件
                if file_path != current_file_path:
                    Profile(type='write', file=GloVar.config_file_path, section='param', option='file_path', value=current_file_path)
            else:
                Logger('暂不支持此类型文件!!!')
        else:
            Logger('取消打开文件!')


    # 编辑文本
    def connect_edit_text(self):
        Logger('编辑当前文件: %s' % self.text_path)
        # 允许写入
        self.text_show_text.setReadOnly(False)
        # 更改背景
        self.text_show_text.setStyleSheet('background-color:#C0D8F0')


    # 保存文本
    def connect_save_text(self):
        Logger('保存当前文件: %s' % self.text_path)
        # 获取文本内容
        text = self.text_show_text.toPlainText()
        with open(self.text_path, 'w+', encoding='utf-8') as f:
            f.write(text)
        # 不允许写入
        self.text_show_text.setReadOnly(True)
        # 恢复背景颜色
        self.text_show_text.setStyleSheet('background-color:white')


    # text展示操作
    def show_text(self):
        self.edit_text_button.setEnabled(True)
        self.save_text_button.setEnabled(True)
        self.text_show_text.setStyleSheet('background-color:white')
        with open(self.text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        self.text_path_label.setText(self.text_path)
        # self.text_show_text.setText(text)
        # 展示纯文本(不会渲染html)
        self.text_show_text.setPlainText(text)

    def resizeEvent(self, event):
        self.signal.emit('resize>')