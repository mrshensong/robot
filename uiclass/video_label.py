import os
import cv2
import sys
import time
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QFrame, QLabel, QSlider, QApplication, QInputDialog, QPushButton
from PyQt5.QtGui import QMovie, QPixmap, QImage, QPainter, QPen, QPolygon, QCursor
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QRect
from GlobalVar import RobotArmAction, IconPath, Logger, GloVar, MergePath, RobotArmParam, Profile, RecordAction
from uiclass.timer import Timer


# 动作添加控件
class VideoLabel(QLabel):

    signal = pyqtSignal(str)

    def __init__(self, parent, camera_width, camera_height):
        super(VideoLabel, self).__init__(parent)
        self.parent = parent
        # 鼠标拖动的起始和终止x/y
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        # 鼠标是否按下标志
        self.mouse_press_flag = False
        # 鼠标是否右拖动动作标志
        self.mouse_move_flag = False
        # 视频真实尺寸和视频标签显示尺寸比例
        self.x_unit = 1.0
        self.y_unit = 1.0
        # 框选的屏幕起点和终点所占label_video比例
        self.box_screen_scale = eval(Profile(type='read', file=GloVar.config_file_path, section='param', option='box_screen_scale').value)
        # 框选的屏幕大小
        self.box_screen_size = [0, 0, 0, 0]
        # False直播/True录播/None什么都不播放状态
        self.video_play_flag = None
        # 是否使用电脑自带摄像头
        self.use_system_camera = True
        # 使用自定义定时器(视频播放定时器)
        self.timer_video = Timer()
        self.timer_video.timeSignal[str].connect(self.show_video)
        # 视频进度条刷新
        self.slider_thread = Timer(frequent=4)
        self.slider_thread.timeSignal[str].connect(self.slider_refresh)
        # 获取实时流时候的image
        self.timer_camera_image = Timer()
        self.timer_camera_image.timeSignal[str].connect(self.get_camera_image)
        # 相机状态
        self.camera_opened = 'OPENED'
        self.camera_closed = 'CLOSED'
        self.camera_status = self.camera_closed
        # 视频播放状态提示
        self.video_status_play_tip = '播放'
        self.video_status_pause_tip = '暂停'
        self.video_status_replay_tip = '重播'
        # 视频状态(初始化/播放中/暂停/播放完毕)
        self.STATUS_INIT = 0
        self.STATUS_PLAYING = 1
        self.STATUS_PAUSE = 2
        self.STATUS_STOP = 3
        self.video_status = self.STATUS_PLAYING
        # 重置视频标签的尺寸(根据VideoTab的尺寸来的)
        self.video_label_size_width = 0
        self.video_label_size_height = 0
        # 视频流&视频尺寸
        self.real_time_video_width = camera_width
        self.real_time_video_height = camera_height
        # 默认将实时流尺寸和本地视频尺寸置位一样
        self.local_video_width = camera_width
        self.local_video_height = camera_height
        # 数据处理gif动图
        self.data_processing_gif = QMovie(IconPath.data_processing_file)
        # 取出来图片的尺寸(shape有三个元素(height/width/通道数)-->我们只需要前两个height和width)
        # 因为读取出来的顺序为(height, width), 故而需要进行反装变为(height, width)
        self.data_process_background_size = tuple(reversed(cv2.imread(IconPath.data_is_ready_file).shape[:2]))
        # 当前获取的图片
        self.image = None
        # 模板图片(暂停时框选图片模板图片)
        self.mask_image = None
        '''以下为本地视频相关'''
        # 保存的case执行完的视频
        self.videos = []
        # 保存的视频中case类型和视频名字
        self.videos_title = []
        # 数据处理时, 保存没有对应视频模板的视频文件
        self.videos_without_template = []
        # 当前视频对象(本地视频)
        self.video_cap = None
        # 当前视频所在序列号(第0个视频)
        self.current_video = 0
        # 当前帧数
        self.current_frame = 0
        # 当前视频总帧数
        self.frame_count = 0
        # 视频title的序列号([1/5]点击.mp4)
        self.video_title_serial_show = ''
        # 滑动条标志位(如果有滑动动作标志为True, 否则为False)
        self.slider_flag = False
        # 读取配置文件中车机真实尺寸
        RobotArmParam.actual_screen_width = int(Profile(type='read', file=GloVar.config_file_path, section='param', option='actual_screen_width').value)
        RobotArmParam.actual_screen_height = int(Profile(type='read', file=GloVar.config_file_path, section='param', option='actual_screen_height').value)
        # 控件初始化
        self.initUI()

    def initUI(self):
        # 视频标签
        self.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        # self.label_video.signal[str].connect(self.recv_video_label_signal)
        # 填充背景图片
        self.setPixmap(QPixmap(IconPath.background_file))
        # 自动填充满label
        self.setScaledContents(True)
        # 标准光标
        self.setCursor(Qt.ArrowCursor)
        # 十字光标
        # self.setCursor(Qt.CrossCursor)
        # 按钮尺寸
        self.media_button_size = 36

        # label垂直布局
        self.label_v_layout = QVBoxLayout(self)
        self.label_v_layout.setSpacing(0)
        self.label_v_layout.setContentsMargins(0, 3, 0, 3)
        # button水平布局
        self.button_h_layout = QHBoxLayout(self)
        # 暂停按钮/空格键
        self.status_video_button = QPushButton(self)
        self.status_video_button.setCursor(QCursor(Qt.ArrowCursor))
        self.status_video_button.setObjectName('status_video_button')
        self.status_video_button.setToolTip(self.video_status_play_tip)
        self.status_video_button.setFixedSize(self.media_button_size, self.media_button_size)
        self.status_video_button.setStyleSheet('QPushButton{border-image: url('+ IconPath.Icon_player_play + ')}')
        self.status_video_button.setShortcut(Qt.Key_Space)
        self.status_video_button.clicked.connect(self.switch_video)
        self.status_video_button.setEnabled(False)
        # 上一个视频
        self.last_video_button = QPushButton(self)
        self.last_video_button.setCursor(QCursor(Qt.ArrowCursor))
        self.last_video_button.setObjectName('last_video_button')
        self.last_video_button.setToolTip('上一个视频')
        self.last_video_button.setFixedSize(self.media_button_size, self.media_button_size)
        self.last_video_button.setStyleSheet('QPushButton{border-image: url('+ IconPath.Icon_player_last_video + ')}')
        self.last_video_button.setShortcut(Qt.Key_Up)
        self.last_video_button.clicked.connect(self.last_video)
        self.last_video_button.setEnabled(True)
        # 下一个视频
        self.next_video_button = QPushButton(self)
        self.next_video_button.setCursor(QCursor(Qt.ArrowCursor))
        self.next_video_button.setObjectName('next_video_button')
        self.next_video_button.setToolTip('下一个视频')
        self.next_video_button.setFixedSize(self.media_button_size, self.media_button_size)
        self.next_video_button.setStyleSheet('QPushButton{border-image: url('+ IconPath.Icon_player_next_video + ')}')
        self.next_video_button.setShortcut(Qt.Key_Down)
        self.next_video_button.clicked.connect(self.next_video)
        self.next_video_button.setEnabled(False)
        # 上一帧
        self.last_frame_button = QPushButton(self)
        self.last_frame_button.setCursor(QCursor(Qt.ArrowCursor))
        self.last_frame_button.setObjectName('last_frame_button')
        self.last_frame_button.setToolTip('上一帧图像')
        self.last_frame_button.setFixedSize(self.media_button_size, self.media_button_size)
        self.last_frame_button.setStyleSheet('QPushButton{border-image: url('+ IconPath.Icon_player_last_frame + ')}')
        self.last_frame_button.setShortcut(Qt.Key_Left)
        self.last_frame_button.clicked.connect(self.last_frame)
        self.last_frame_button.setEnabled(False)
        # 下一帧
        self.next_frame_button = QPushButton(self)
        self.next_frame_button.setCursor(QCursor(Qt.ArrowCursor))
        self.next_frame_button.setObjectName('next_frame_button')
        self.next_frame_button.setToolTip('下一帧图像')
        self.next_frame_button.setFixedSize(self.media_button_size, self.media_button_size)
        self.next_frame_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_next_frame + ')}')
        self.next_frame_button.setShortcut(Qt.Key_Right)
        self.next_frame_button.clicked.connect(self.next_frame)
        self.next_frame_button.setEnabled(False)
        # 帧数显示
        self.label_frame_show = QLabel(self)
        self.label_frame_show.setObjectName("label_frame_show")
        self.label_frame_show.setAlignment(Qt.AlignCenter)
        self.label_frame_show.setText('')
        self.label_frame_show.setAlignment(Qt.AlignCenter)
        self.label_frame_show.setStyleSheet('color:black')
        # 显示视频名字
        self.label_video_title = QLabel(self)
        self.label_video_title.setObjectName("label_video_title")
        self.label_video_title.setAlignment(Qt.AlignCenter)
        self.label_video_title.setStyleSheet('color:white')
        self.label_video_title.setText('[实时视频流]')
        # 视频进度条
        self.video_progress_bar = QSlider(Qt.Horizontal, self)
        self.video_progress_bar.setCursor(QCursor(Qt.ArrowCursor))
        self.video_progress_bar.setEnabled(False)
        progress_bar_style = 'QSlider {border-color: #BCBCBC;}\
                              QSlider::groove:horizontal {border: 1px solid #999999; height: 1px; margin: 0px 0; left: 0px; right: 0px;}\
                              QSlider::handle:horizontal {border: 0px; width: 10px; margin: -5px 0px -5px 0px; border-radius: 5px; background: qradialgradient(spread:pad, cx:0, cy:0, radius:5, fx:0, fy:0, stop:0.6 #FFFFFF, stop:0.8 #FFFFFF);}\
                              QSlider::handle:horizontal:hover {border: 0px; width: 16px; margin: -8px 0px -8px 0px; border-radius: 8px; background: qradialgradient(spread:pad, cx:0, cy:5, radius:8, fx:0, fy:0, stop:0.6 #3090C0, stop:0.8 #3090C0);}\
                              QSlider::add-page:horizontal {background: qlineargradient(spread: pad, x1:0, y1:1, x2:0, y2:0, stop:0 #BCBCBC, stop:0.25 #BCBCBC, stop:0.5 #BCBCBC, stop:1 #BCBCBC);}\
                              QSlider::sub-page:horizontal {background: qlineargradient(spread: pad, x1:0, y1:1, x2:0, y2:0, stop:0 #439cf3, stop:0.25 #439cf3, stop:0.5 #439cf3, stop:1 #439cf3);}'
        self.video_progress_bar.setStyleSheet(progress_bar_style)
        self.video_progress_bar.valueChanged.connect(self.connect_video_progress_bar)
        # button布局管理
        self.button_h_layout.addStretch(1)
        self.button_h_layout.addWidget(self.last_frame_button)
        self.button_h_layout.addSpacing(30)
        self.button_h_layout.addWidget(self.last_video_button)
        self.button_h_layout.addSpacing(30)
        self.button_h_layout.addWidget(self.status_video_button)
        self.button_h_layout.addSpacing(30)
        self.button_h_layout.addWidget(self.next_video_button)
        self.button_h_layout.addSpacing(30)
        self.button_h_layout.addWidget(self.next_frame_button)
        self.button_h_layout.addStretch(1)
        # label布局管理
        self.label_v_layout.addWidget(self.label_video_title)
        self.label_v_layout.addStretch(1)
        self.label_v_layout.addWidget(self.label_frame_show)
        self.label_v_layout.addWidget(self.video_progress_bar)
        self.label_v_layout.addLayout(self.button_h_layout)
        # 重置控件布局
        self.setLayout(self.label_v_layout)

    '''以下内容为实时流工具栏相关操作'''
    # 切换摄像头状态
    def switch_camera_status(self):
        # 实时流保证30fps/s即可
        self.timer_video.frequent = 30
        # 本地视频进度条关闭
        self.slider_thread.stop()
        self.setCursor(Qt.ArrowCursor)
        self.last_video_button.setEnabled(False)
        self.next_video_button.setEnabled(False)
        self.last_frame_button.setEnabled(False)
        self.next_frame_button.setEnabled(False)
        # 关掉数据处理标志位
        GloVar.data_process_flag = False
        # 复位本地视频相关参数
        self.videos, self.videos_title = [], []
        self.current_frame, self.current_video, self.frame_count = 0, 0, 0
        if self.camera_status == self.camera_closed:
            # 不管本地视频是否正在播放(先关掉视频, 再切换到直播)
            self.timer_video.stop()
            self.video_play_flag = False
            self.label_video_title.setText('[实时视频流]')
            self.video_progress_bar.setValue(0)
            self.label_frame_show.setText('')
            self.video_progress_bar.setEnabled(False)
            GloVar.select_template_flag = False
            # 打开实时流视频并播放
            Logger('<打开摄像头>')
            self.camera_status = self.camera_opened
            # self.video_stream()
            self.timer_camera_image.start()
            time.sleep(3)
            # time.sleep(15)
            # 打开视频展示定时器
            self.timer_video.start()
            self.video_status = self.STATUS_PLAYING
            self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_pause + ')}')
            self.status_video_button.setToolTip(self.video_status_pause_tip)
            self.status_video_button.setEnabled(True)
            # 调整视频尺寸
            self.signal.emit('reset_video_label_size>live_video')
        else:
            Logger('<关闭摄像头>')
            # 关闭视频展示定时器
            self.timer_video.stop()
            # 停止获取实时流image
            self.timer_camera_image.stop()
            self.video_status = self.STATUS_INIT
            GloVar.select_template_flag = False
            # 既不是直播也不是本地视频播放
            self.video_play_flag = None
            self.setCursor(Qt.ArrowCursor)
            self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
            self.status_video_button.setToolTip(self.video_status_play_tip)
            self.camera_status = self.camera_closed
            self.setPixmap(QPixmap(IconPath.background_file))
            self.status_video_button.setEnabled(False)

    '''以下内容为视频进度栏的刷新'''
    # 连接到刷新视频进度栏
    def connect_video_progress_bar(self):
        self.current_frame = self.video_progress_bar.value()
        self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
        self.label_frame_show.setStyleSheet('color:white')
        self.slider_flag = True

    # 本地视频进度条刷新
    def slider_refresh(self):
        if self.video_play_flag is True and self.slider_flag is True:
            try:
                if self.video_status == self.STATUS_PLAYING:
                    self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
                    flag, self.image = self.video_cap.read()
                else:
                    self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
                    flag, self.image = self.video_cap.read()
                    show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                    self.setPixmap(QPixmap.fromImage(show_image))
                    self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
                    self.label_frame_show.setStyleSheet('color:white')
                    self.video_progress_bar.setValue(self.current_frame)
                    # 当遇到当前视频播放完毕时, 需要将进度条往回拉动的时候
                    if self.video_status == self.STATUS_STOP:
                        self.video_status = self.STATUS_PAUSE
                        self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
                        self.status_video_button.setToolTip(self.video_status_play_tip)
            except Exception as e:
                Logger('[当前视频播放完毕]')
            self.slider_flag = False

    # 定时器获取实时流摄像头图片(代替展示摄像头)
    def get_camera_image(self):
        self.image = GloVar.camera_image.copy()

    '''以下为视频展示相关操作(如播放/暂停/前后视频/前后帧等等)'''
    # 展示视频函数
    def show_video(self):
        # 实时模式
        if self.video_play_flag is False:
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(show_image))
            # if GloVar.save_pic_flag is True:
            #     cv2.imencode('.jpg', self.image.copy())[1].tofile('mask.jpg')
            #     GloVar.save_pic_flag = False
        # 本地视频播放模式(可以数帧)
        elif self.video_play_flag is True:
            if self.current_frame < self.frame_count:
                self.current_frame += 1
                flag, self.image = self.video_cap.read()
                if flag is True:
                    show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                    self.setPixmap(QPixmap.fromImage(show_image))
                    self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
                    self.label_frame_show.setStyleSheet('color:white')
                    self.video_progress_bar.setValue(self.current_frame)
                else:
                    self.video_cap.release()
                    self.video_status = self.STATUS_STOP
                    self.timer_video.stop()
                    self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_replay + ')}')
                    self.status_video_button.setToolTip(self.video_status_replay_tip)
                    # 因为已经读取视频停止, 故而帧数并没有增加(所以显示的也是最后一帧)
                    self.video_progress_bar.setValue(self.frame_count-1)
                    self.last_video_button.setEnabled(True)
                    self.next_video_button.setEnabled(True)
                    self.last_frame_button.setEnabled(True)
                    self.next_frame_button.setEnabled(True)
                    # 再重新加载视频(有可能视频播放完毕后, 需要往前进一帧)
                    self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
            else:
                self.video_status = self.STATUS_STOP
                self.timer_video.stop()
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_replay + ')}')
                self.status_video_button.setToolTip(self.video_status_replay_tip)
                self.last_video_button.setEnabled(True)
                self.next_video_button.setEnabled(True)
                self.last_frame_button.setEnabled(True)
                self.next_frame_button.setEnabled(True)
                # 再重新加载视频(有可能视频播放完毕后, 需要往前进一帧)
                self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
        # 其余模式(不播放视频)
        else:
            # 帧率显示置空
            self.label_frame_show.setText('')
            # 去掉视频title
            self.label_video_title.setText('')
        # QApplication.processEvents() # 界面刷新

    # 暂停视频后的模板框选准备
    def template_label(self):
        time.sleep(0.3)
        # 暂停后不允许机械臂动作操作
        RobotArmAction.uArm_action_type = None
        # 实时流
        if self.video_play_flag is False:
            # 如果是case中框选视频模板动作
            if GloVar.draw_frame_flag == GloVar.result_template:
                # 此目录必须一直存在(不能被修改(需要进行数据处理))
                GloVar.mask_path = MergePath([GloVar.project_picture_path, 'template']).merged_path
            elif GloVar.draw_frame_flag == GloVar.assert_template:
                # assert_template目录
                GloVar.mask_path = MergePath([GloVar.project_picture_path, 'assert']).merged_path
            # 其余情况
            else:
                GloVar.mask_path = MergePath([GloVar.project_picture_path, '框选图']).merged_path
        # 本地视频(框选模板名称默认和视频名相同>路径只是将video替换为picture即可)
        else:
            # 数据处理时传入的路径(根据视频名字来的)
            if GloVar.data_process_flag is True:
                video_name_path_cut_list = os.path.split(self.videos_title[self.current_video])[0].split('/')
                new_video_name_path_cut_list = video_name_path_cut_list[:-4] + ['template'] + video_name_path_cut_list[-2:]
                GloVar.mask_path = '/'.join(new_video_name_path_cut_list).replace('/video/', '/picture/')
            else:
                GloVar.mask_path = MergePath([GloVar.project_picture_path, '框选图']).merged_path

    # 空格键 播放/暂停/重播
    def switch_video(self):
        # 按钮防抖
        self.status_video_button.setEnabled(False)
        # 如果是实时模式
        if self.video_play_flag is False:
            if self.video_status is self.STATUS_INIT:
                self.timer_video.start()
                self.label_video_title.setStyleSheet('color:white')
                self.video_status = self.STATUS_PLAYING
                GloVar.select_template_flag = False
                self.setCursor(Qt.ArrowCursor)
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_pause + ')}')
                self.status_video_button.setToolTip(self.video_status_pause_tip)
                Logger('<打开视频流>')
            elif self.video_status is self.STATUS_PLAYING:
                self.timer_video.stop()
                self.video_status = self.STATUS_PAUSE
                GloVar.select_template_flag = True
                self.setCursor(Qt.CrossCursor)
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
                self.status_video_button.setToolTip(self.video_status_play_tip)
                self.template_label()
                self.mask_image = self.image
                Logger('<暂停视频流>')
            elif self.video_status is self.STATUS_PAUSE:
                self.timer_video.start()
                self.label_video_title.setStyleSheet('color:white')
                self.video_status = self.STATUS_PLAYING
                GloVar.select_template_flag = False
                self.setCursor(Qt.ArrowCursor)
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_pause + ')}')
                self.status_video_button.setToolTip(self.video_status_pause_tip)
                Logger('<打开视频流>')
        # 如果是播放本地视频
        elif self.video_play_flag is True:
            if self.video_status is self.STATUS_INIT:
                self.timer_video.start()
                self.last_frame_button.setEnabled(False)
                self.next_frame_button.setEnabled(False)
                self.last_video_button.setEnabled(False)
                self.next_video_button.setEnabled(False)
                self.label_video_title.setStyleSheet('color:white')
                self.video_status = self.STATUS_PLAYING
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_pause + ')}')
                self.status_video_button.setToolTip(self.video_status_pause_tip)
                GloVar.select_template_flag = False
                self.setCursor(Qt.ArrowCursor)
                Logger('<播放视频>')
            elif self.video_status is self.STATUS_PLAYING:
                self.timer_video.stop()
                # 暂停后/使能上下一帧
                self.last_frame_button.setEnabled(True)
                self.next_frame_button.setEnabled(True)
                self.last_video_button.setEnabled(True)
                self.next_video_button.setEnabled(True)
                self.video_status = self.STATUS_PAUSE
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
                self.status_video_button.setToolTip(self.video_status_play_tip)
                GloVar.select_template_flag = True
                self.setCursor(Qt.CrossCursor)
                self.template_label()
                self.mask_image = self.image
                Logger('<暂停视频>')
            elif self.video_status is self.STATUS_PAUSE:
                self.timer_video.start()
                self.last_frame_button.setEnabled(False)
                self.next_frame_button.setEnabled(False)
                self.last_video_button.setEnabled(False)
                self.next_video_button.setEnabled(False)
                self.label_video_title.setStyleSheet('color:white')
                self.video_status = self.STATUS_PLAYING
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_pause + ')}')
                self.status_video_button.setToolTip(self.video_status_pause_tip)
                GloVar.select_template_flag = False
                self.setCursor(Qt.ArrowCursor)
                Logger('<播放视频>')
            elif self.video_status is self.STATUS_STOP:
                self.current_frame = 0
                self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
                _, self.image = self.video_cap.read()
                show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                self.setPixmap(QPixmap.fromImage(show_image))
                self.label_video_title.setStyleSheet('color:white')
                self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
                self.label_frame_show.setStyleSheet('color:white')
                # 开启视频流
                self.timer_video.start()
                self.video_status = self.STATUS_PLAYING
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_pause + ')}')
                self.status_video_button.setToolTip(self.video_status_pause_tip)
                self.last_video_button.setEnabled(False)
                self.next_video_button.setEnabled(False)
                self.last_frame_button.setEnabled(False)
                self.next_frame_button.setEnabled(False)
                Logger('<重新播放视频>')
        time.sleep(0.1)  # 延时防抖
        self.status_video_button.setEnabled(True)

    # 切换到上个视频
    def last_video(self):
        # 防抖(首末行)
        self.last_video_button.setEnabled(False)
        if self.video_play_flag is True:
            self.timer_video.stop()
            self.video_status = self.STATUS_INIT
            self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
            self.status_video_button.setToolTip(self.video_status_play_tip)
            if self.current_video > 0:
                self.current_video = self.current_video - 1
            else:
                self.current_video = len(self.videos) - 1
            # 加载本地视频
            self.current_frame = 0
            self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            # 需要获取视频尺寸
            self.local_video_width = int(self.video_cap.get(3))
            self.local_video_height = int(self.video_cap.get(4))
            # 获取视频总帧数
            self.frame_count = int(self.video_cap.get(7))
            # 获取第一帧
            _, self.image = self.video_cap.read()
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(show_image))
            # 设置帧数显示
            self.label_frame_show.setText(str(self.current_frame+1) + 'F/' + str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
            # 设置视频进度滑动条范围
            self.video_progress_bar.setRange(0, self.frame_count - 1)
            # 设置视频title
            self.label_video_title.setText(self.set_video_title(self.current_video, self.videos, self.videos_title))
            self.label_video_title.setStyleSheet('color:white')
            self.last_frame_button.setEnabled(True)
            self.next_frame_button.setEnabled(True)
        self.last_video_button.setEnabled(True)
        self.next_video_button.setEnabled(True)
        self.status_video_button.setEnabled(True)
        self.setCursor(Qt.ArrowCursor)
        # 调整视频尺寸
        self.signal.emit('reset_video_label_size>local_video')
        self.last_video_button.setEnabled(True)

    # 切换到下个视频
    def next_video(self):
        # 防抖(首末行)
        self.next_video_button.setEnabled(False)
        if self.video_play_flag is True:
            self.timer_video.stop()
            self.video_status = self.STATUS_INIT
            self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
            self.status_video_button.setToolTip(self.video_status_play_tip)
            if self.current_video < len(self.videos) - 1:
                self.current_video = self.current_video + 1
            else:
                self.current_video = 0
            # 加载本地视频
            self.current_frame = 0
            self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            # 需要获取视频尺寸
            self.local_video_width = int(self.video_cap.get(3))
            self.local_video_height = int(self.video_cap.get(4))
            # 获取视频总帧数
            self.frame_count = int(self.video_cap.get(7))
            # 获取第一帧
            _, self.image = self.video_cap.read()
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(show_image))
            # 设置帧数显示
            self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
            # 设置视频进度滑动条范围
            self.video_progress_bar.setRange(0, self.frame_count - 1)
            # 设置视频title
            self.label_video_title.setText(self.set_video_title(self.current_video, self.videos, self.videos_title))
            self.label_video_title.setStyleSheet('color:white')
            self.last_frame_button.setEnabled(True)
            self.next_frame_button.setEnabled(True)
        self.last_video_button.setEnabled(True)
        self.next_video_button.setEnabled(True)
        self.status_video_button.setEnabled(True)
        self.setCursor(Qt.ArrowCursor)
        # 调整视频尺寸
        self.signal.emit('reset_video_label_size>local_video')
        self.next_video_button.setEnabled(True)

    # 切换到上一帧(不能防抖, 如果防抖的话就不能左右键快速播帧)
    def last_frame(self):
        # self.last_frame_button.setEnabled(False)
        if self.current_frame > 0:
            self.current_frame = self.current_frame - 1
        else:
            self.current_frame = 0
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        flag, self.image = self.video_cap.read()
        if flag is True:
            self.mask_image = self.image
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(show_image))
            self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
            # 当遇到当前视频播放完毕时, 需要回退帧的时候
            if self.video_status == self.STATUS_STOP:
                self.video_status = self.STATUS_PAUSE
                self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
                self.status_video_button.setToolTip(self.video_status_play_tip)
        else:
            self.video_cap.release()
            self.video_status = self.STATUS_STOP
            self.timer_video.stop()
            self.status_video_button.setStyleSheet('{border-image: url(' + IconPath.Icon_player_replay + ')}')
            self.status_video_button.setToolTip(self.video_status_replay_tip)
            self.video_progress_bar.setValue(self.frame_count-1)
            # 再重新加载视频(有可能视频播放完毕后, 需要往前进一帧)
            self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
        # self.last_frame_button.setEnabled(True)

    # 切换到下一帧(不能防抖, 如果防抖的话就不能左右键快速播帧)
    def next_frame(self):
        # self.next_frame_button.setEnabled(False)
        if self.current_frame < self.frame_count:
            self.current_frame = self.current_frame + 1
        else:
            self.current_frame = self.frame_count - 1
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        flag, self.image = self.video_cap.read()
        if flag is True:
            self.mask_image = self.image
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(show_image))
            self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
        else:
            self.video_cap.release()
            self.video_status = self.STATUS_STOP
            self.timer_video.stop()
            self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_replay + ')}')
            self.status_video_button.setToolTip(self.video_status_replay_tip)
            self.video_progress_bar.setValue(self.frame_count-1)
        # self.next_frame_button.setEnabled(True)

    # 导入本地视频操作
    def import_local_video(self):
        self.x0, self.y0 = self.x1, self.y1
        self.current_frame, self.current_video, self.frame_count = 0, 0, 0
        # 加载本地视频对象
        self.video_cap = cv2.VideoCapture(self.videos[0])  # 重新加载这个视频
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # 需要获取视频尺寸
        self.local_video_width = int(self.video_cap.get(3))
        self.local_video_height = int(self.video_cap.get(4))
        # 获取视频总帧数
        self.frame_count = int(self.video_cap.get(7))
        # 本地视频播放标志打开, 视频状态为STATUS_INIT
        self.video_play_flag = True
        self.video_status = self.STATUS_INIT
        self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
        self.status_video_button.setToolTip(self.video_status_play_tip)
        # 设置视频title
        self.label_video_title.setText(self.set_video_title(self.current_video, self.videos, self.videos_title))
        self.label_video_title.setStyleSheet('color:white')
        # 获取第一帧
        _, self.image = self.video_cap.read()
        show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(show_image))
        # 设置帧数显示
        self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
        self.label_frame_show.setStyleSheet('color:white')
        # 使能视频(播放/暂停/重播)按钮和视频进度条
        self.status_video_button.setEnabled(True)
        self.video_progress_bar.setEnabled(True)
        self.video_progress_bar.setRange(0, self.frame_count - 1)
        self.video_progress_bar.setValue(self.current_frame)
        self.slider_thread.start()
        self.last_video_button.setEnabled(True)
        self.next_video_button.setEnabled(True)
        self.last_frame_button.setEnabled(True)
        self.next_frame_button.setEnabled(True)
        # 关掉数据处理标志位
        GloVar.data_process_flag = False
        # 调整视频尺寸
        self.signal.emit('reset_video_label_size>local_video')

    # 导入视频处理视频
    def import_data_process_with_video(self):
        self.x0, self.y0 = self.x1, self.y1
        self.current_frame, self.current_video, self.frame_count = 0, 0, 0
        # 加载本地视频对象
        self.video_cap = cv2.VideoCapture(self.videos[0])  # 重新加载这个视频
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # 需要获取视频尺寸
        self.local_video_width = int(self.video_cap.get(3))
        self.local_video_height = int(self.video_cap.get(4))
        # 获取视频总帧数
        self.frame_count = int(self.video_cap.get(7))
        # 本地视频播放标志打开, 视频状态为STATUS_INIT
        self.video_play_flag = True
        self.video_status = self.STATUS_INIT
        self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
        self.status_video_button.setToolTip(self.video_status_play_tip)
        # 设置视频title
        self.label_video_title.setText(self.set_video_title(self.current_video, self.videos, self.videos_title))
        self.label_video_title.setStyleSheet('color:white')
        # 获取第一帧
        _, self.image = self.video_cap.read()
        show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(show_image))
        # 设置帧数显示
        self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
        self.label_frame_show.setStyleSheet('color:white')
        # 使能视频(播放/暂停/重播)按钮和视频进度条
        self.status_video_button.setEnabled(True)
        self.last_video_button.setEnabled(True)
        self.next_video_button.setEnabled(True)
        self.last_frame_button.setEnabled(True)
        self.next_frame_button.setEnabled(True)
        self.video_progress_bar.setEnabled(True)
        self.video_progress_bar.setValue(self.current_frame)
        self.video_progress_bar.setRange(0, self.frame_count - 1)
        self.slider_thread.start()
        # 调整视频尺寸
        self.signal.emit('reset_video_label_size>local_video')

    # 数据处理导入视频(没有需要数据处理的视频)
    def import_data_process_without_video(self):
        # 关闭视频展示定时器
        self.timer_video.stop()
        # 此时什么都不播放(状态为None)
        self.video_play_flag = None
        # 关掉数据处理标志位
        GloVar.data_process_flag = False
        # 复位视频状态为STATUS_INIT
        self.video_status = self.STATUS_INIT
        # 进度条关闭
        self.slider_thread.stop()
        # 实时流保证30fps/s即可
        self.timer_video.frequent = 30
        self.setCursor(Qt.ArrowCursor)
        self.status_video_button.setEnabled(False)
        self.last_video_button.setEnabled(False)
        self.next_video_button.setEnabled(False)
        self.last_frame_button.setEnabled(False)
        self.next_frame_button.setEnabled(False)
        self.video_progress_bar.setEnabled(False)
        # 进度条设置
        self.video_progress_bar.setValue(0)
        # 帧率显示置空
        self.label_frame_show.setText('')
        # 去掉视频title
        self.label_video_title.setText('')
        # 复位背景图
        self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
        self.status_video_button.setToolTip(self.video_status_play_tip)
        self.camera_status = self.camera_closed
        # 需要获取gif图的尺寸
        self.local_video_width = self.data_process_background_size[0]
        self.local_video_height = self.data_process_background_size[1]
        # 调整视频尺寸
        self.signal.emit('reset_video_label_size>local_video')
        # 铺设背景图
        self.setPixmap(QPixmap(IconPath.data_is_ready_file))

    # 运行数据处理的时候需要进行的操作
    def data_process_execute(self):
        # 此时什么都不播放(状态为None)
        self.video_play_flag = None
        # 复位视频状态为STATUS_INIT
        self.video_status = self.STATUS_INIT
        # 进度条关闭
        self.slider_thread.stop()
        # 关掉数据处理标志位
        GloVar.data_process_flag = False
        # 实时流保证30fps/s即可
        self.timer_video.frequent = 30
        self.setCursor(Qt.ArrowCursor)
        self.last_video_button.setEnabled(False)
        self.next_video_button.setEnabled(False)
        self.status_video_button.setEnabled(False)
        self.last_frame_button.setEnabled(False)
        self.next_frame_button.setEnabled(False)
        # 进度条设置
        self.video_progress_bar.setValue(0)
        self.label_frame_show.setText('')
        self.video_progress_bar.setEnabled(False)
        # 去掉视频title
        self.label_video_title.setText('')
        # 复位背景图
        self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
        self.status_video_button.setToolTip(self.video_status_play_tip)
        self.camera_status = self.camera_closed
        # 需要获取gif图的尺寸
        self.local_video_width = self.data_process_background_size[0]
        self.local_video_height = self.data_process_background_size[1]
        # 调整视频尺寸
        self.signal.emit('reset_video_label_size>local_video')
        # 播放正在进行数据处理的gif图
        self.setMovie(self.data_processing_gif)
        self.data_processing_gif.start()

    def data_process_finished(self):
        # 停掉gif动图
        self.data_processing_gif.stop()
        # 此时什么都不播放(状态为None)
        self.video_play_flag = None
        # 进度条设置
        self.video_progress_bar.setValue(0)
        self.slider_thread.stop()
        time.sleep(0.3)
        # 复位视频状态为STATUS_INIT
        self.video_status = self.STATUS_INIT
        # 实时流保证30fps/s即可
        self.timer_video.frequent = 30
        # 关掉数据处理标志位
        GloVar.data_process_flag = False
        self.setCursor(Qt.ArrowCursor)
        self.status_video_button.setEnabled(False)
        self.last_video_button.setEnabled(False)
        self.next_video_button.setEnabled(False)
        self.last_frame_button.setEnabled(False)
        self.next_frame_button.setEnabled(False)
        self.video_progress_bar.setEnabled(False)
        # /这块显示有问题--需要接着看/
        # 复位背景图
        self.status_video_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_player_play + ')}')
        self.status_video_button.setToolTip(self.video_status_play_tip)
        self.camera_status = self.camera_closed
        # 帧率显示置空
        self.label_frame_show.setText('')
        # 去掉视频title
        self.label_video_title.setText('')
        # 需要获取gif图的尺寸
        self.local_video_width = self.data_process_background_size[0]
        self.local_video_height = self.data_process_background_size[1]
        # 调整视频尺寸
        self.signal.emit('reset_video_label_size>local_video')
        # 铺设背景图
        self.setPixmap(QPixmap(IconPath.data_process_finished_file))

    # 返回视频title
    def set_video_title(self, current_video, videos, videos_title):
        videos_num = len(videos)
        if videos_num > 1:
            self.video_title_serial_show = '[' + str(current_video + 1) + '/' + str(videos_num) + ']'
        else:
            self.video_title_serial_show = ''
        video_title = self.video_title_serial_show + videos_title[current_video]
        return video_title

    # 鼠标点击事件
    def mousePressEvent(self, event):
        self.mouse_press_flag = True
        self.x0 = event.x()
        self.y0 = event.y()
        self.x0 = self.x0
        self.y1 = self.y0

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if self.mouse_move_flag is True:
            # 如果框选屏幕大小(返回框选的尺寸信息)
            if GloVar.box_screen_flag is True:
                # 框选的车机屏幕大小
                self.box_screen_size[0] = self.x0
                self.box_screen_size[1] = self.y0
                self.box_screen_size[2] = abs(self.x1-self.x0)
                self.box_screen_size[3] = abs(self.y1-self.y0)
                # 起点和终点所占video_label比例
                self.box_screen_scale[0] = round(float(self.x0/self.size().width()),  6)
                self.box_screen_scale[1] = round(float(self.y0/self.size().height()), 6)
                self.box_screen_scale[2] = round(float(self.x1/self.size().width()),  6)
                self.box_screen_scale[3] = round(float(self.y1/self.size().height()), 6)
                # 将box_screen_scale尺寸存入配置文件(不需要每次打开都进行框选)
                Profile(type='write', file=GloVar.config_file_path, section='param', option='box_screen_scale', value=str(self.box_screen_scale))
                GloVar.box_screen_flag = False
                GloVar.select_template_flag = False
                GloVar.add_action_button_flag = True
                self.setCursor(Qt.ArrowCursor)
                Logger('[框选车机屏幕]--起点及尺寸: %s' % str(self.box_screen_size))
            # 如果是机械臂滑动动作
            elif RobotArmAction.uArm_action_type == RobotArmAction.uArm_slide:
                start = self.calculating_point(self.x0, self.y0)
                end   = self.calculating_point(self.x1, self.y1)
                position = start + end
                info_list = [RobotArmAction.uArm_slide, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
            # 其余情况判断是否暂停(若有暂停, 则可以进行模板框选)
            else:
                self.save_template()
        else:
            if RobotArmAction.uArm_action_type == RobotArmAction.uArm_click:
                position = self.calculating_point(self.x0, self.y0)
                info_list = [RobotArmAction.uArm_click, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
            elif RobotArmAction.uArm_action_type == RobotArmAction.uArm_double_click:
                position = self.calculating_point(self.x0, self.y0)
                info_list = [RobotArmAction.uArm_double_click, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
            elif RobotArmAction.uArm_action_type == RobotArmAction.uArm_long_click:
                position = self.calculating_point(self.x0, self.y0)
                info_list = [RobotArmAction.uArm_long_click, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
        self.mouse_press_flag = False
        self.mouse_move_flag = False

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.mouse_press_flag is True:
            self.mouse_move_flag = True
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        # 滑动动作直线显示
        if RobotArmAction.uArm_action_type == RobotArmAction.uArm_slide:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
            painter.drawLine(QPoint(self.x0, self.y0), QPoint(self.x1, self.y1))
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2], self.box_screen_size[3]))
        # 点击动作画圆显示
        elif RobotArmAction.uArm_action_type in [RobotArmAction.uArm_click, RobotArmAction.uArm_long_click, RobotArmAction.uArm_double_click]:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
            painter.drawEllipse(self.x0-5, self.y0-5, 10, 10)
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2], self.box_screen_size[3]))
        # 框选动作
        elif GloVar.select_template_flag is True:
            rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(rect)
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2], self.box_screen_size[3]))
        # 其余情况(不绘制图, 一个小点,几乎不能看到)
        else:
            point = [QPoint(self.x0, self.y0)]
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
            painter.drawPoints(QPolygon(point))
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2], self.box_screen_size[3]))

    # 保存模板
    def save_template(self):
        if GloVar.select_template_flag is True:
            # x_unit, y_unit = 1280 / 1280, 1024 / 1024
            x_unit, y_unit = self.x_unit, self.y_unit
            x0, y0, x1, y1 = int(self.x0 * x_unit), int(self.y0 * y_unit), int(self.x1 * x_unit), int(self.y1 * y_unit)
            cut_img = self.mask_image[y0:y1, x0:x1]
            # 直播状态
            if self.video_play_flag is False:
                # 如果是case中框选视频模板动作
                if GloVar.draw_frame_flag == GloVar.result_template:
                    # 接收模板路径
                    mask_path = GloVar.mask_path
                    # default_name = 'type-name'
                    default_name = RecordAction.current_video_type + '/' + RecordAction.current_video_name
                elif GloVar.draw_frame_flag == GloVar.assert_template:
                    mask_path = GloVar.mask_path
                    # 获取断言模板图片名字
                    default_name = GloVar.assert_template
                else:
                    # 接收模板路径
                    mask_path = GloVar.mask_path
                    default_name = '截图'
            # 本地视频播放
            elif self.video_play_flag is True:
                # 数据处理产生的模板
                if GloVar.data_process_flag is True:
                    mask_path = os.path.split(GloVar.mask_path)[0]
                    default_name = os.path.split(GloVar.mask_path)[1]
                # 离线视频产生的模板
                else:
                    mask_path = GloVar.mask_path
                    default_name = '截图'
            else:
                Logger('[当前状态不允许保存模板!]')
                return
            # 如果模板路径为None(说明不允许框选模板)
            if mask_path is not None:
                # value, ok = QInputDialog.getText(self, '标注输入框', '请输入文本', QLineEdit.Normal, '应用')
                value, ok = QInputDialog.getText(self, '标注输入框', '请输入文本', QLineEdit.Normal, default_name)
                # 如果输入有效值
                if ok:
                    # 如果是数据处理(需要对图像特殊处理)
                    if GloVar.data_process_flag is True:
                        # 将模板灰度化/并在模板起始位置打标记
                        rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                        # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置, 每一列前四个像素分别代表 千/百/十/个 位)
                        # rect_image[0][0] = y0 // 10
                        # rect_image[0][1] = y1 // 10
                        # rect_image[0][2] = x0 // 10
                        # rect_image[0][3] = x1 // 10
                        rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                        rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                        rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                        rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                        cut_img = rect_image
                        # 模板存放位置
                        mask_path = mask_path
                        if os.path.exists(mask_path) is False:
                            os.makedirs(mask_path)
                        template_name = MergePath([mask_path, value + '.bmp']).merged_path
                        cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                    # 非数据处理情况
                    else:
                        # 如果输入的参数中带有'-'代表需要分级保存, 并需要新建文件夹
                        if '/' in value:
                            # 直播时的情况
                            if self.video_play_flag is False:
                                folder_layer_count = len(value.split('/')) - 1
                                if folder_layer_count == 1:
                                    mask_path = MergePath([mask_path, value.split('/')[0]]).merged_path
                                elif folder_layer_count == 2:
                                    mask_path = MergePath([mask_path, value.split('/')[0], value.split('/')[1]]).merged_path
                                else:
                                    Logger('[输入的模板名称错误!]')
                                    return
                                if os.path.exists(mask_path) is False:
                                    os.makedirs(mask_path)
                                # 如果是框选数据匹配模板的话(框选模板保存为灰度图)
                                if GloVar.draw_frame_flag == GloVar.result_template:
                                    # 将模板灰度化/并在模板起始位置打标记
                                    rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                    # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                    # rect_image[0][0] = y0 // 10
                                    # rect_image[0][1] = y1 // 10
                                    # rect_image[0][2] = x0 // 10
                                    # rect_image[0][3] = x1 // 10
                                    rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                    rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                    cut_img = rect_image
                                    template_name = MergePath([mask_path, value.split('/')[-1] + '.bmp']).merged_path
                                    cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                    # 视频动作中模板框选完成
                                    self.signal.emit(GloVar.result_template_finished + '>' + template_name)
                                # 断言模板
                                elif GloVar.draw_frame_flag == GloVar.assert_template:
                                    # 将模板灰度化/并在模板起始位置打标记
                                    rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                    # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                    rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                    rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                    cut_img = rect_image
                                    template_name = MergePath([mask_path, RecordAction.current_video_name, default_name, value + '.bmp']).merged_path
                                    cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                    # 视频动作中模板框选完成
                                    self.signal.emit(GloVar.assert_template_finished + '>' + template_name)
                                else:
                                    template_name = MergePath([mask_path, value.split('/')[-1] + '.jpg']).merged_path
                                    cv2.imencode('.jpg', cut_img)[1].tofile(template_name)
                            # 本地视频播放的情况下
                            elif self.video_play_flag is True:
                                template_name = 'null'
                                Logger('[输入的模板名称错误!]')
                            # 其余情况(不播放视频)
                            else:
                                template_name = 'null'
                                Logger('[此时状态不应该有模板输入!]')
                        # 如果输入的参数中不带有'-', 则图片正常保存即可
                        else:
                            # 直播
                            if self.video_play_flag is False:
                                mask_path = MergePath([mask_path]).merged_path
                            # 本地视频播放
                            elif self.video_play_flag is True:
                                mask_path = mask_path
                            # 其余情况(不播放视频)
                            else:
                                mask_path = mask_path
                            if os.path.exists(mask_path) is False:
                                os.makedirs(mask_path)
                            # 如果是框选数据匹配模板的话(框选模板保存为灰度图)
                            if GloVar.draw_frame_flag == GloVar.result_template:
                                # 将模板灰度化/并在模板起始位置打标记
                                rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                cut_img = rect_image
                                template_name = MergePath([mask_path, value.split('/')[-1] + '.bmp']).merged_path
                                cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                # 视频动作中模板框选完成
                                self.signal.emit(GloVar.result_template_finished + '>' + template_name)
                            # 断言模板
                            elif GloVar.draw_frame_flag == GloVar.assert_template:
                                # 将模板灰度化/并在模板起始位置打标记
                                rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                cut_img = rect_image
                                template_name = MergePath([mask_path, value + '.bmp']).merged_path
                                cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                # 视频动作中模板框选完成
                                self.signal.emit(GloVar.assert_template_finished + '>' + template_name)
                            else:
                                template_name = MergePath([mask_path, value + '.jpg']).merged_path
                                cv2.imencode('.jpg', cut_img)[1].tofile(template_name)
                    # case中框选模板标志位复位
                    GloVar.draw_frame_flag = GloVar.other_template
                    Logger('[框选的模板保存路径为]: %s' % template_name)
                else:
                    Logger('[框选动作取消!]')
            # 保存完图片后, 让红色框消失
            self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0

    # 在模板图片中的前4行4列写入位置信息(roi图片/column列数,从0-3/num坐标信息)
    def write_position_info_to_roi(self, roi, column, num):
        num_length = len(str(num))
        if num_length == 4:
            str_num = str(num)
        elif num_length == 3:
            str_num = str(0) + str(num)
        elif num_length == 2:
            str_num = str(00) + str(num)
        elif num_length == 1:
            str_num = str(000) + str(num)
        else:
            str_num = '1234'
        position_info = [int(list(str_num)[0]), int(list(str_num)[1]), int(list(str_num)[2]), int(list(str_num)[3])]
        roi[0][column] = position_info[0]
        roi[1][column] = position_info[1]
        roi[2][column] = position_info[2]
        roi[3][column] = position_info[3]
        return roi

    # 计算传入机械臂的坐标
    def calculating_point(self, x, y):
        i = x - self.box_screen_size[0]
        robot_y_offset = round((i / self.box_screen_size[2] * RobotArmParam.actual_screen_width), 3)
        j = y - (self.box_screen_size[1] + self.box_screen_size[3])
        robot_x_offset = round((j / self.box_screen_size[3] * RobotArmParam.actual_screen_height), 3)
        return robot_x_offset, robot_y_offset


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = VideoLabel(None)
    gui.show()
    sys.exit(app.exec_())