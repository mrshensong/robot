import os
import sys
import cv2
import time
import json
import requests
import datetime
import gxipy as gx
import numpy as np
from threading import Thread
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from uiclass.stream import Stream
from uiclass.timer import Timer
from uiclass.video_label import Video_Label
from uiclass.show_tab_widget import ShowTabWidget
from uiclass.controls import CameraParamAdjustControl
from GlobalVar import gloVar, icon_path, uArm_action, uArm_param, logger, robot_other, add_action_window, merge_path, window_status, profile, record_action, sleep_action


class UiMainWindow(QMainWindow):
    # 视频状态(初始化/播放中/暂停/播放完毕)
    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2
    STATUS_STOP = 3
    # 相机状态
    camera_opened = 'OPENED'
    camera_closed = 'CLOSED'
    # 字体 'Microsoft YaHei'
    font = 'Times New Roman'
    # icon文件
    icon_file = icon_path.Icon_file
    # background文件
    background_file = icon_path.background_file


    def setupUi(self):
        # 初始化参数
        self.init_param()
        # 使用自定义定时器
        self.timer_video = Timer()
        self.timer_video.timeSignal[str].connect(self.show_video)
        # 显示窗口状态栏
        self.timer_window_status = Timer(frequent=3)
        self.timer_window_status.timeSignal[str].connect(self.show_window_status)
        self.timer_window_status.start()
        # 视频进度条
        self.slider_thread = Timer(frequent=4)
        self.slider_thread.timeSignal[str].connect(self.slider_refresh)
        # 使用自带定时器
        # self.timer_video = QTimer(self)
        # self.timer_video.timeout.connect(self.show_video)
        # self.timer_video.start(1)

        self.setObjectName("MainWindow")
        self.setGeometry(0, 0, 1000, 600)
        self.setMinimumSize(QtCore.QSize(1000, 600))
        self.setWindowTitle("Auto Robot")
        self.setWindowIcon(QIcon(self.icon_file))

        self.central_widget = QWidget(self)

        self.central_widget.setObjectName("central_widget")
        self.grid = QtWidgets.QGridLayout(self.central_widget)
        # self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setObjectName('grid')
        ## 定义UI 字体 和 字号大小
        self.setFont(QFont(self.font, 13))
        # 设置UI背景颜色为灰色
        # self.central_widget.setStyleSheet('background-color:lightgrey')

        # 视频播放框架
        self.video_play_frame()
        # case展示
        self.show_case()
        # 控制台输出框架
        self.output_text()

        self.setCentralWidget(self.central_widget)
        # 菜单栏
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_bar.setObjectName('menu_bar')
        self.setMenuBar(self.menu_bar)
        # 状态栏 & 状态栏显示
        self.status_bar = QtWidgets.QStatusBar(self)
        self.status_bar.setObjectName('status_bar')
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.window_status_text)
        self.status_bar.setStyleSheet('color:green')
        self.status_bar.setFont(QFont(self.font, 13))
        # 工具栏
        self.ui_toolbar = self.addToolBar('ui_toolbar')
        self.robot_operate_toolbar = self.addToolBar('operate_toolbar')
        self.video_play_toolbar = self.addToolBar('video_play_toolbar')
        # 视频实时流参数设置框
        self.camera_param_setting_widget = CameraParamAdjustControl(self)

        # 网上百度到的说明:其作用是如其名称一样，用来将QObject 里的子孙QObject的某些信号按照其objectName连接到相应的槽上
        # 如 button_hello.setObjectName("hello_button")
        QtCore.QMetaObject.connectSlotsByName(self)
        # 接收进程打印的信息
        sys.stdout = Stream(newText=self.update_text)
        sys.stderr = Stream(newText=self.update_text)
        # 菜单栏
        self.menu_bar_show()
        # 工具栏
        self.tool_bar()
        # 打开python_service
        # Thread(target=self.open_python_server, args=()).start()
        # 获取python_server的pid
        # Thread(target=self.get_python_server_pid, args=()).start()


    # 所有参数初始化
    def init_param(self):
        # 保存的case执行完的视频
        self.videos = []
        # 保存的视频中case类型和视频名字
        self.videos_title = []
        # 录播相关参数
        self.video_cap = None # 当前视频对象
        self.get_path = None # 获取到的视频根目录
        self.video_play_flag = False  # False直播/True录播
        self.current_video = 0  # 当前视频所在序列号(第0个视频)
        self.current_frame = 0  # 当前帧数
        self.frame_count = 0  # 总帧数
        # 滑动条标志位(如果有滑动动作标志为True, 否则为False)
        self.slider_flag = False
        # 放置视频标签的尺寸
        self.video_label_size_width = 0
        self.video_label_size_height = 0
        # 视频流&视频尺寸
        self.real_time_video_width = 1280
        self.real_time_video_height = 720
        # self.real_time_video_width = 1920
        # self.real_time_video_height = 1280
        self.offline_video_width = 0
        self.offline_video_height = 0
        # 是否第一次窗口缩放
        self.first_window_zoom_flag = True
        # 是否使用电脑自带摄像头
        self.use_system_camera = True
        self.camera_status = self.camera_closed
        # 初始化播放状态
        self.video_status = self.STATUS_INIT
        # 当前图像帧
        self.image = None
        # 获取截图保存路径
        self.picture_path = profile(type='read', file=gloVar.config_file_path, section='param', option='picture_path').path
        # 视频所在的路径
        self.videos_path = profile(type='read', file=gloVar.config_file_path, section='param', option='videos_path').path
        # 窗口状态栏显示的固定格式
        self.window_status_text = '机械臂:[%s];    视频帧率:[%s];    action_tab页面:[%s];    case_tab页面:[%s]'\
                                  % (window_status.robot_connect_status, window_status.video_frame_rate,
                                    window_status.action_tab_status, window_status.case_tab_status)
        # 今天的日期(用作文件夹名)
        self.today_data = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # 获取当前路径(连接符标准化为正斜杠模式)
        gloVar.project_path = merge_path(section_path=[os.path.abspath(os.getcwd())]).merged_path
        gloVar.project_video_path = merge_path(section_path=[os.path.abspath(os.getcwd()), 'video', self.today_data]).merged_path
        # python_server的pid
        self.python_server_pid = None


    # 打开python服务
    def open_python_server(self):
        os.system('python pythonservice/manage.py runserver')


    # 获取8000端口pid
    def get_python_server_pid(self):
        while True:
            result = os.popen('netstat -aon | findstr 8000').readlines()
            if '127.0.0.1:8000' in ''.join(result):
                for line in result:
                    if '127.0.0.1:8000' in line:
                        self.python_server_pid = line.split('LISTENING')[1].split('\n')[0].strip()
                        break
                break
            else:
                time.sleep(0.5)


    # 展示窗口状态栏
    def show_window_status(self):
        self.window_status_text = '机械臂:[%s];    视频帧率:[%s];    action_tab页面:[%s];    case_tab页面:[%s]' \
                                  % (window_status.robot_connect_status, window_status.video_frame_rate,
                                     window_status.action_tab_status, window_status.case_tab_status)
        self.status_bar.showMessage(self.window_status_text)


    # 视频流
    def video_stream(self):
        if self.use_system_camera is True:
            Thread(target=self.system_camera_stream, args=()).start()
        else:
            Thread(target=self.external_camera_stream, args=()).start()


    # 切换摄像头状态
    def switch_camera_status(self):
        self.label_video.setCursor(Qt.ArrowCursor)
        self.last_video_button.setEnabled(False)
        self.next_video_button.setEnabled(False)
        self.last_frame_button.setEnabled(False)
        self.next_frame_button.setEnabled(False)
        if self.camera_status == self.camera_closed:
            # 不管离线视频是否正在播放(先关掉视频, 再切换到直播)
            self.timer_video.stop()
            self.label_video.video_play_flag = self.video_play_flag = False
            self.label_video_title.setText('[实时视频流]')
            self.video_progress_bar.setValue(0)
            self.label_frame_show.setText('')
            self.video_progress_bar.setEnabled(False)
            robot_other.select_template_flag = False
            # 离线视频进度条关闭
            self.slider_thread.stop()
            # 打开实时流视频并播放
            logger('<打开摄像头>')
            self.camera_status = self.camera_opened
            self.video_stream()
            self.switch_camera_status_action.setIcon(QIcon(icon_path.Icon_ui_close_camera))
            # 设置提示
            self.switch_camera_status_action.setToolTip('close_camera')
            time.sleep(3)
            # time.sleep(15)
            # 打开视频展示定时器
            self.timer_video.start()
            self.video_status = self.STATUS_PLAYING
            self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_pause + ')')
            self.status_video_button.setEnabled(True)
            # 让show_tab_widget可以操作
            self.show_tab_widget.setEnabled(True)
            # 通过在线视频尺寸自适应视频播放窗口
            self.video_label_adaptive(self.real_time_video_width, self.real_time_video_height)
        else:
            logger('<关闭摄像头>')
            # 关闭视频展示定时器
            self.timer_video.stop()
            self.video_status = self.STATUS_INIT
            robot_other.select_template_flag = False
            # 离线视频进度条打开
            self.slider_thread.start()
            self.label_video.setCursor(Qt.ArrowCursor)
            self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
            self.camera_status = self.camera_closed
            self.switch_camera_status_action.setIcon(QIcon(icon_path.Icon_ui_open_camera))
            self.switch_camera_status_action.setToolTip('open_camera')
            self.label_video.setPixmap(QtGui.QPixmap(self.background_file))
            self.status_video_button.setEnabled(False)


    # 系统摄像头流
    def system_camera_stream(self):
        # 使用电脑自带摄像头
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.real_time_video_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.real_time_video_height)
        # 使用罗技摄像头
        # cap = cv2.VideoCapture(1)
        while self.camera_status == self.camera_opened:
            _, frame = cap.read()
            self.image = frame.copy()
        cap.release()


    # 外接摄像头
    def external_camera_stream(self):
        # create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num is 0:
            print("Number of enumerated devices is 0")
            return
        # open device by serial number
        cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))
        # if camera is mono
        if cam.PixelColorFilter.is_implemented() is False:
            print("This sample does not support mono camera.")
            cam.close_device()
            return
        # set continuous acquisition
        cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        # set exposure(曝光)
        cam.ExposureTime.set(10000.0)
        # set gain(增益)
        cam.Gain.set(10.0)
        # set roi(ROI)
        cam.Width.set(self.real_time_video_width)
        cam.Height.set(self.real_time_video_height)
        cam.OffsetX.set(int((1200-self.real_time_video_height)/2))
        cam.OffsetY.set(int((1920-self.real_time_video_width)/2))
        # 自动白平衡
        cam.BalanceWhiteAuto.set(True)
        # set param of improving image quality
        if cam.GammaParam.is_readable():
            gamma_value = cam.GammaParam.get()
            gamma_lut = gx.Utility.get_gamma_lut(gamma_value)
        else:
            gamma_lut = None
        if cam.ContrastParam.is_readable():
            contrast_value = cam.ContrastParam.get()
            contrast_lut = gx.Utility.get_contrast_lut(contrast_value)
        else:
            contrast_lut = None
        color_correction_param = cam.ColorCorrectionParam.get()
        # start data acquisition
        cam.stream_on()
        # acquisition image: num is the image number
        while self.camera_status == self.camera_opened:
            # get raw image
            raw_image = cam.data_stream[0].get_image()
            if raw_image is None:
                print("Getting image failed.")
                continue
            # get RGB image from raw image
            rgb_image = raw_image.convert("RGB")
            if rgb_image is None:
                continue
            # improve image quality
            rgb_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)
            # create numpy array with data from raw image
            numpy_image = rgb_image.get_numpy_array()
            if numpy_image is None:
                continue
            # 将图片格式转换为cv模式
            numpy_image = cv2.cvtColor(np.asarray(numpy_image), cv2.COLOR_RGB2BGR)
            self.image = numpy_image.copy()
            # print height, width, and frame ID of the acquisition image
            # print("Frame ID: %d   Height: %d   Width: %d" % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))
        # stop data acquisition
        cam.stream_off()
        # close device
        cam.close_device()


    # 拍照/截屏 动作
    def screen_shot(self):
        # 视频流未打开时不允许拍照
        if self.camera_status == self.camera_closed:
            QMessageBox.warning(self, "警告", "还没有开启视频流! 请打开视频流!", QMessageBox.Yes | QMessageBox.No)
        else:
            Thread(target=self.screen_capture_thread, args=()).start()


    # 摄像头截屏线程
    def screen_capture_thread(self, capture_type='jpg'):
        capture_path = merge_path([self.picture_path, 'screen_shot']).merged_path
        if os.path.exists(capture_path) is False:
            os.makedirs(capture_path)
        capture_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + '.' + capture_type
        capture_name = merge_path([capture_path, capture_name]).merged_path
        cv2.imencode('.' + capture_type, self.image.copy())[1].tofile(capture_name)
        logger('[截取的图片为]: %s' %capture_name)


    # 框选车机屏幕大小
    def box_screen(self):
        # 视频流未打开时不允许框选车机屏幕
        if self.camera_status == self.camera_closed:
            QMessageBox.warning(self, "警告", "请先打开视频流! 之后再框选屏幕!", QMessageBox.Yes | QMessageBox.No)
        else:
            reply = QMessageBox.question(self, '提示', '是否要框选车机屏幕?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                # 清除上次无关的鼠标操作产生的起止点
                self.label_video.x1, self.label_video.x1 = self.label_video.x0, self.label_video.y0
                self.label_video.setCursor(Qt.CrossCursor)
                robot_other.select_template_flag = True
                gloVar.box_screen_flag = True
                uArm_action.uArm_action_type = None


    # 更新控制台内容
    def update_text(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()


    # 菜单栏
    def menu_bar_show(self):
        # 菜单栏显示
        self.test_action = QAction('exit', self)
        self.file_bar = self.menu_bar.addMenu('File')
        self.file_bar.addAction(self.test_action)


    # 机械臂动作事件
    def uArm_action_event(self, action):
        if sum(self.label_video.box_screen_size) == 0:
            QMessageBox.about(self, "提示", "请先框选屏幕大小")
            return
        else:
            Thread(target=self.uArm_action_event_thread, args=(action,)).start()


    # 正在进行的操作是否需要录入脚本(默认参数为None; 当有参数时, 将record_status的状态传给uArm_action.uArm_with_record)
    def switch_uArm_with_record_status(self, record_status=None):
        if record_status is not None:
            uArm_action.uArm_with_record = bool(1-record_status)
        if uArm_action.uArm_with_record is False:
            uArm_action.uArm_with_record = True
            self.robot_with_record_action.setIcon(QIcon(icon_path.Icon_robot_without_record))
            self.robot_with_record_action.setToolTip('without_record')
            logger('<脚本录制打开--以下操作将会被保存为action>')
        else:
            uArm_action.uArm_with_record = False
            self.robot_with_record_action.setIcon(QIcon(icon_path.Icon_robot_with_record))
            self.robot_with_record_action.setToolTip('with_record')
            logger('<脚本录制关闭--以下操作将不会被保存为action>')


    # 离线视频播放
    def play_exist_video(self):
        camera_opened_flag = False # 在选择视频的时候判断此时实时流是否开启, 如果为True说明开启着, 如果False说明关闭着
        # 按下选择视频按钮, 判断当前视频流是否开启, 若开启着, 则先停止视频流/再判断是否有选择目录(没有选择目录的话, 再次恢复开启实时流状态)
        # 停止视频流, 并切换视频流按钮(打开/关闭视频流)状态
        if self.camera_status == self.camera_opened:
            camera_opened_flag = True
            self.switch_camera_status()
        self.get_path = QFileDialog.getExistingDirectory(self, '选择文件夹', self.videos_path)
        if self.get_path:
            if self.videos_path != self.get_path:
                # 保存此次打开的路径(路径默认上一次)
                self.videos_path = self.get_path
                profile(type='write', file=gloVar.config_file_path, section='param', option='videos_path', value=self.get_path)
            uArm_action.uArm_action_type = None
            self.label_video.x0, self.label_video.y0 = self.label_video.x1, self.label_video.y1
            self.videos, self.videos_title = [], []
            self.current_frame, self.current_video, self.frame_count = 0, 0, 0
            for home, dirs, files in os.walk(self.get_path):
                for file in files:
                    # 判断视频文件(通过后缀名)
                    (file_text, extension) = os.path.splitext(file)
                    if extension in ['.mp4', '.MP4', '.avi', '.AVI']:
                        # 文件名列表, 包含完整路径
                        file = merge_path([home, file]).merged_path
                        # 视频title(显示路径分割后的最后两段)/路径太短的话(全部显示)
                        if len(file.split('/')) > 3:
                            file_name = merge_path(file.split('/')[-2:]).merged_path
                        else:
                            file_name = file
                        self.videos.append(file)
                        self.videos_title.append(file_name)
            # 加载离线视频对象
            self.video_cap = cv2.VideoCapture(self.videos[0]) # 重新加载这个视频
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # 需要获取视频尺寸
            self.offline_video_width  = int(self.video_cap.get(3))
            self.offline_video_height = int(self.video_cap.get(4))
            # 获取视频总帧数
            self.frame_count          = int(self.video_cap.get(7))
            # 更换视频标签背景
            self.label_video.setPixmap(QtGui.QPixmap(self.background_file))
            # 离线视频播放标志打开, 视频状态为STATUS_INIT
            self.label_video.video_play_flag = self.video_play_flag = True
            self.video_status = self.STATUS_INIT
            self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
            # 设置视频title
            self.label_video_title.setText('['+str(self.current_video+1)+'/'+str(len(self.videos))+']'+self.videos_title[self.current_video])
            self.label_video_title.setStyleSheet('color:white')
            # 获取第一帧
            _, self.image = self.video_cap.read()
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
            # 设置帧数显示
            self.label_frame_show.setText(str(self.current_frame+1) + 'F/' + str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            # 使能视频(播放/暂停/重播)按钮和视频进度条
            self.status_video_button.setEnabled(True)
            self.video_progress_bar.setEnabled(True)
            self.last_video_button.setEnabled(True)
            self.next_video_button.setEnabled(True)
            self.last_frame_button.setEnabled(True)
            self.next_frame_button.setEnabled(True)
            self.video_progress_bar.setRange(0, self.frame_count-1)
            # 让show_tab_widget不可以操作
            self.show_tab_widget.setEnabled(False)
            # 强制关闭脚本录制状态
            self.switch_uArm_with_record_status(record_status=False)
            # 通过离线视频尺寸自适应视频播放窗口
            self.video_label_adaptive(self.offline_video_width, self.offline_video_height)
        else:
            logger('没有选择视频路径!')
            if camera_opened_flag is True:
                self.switch_camera_status()


    # 机械臂动作线程
    def uArm_action_event_thread(self, action):
        if action == uArm_action.uArm_click:
            # 单击标志
            uArm_action.uArm_action_type = uArm_action.uArm_click
        elif action == uArm_action.uArm_double_click:
            # 双击标志
            uArm_action.uArm_action_type = uArm_action.uArm_double_click
        elif action == uArm_action.uArm_long_click:
            # 长按标志
            uArm_action.uArm_action_type = uArm_action.uArm_long_click
        elif action == uArm_action.uArm_slide:
            # 滑动标志(避免出现乱画直线的情况)
            self.label_video.x1, self.label_video.y1 = self.label_video.x0, self.label_video.y0
            uArm_action.uArm_action_type = uArm_action.uArm_slide
        elif action == uArm_action.uArm_lock:
            # 机械臂锁定
            response = self.uArm_get_request(uArm_action.uArm_lock)
            logger(response)
        elif action == uArm_action.uArm_unlock:
            # 机械臂解锁
            response = self.uArm_get_request(uArm_action.uArm_unlock)
            logger(response)
        elif action == uArm_action.uArm_get_position:
            # 获取机械臂当前坐标
            response = self.uArm_get_request(uArm_action.uArm_get_position)
            uArm_param.base_x_point = float(response.split(',')[0])
            uArm_param.base_y_point = float(response.split(',')[1])
            uArm_param.base_z_point = float(response.split(',')[2])
            logger('当前位置为: %s' % response)
        else:
            logger('当前不支持[%s]这个动作' % action)


    # get请求->机械臂相关操作函数(解锁/上锁/获取坐标)
    def uArm_get_request(self, action):
        try:
            response = requests.get(uArm_param.port_address + 'uArm/' + str(action))
            gloVar.request_status = response.text
        except TimeoutError:
            gloVar.request_status = '机械臂服务连接异常'
        finally:
            return gloVar.request_status


    # post请求->机械臂命令(单击/双击/长按/滑动)
    def uArm_post_request(self, type, action, data_dict):
        try:
            response = requests.post(url=uArm_param.port_address + str(type) +'/' + str(action), data=json.dumps(data_dict))
            gloVar.request_status = response.text
        except TimeoutError:
            gloVar.request_status = '机械臂服务连接异常'
        finally:
            return gloVar.request_status


    # 获取picture路径
    def get_picture_path(self):
        self.picture_path = QtWidgets.QFileDialog.getExistingDirectory(self.central_widget, "浏览", self.picture_path)
        self.set_config_value(gloVar.config_file_path, 'param', 'picture_path', self.picture_path)
        logger('修改保存图片路径为: %s' % self.picture_path)


    # 设置相机参数
    def set_camera_param(self):
        self.camera_param_setting_widget.show()
        self.camera_param_setting_widget.exec()


    def tool_bar(self):
        # ui相关action
        self.setting_action               = QAction(QIcon(icon_path.Icon_ui_setting), 'setting', self)
        self.switch_camera_status_action  = QAction(QIcon(icon_path.Icon_ui_open_camera), 'open_camera', self)
        self.capture_action               = QAction(QIcon(icon_path.Icon_ui_capture), 'capture', self)
        self.box_screen_action            = QAction(QIcon(icon_path.Icon_ui_box_screen), 'box_screen', self)
        self.picture_path_action          = QAction(QIcon(icon_path.Icon_ui_folder_go), 'picture_path', self)
        # 绑定触发函数
        self.switch_camera_status_action.triggered.connect(self.switch_camera_status)
        self.capture_action.triggered.connect(self.screen_shot)
        self.box_screen_action.triggered.connect(self.box_screen)
        self.picture_path_action.triggered.connect(self.get_picture_path)
        self.setting_action.triggered.connect(self.set_camera_param)
        # robot相关action
        self.click_action        = QAction(QIcon(icon_path.Icon_robot_click), 'click', self)
        self.double_click_action = QAction(QIcon(icon_path.Icon_robot_double_click), 'double_click', self)
        self.long_click_action   = QAction(QIcon(icon_path.Icon_robot_long_click), 'long_click', self)
        self.slide_action        = QAction(QIcon(icon_path.Icon_robot_slide), 'slide', self)
        self.robot_lock_action   = QAction(QIcon(icon_path.Icon_robot_lock), 'lock', self)
        self.robot_unlock_action = QAction(QIcon(icon_path.Icon_robot_unlock), 'unlock', self)
        self.robot_get_position_action = QAction(QIcon(icon_path.Icon_robot_get_position), 'get_position', self)
        self.robot_with_record_action = QAction(QIcon(icon_path.Icon_robot_with_record), 'with_record', self)
        # 绑定触发函数
        self.click_action.triggered.connect(lambda: self.uArm_action_event(uArm_action.uArm_click))
        self.double_click_action.triggered.connect(lambda: self.uArm_action_event(uArm_action.uArm_double_click))
        self.long_click_action.triggered.connect(lambda: self.uArm_action_event(uArm_action.uArm_long_click))
        self.slide_action.triggered.connect(lambda: self.uArm_action_event(uArm_action.uArm_slide))
        self.robot_lock_action.triggered.connect(lambda: self.uArm_action_event(uArm_action.uArm_lock))
        self.robot_unlock_action.triggered.connect(lambda: self.uArm_action_event(uArm_action.uArm_unlock))
        self.robot_get_position_action.triggered.connect(lambda: self.uArm_action_event(uArm_action.uArm_get_position))
        self.robot_with_record_action.triggered.connect(lambda: self.switch_uArm_with_record_status(record_status=None))
        # 视频播放工具栏
        self.video_play_action = QAction(QIcon(icon_path.Icon_video_play), 'video_play', self)
        self.video_play_action.triggered.connect(self.play_exist_video)
        # ui工具栏
        self.ui_toolbar.addAction(self.switch_camera_status_action)
        self.ui_toolbar.addAction(self.capture_action)
        self.ui_toolbar.addAction(self.box_screen_action)
        self.ui_toolbar.addAction(self.picture_path_action)
        self.ui_toolbar.addAction(self.setting_action)
        self.ui_toolbar.addSeparator()
        # robot工具栏
        self.robot_operate_toolbar.addAction(self.robot_lock_action)
        self.robot_operate_toolbar.addAction(self.robot_unlock_action)
        self.robot_operate_toolbar.addAction(self.robot_get_position_action)
        self.robot_operate_toolbar.addAction(self.click_action)
        self.robot_operate_toolbar.addAction(self.double_click_action)
        self.robot_operate_toolbar.addAction(self.long_click_action)
        self.robot_operate_toolbar.addAction(self.slide_action)
        self.robot_operate_toolbar.addAction(self.robot_with_record_action)
        # 存在的视频播放工具栏
        self.video_play_toolbar.addAction(self.video_play_action)


    # 视频播放框架
    def video_play_frame(self):
        self.video_frame = QFrame(self.central_widget)
        self.grid.addWidget(self.video_frame, 0, 0, 5, 8)
        self.video_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.video_frame_h_layout = QHBoxLayout(self.video_frame)
        # 视频标签
        self.label_video = Video_Label(self.video_frame)
        self.label_video.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.label_video.setObjectName('label_video')
        self.label_video.signal[str].connect(self.recv_video_label_signal)
        # 填充背景图片
        self.label_video.setPixmap(QtGui.QPixmap(self.background_file))
        # 自动填充满label
        self.label_video.setScaledContents(True)
        # 标准光标
        self.label_video.setCursor(Qt.ArrowCursor)
        # 十字光标
        # self.label_video.setCursor(Qt.CrossCursor)

        # 单独布局视频label
        self.video_frame_h_layout.addStretch(1)
        self.video_frame_h_layout.addWidget(self.label_video)
        self.video_frame_h_layout.addStretch(1)

        # label垂直布局
        self.label_v_layout = QVBoxLayout(self.label_video)
        # button水平布局
        self.button_h_layout = QHBoxLayout(self.label_video)
        # 暂停按钮/空格键
        self.status_video_button = QtWidgets.QPushButton(self.label_video)
        self.status_video_button.setObjectName('status_video_button')
        self.status_video_button.setFixedSize(48, 48)
        # 图片铺满按钮背景
        self.status_video_button.setStyleSheet('border-image: url('+ icon_path.Icon_player_play + ')')
        self.status_video_button.setShortcut(Qt.Key_Space)
        self.status_video_button.clicked.connect(self.switch_video)
        self.status_video_button.setEnabled(False)
        # 上一个视频
        self.last_video_button = QtWidgets.QPushButton(self.label_video)
        self.last_video_button.setObjectName('last_video_button')
        self.last_video_button.setFixedSize(48, 48)
        self.last_video_button.setStyleSheet('border-image: url('+ icon_path.Icon_player_last_video + ')')
        self.last_video_button.setShortcut(Qt.Key_Up)
        self.last_video_button.clicked.connect(self.last_video)
        self.last_video_button.setEnabled(True)
        # 下一个视频
        self.next_video_button = QtWidgets.QPushButton(self.label_video)
        self.next_video_button.setObjectName('next_video_button')
        self.next_video_button.setFixedSize(48, 48)
        self.next_video_button.setStyleSheet('border-image: url('+ icon_path.Icon_player_next_video + ')')
        self.next_video_button.setShortcut(Qt.Key_Down)
        self.next_video_button.clicked.connect(self.next_video)
        self.next_video_button.setEnabled(False)
        # 上一帧
        self.last_frame_button = QtWidgets.QPushButton(self.label_video)
        self.last_frame_button.setObjectName('last_frame_button')
        self.last_frame_button.setFixedSize(48, 48)
        self.last_frame_button.setStyleSheet('border-image: url('+ icon_path.Icon_player_last_frame + ')')
        self.last_frame_button.setShortcut(Qt.Key_Left)
        self.last_frame_button.clicked.connect(self.last_frame)
        self.last_frame_button.setEnabled(False)
        # 下一帧
        self.next_frame_button = QtWidgets.QPushButton(self.label_video)
        self.next_frame_button.setObjectName('next_frame_button')
        self.next_frame_button.setFixedSize(48, 48)
        self.next_frame_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_next_frame + ')')
        self.next_frame_button.setShortcut(Qt.Key_Right)
        self.next_frame_button.clicked.connect(self.next_frame)
        self.next_frame_button.setEnabled(False)
        # 帧数显示
        self.label_frame_show = QtWidgets.QLabel(self.label_video)
        self.label_frame_show.setObjectName("label_frame_show")
        self.label_frame_show.setAlignment(Qt.AlignCenter)
        self.label_frame_show.setText('')
        self.label_frame_show.setFont(QFont(self.font, 12))
        self.label_frame_show.setAlignment(Qt.AlignCenter)
        self.label_frame_show.setStyleSheet('color:black')
        # 显示视频名字
        self.label_video_title = QtWidgets.QLabel(self.label_video)
        self.label_video_title.setObjectName("label_video_title")
        self.label_video_title.setAlignment(Qt.AlignCenter)
        self.label_video_title.setText('[实时视频流]')
        self.label_video_title.setFont(QFont(self.font, 15))
        # 视频进度条
        self.video_progress_bar = QSlider(Qt.Horizontal, self.label_video)
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


    # 视频标签控件接收函数(接收到信息后需要进行的操作)
    def recv_video_label_signal(self, info_str):
        # 先将字符串转化为list
        # 当list为两个元素时 : 第一个为点击动作类型, 第二个为点击动作坐标
        # 当list为三个元素时 : 第一个为滑动动作类型, 第二个为起点坐标, 第三个为终止点坐标
        info_list = eval(info_str)
        # 如果是添加动作时, 不作操作(只添加动作)
        if add_action_window.add_action_flag is True:
            if info_list[0] in [uArm_action.uArm_click, uArm_action.uArm_double_click, uArm_action.uArm_long_click, uArm_action.uArm_slide]:
                position_str = str(info_list[1])
                position_tuple = info_list[1]
            else: # 为了不让position_str有警告(无具体意义)
                position_str = '0, 0'
                position_tuple = (0.0, 0.0)
            # 添加动作取完坐标后, 需要在子窗口中添加坐标信息, 以及回传坐标信息
            self.show_tab_widget.action_tab.add_action_window.widget.action_tab.points.setText(position_str)
            self.show_tab_widget.action_tab.add_action_window.widget.action_tab.info_dict[add_action_window.points] = position_tuple
            self.show_tab_widget.action_tab.add_action_window.setHidden(False)
            add_action_window.add_action_flag = False
        # 正常点击时会直接执行动作
        else:
            # 根据返回值形成info_dict字典
            info_dict = {add_action_window.des_text: info_list[0],
                         add_action_window.action_type: info_list[0],
                         add_action_window.speed: 150,
                         add_action_window.points: info_list[1],
                         add_action_window.leave: 1,
                         add_action_window.trigger: 0}
            # 默认速度150 & 动作执行后离开
            Thread(target=self.uArm_action_execute, args=(info_dict,)).start()
            # 脚本录制操作
            if uArm_action.uArm_with_record is True:
                self.show_tab_widget.action_tab.add_action_item(info_dict=info_dict)


    # 机械臂动作执行
    def uArm_action_execute(self, info_dict):
        # 从字典中获取键值
        speed = int(info_dict[add_action_window.speed])
        leave = int(info_dict[add_action_window.leave])
        trigger = int(info_dict[add_action_window.trigger])
        action_type = info_dict[add_action_window.action_type]
        position_tuple = tuple(info_dict[add_action_window.points])
        # 有;存在则说明是滑动动作(两个坐标)
        if len(position_tuple) == 2:
            position = tuple(position_tuple)
            start, end = (0.0, 0.0), (0.0, 0.0)
        # 没有则说明是点击动作(单个坐标)
        else:
            position = (0.0, 0.0)
            start, end = position_tuple[:2], position_tuple[2:]
        # 执行单击动作
        if action_type == uArm_action.uArm_click:
            data = {'base': (uArm_param.base_x_point, uArm_param.base_y_point, uArm_param.base_z_point),
                    'speed': speed, 'leave': leave, 'trigger': trigger, 'time': 1,
                    'position': position, 'pressure_duration': 0}
            Thread(target=self.uArm_post_request, args=('uArm', uArm_action.uArm_click, data,)).start()
            logger('执行-->action[click]---------坐标: %s' % str(position))
        # 执行双击动作
        elif action_type == uArm_action.uArm_double_click:
            data = {'base': (uArm_param.base_x_point, uArm_param.base_y_point, uArm_param.base_z_point),
                    'speed': speed, 'leave': leave, 'trigger': trigger, 'time': 2,
                    'position': position, 'pressure_duration': 0}
            Thread(target=self.uArm_post_request, args=('uArm', uArm_action.uArm_click, data,)).start()
            logger('执行-->action[double_click]--坐标: %s' % str(position))
        # 执行长按动作
        elif action_type == uArm_action.uArm_long_click:
            data = {'base': (uArm_param.base_x_point, uArm_param.base_y_point, uArm_param.base_z_point),
                    'speed': speed, 'leave': leave, 'trigger': trigger, 'time': 1,
                    'position': position, 'pressure_duration': 1000}
            Thread(target=self.uArm_post_request, args=('uArm', uArm_action.uArm_click, data,)).start()
            logger('执行-->action[long_click]----坐标: %s' % str(position))
        # 执行滑动动作
        elif action_type == uArm_action.uArm_slide:
            data = {'base': (uArm_param.base_x_point, uArm_param.base_y_point, uArm_param.base_z_point),
                    'speed': speed, 'leave': leave, 'trigger': trigger,
                    'start': start, 'end': end}
            Thread(target=self.uArm_post_request, args=('uArm', uArm_action.uArm_slide, data,)).start()
            logger('执行-->action[slide]---------坐标: %s' % str(tuple(start + end)))


    # 进度条刷新
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
                    show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
                    self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
                    self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
                    self.label_frame_show.setStyleSheet('color:white')
                    self.video_progress_bar.setValue(self.current_frame)
                    # 当遇到当前视频播放完毕时, 需要将进度条往回拉动的时候
                    if self.video_status == self.STATUS_STOP:
                        self.video_status = self.STATUS_PAUSE
                        self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
            except Exception as e:
                logger('[当前视频播放完毕]')
            self.slider_flag = False


    # case展示
    def show_case(self):
        self.show_tab_widget = ShowTabWidget(self.central_widget)
        self.grid.addWidget(self.show_tab_widget, 0, 8, 3, 2)
        self.show_tab_widget.signal[str].connect(self.recv_show_tab_widget_signal)


    # 接收show_tab_widget的信号
    def recv_show_tab_widget_signal(self, signal_str):
        # 执行action动作
        if signal_str.startswith('action_execute_item>'):
            signal_dict = json.loads(signal_str.split('>')[1])
            Thread(target=self.uArm_action_execute, args=(signal_dict,)).start()
        # 执行record动作
        elif signal_str.startswith('record_execute_item>'):
            signal_dict = json.loads(signal_str.split('>')[1])
            # 添加视频存放根目录
            signal_dict['video_path'] = gloVar.project_video_path
            Thread(target=self.uArm_post_request, args=('record', 'record_status', signal_dict)).start()
            logger('执行-->action[%s]----status[%s]' %(record_action.record_status, signal_dict[record_action.record_status]))
        # 执行sleep动作
        elif signal_str.startswith('sleep_execute_item>'):
            signal_dict = json.loads(signal_str.split('>')[1])
            Thread(target=self.uArm_post_request, args=('sleep', 'sleep_time', signal_dict)).start()
            logger('执行-->action[%s]----status[%s]' %(sleep_action.sleep_time, str(signal_dict[sleep_action.sleep_time])))
        # 添加action控件时候, 设置动作标志位
        elif signal_str.startswith('action_tab_action>'):
            # 消除留在视频界面的印记
            self.label_video.x1, self.label_video.y1 = self.label_video.x0, self.label_video.y0
            uArm_action.uArm_action_type = signal_str.split('>')[1]
        else:
            pass


    # 控制台输出
    def output_text(self):
        self.frame_of_console_output = QtWidgets.QFrame(self.central_widget)
        self.frame_of_console_output.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_of_console_output.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_of_console_output.setObjectName("frame_of_console_output")
        self.frame_of_console_output.setMinimumWidth(80)
        self.grid.addWidget(self.frame_of_console_output, 3, 8, 2, 2)
        self.console_v_layout = QVBoxLayout(self.frame_of_console_output)
        self.label_output = QtWidgets.QLabel(self.frame_of_console_output)
        self.label_output.setObjectName("label_output")
        self.label_output.setText('[Console输出]')
        self.label_output.setAlignment(Qt.AlignLeft)
        self.label_output.setFont(QFont(self.font, 12))
        self.console = QTextEdit(self.frame_of_console_output)
        self.console.verticalScrollBar().setStyleSheet("QScrollBar{width:10px;}")
        self.console.horizontalScrollBar().setStyleSheet("QScrollBar{height:10px;}")
        self.console.setReadOnly(True)
        self.console.ensureCursorVisible()
        self.console.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.console.setWordWrapMode(QTextOption.NoWrap)
        self.console.setFont(QFont('monospaced', 13))
        # self.console.setStyleSheet('background-color:lightGray')
        self.console_v_layout.addWidget(self.label_output)
        self.console_v_layout.addWidget(self.console)


    # 展示视频函数
    def show_video(self):
        # 实时模式
        if self.video_play_flag is False:
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
            if gloVar.save_pic_flag is True:
                cv2.imencode('.jpg', self.image.copy())[1].tofile('mask.jpg')
                gloVar.save_pic_flag = False
        # 录播模式(可以数帧)
        else:
            if self.current_frame < self.frame_count:
                self.current_frame += 1
                flag, self.image = self.video_cap.read()
                if flag is True:
                    show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
                    self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
                    self.label_frame_show.setText(str(self.current_frame+1)+'F/'+str(self.frame_count))
                    self.label_frame_show.setStyleSheet('color:white')
                    self.video_progress_bar.setValue(self.current_frame)
                else:
                    self.video_cap.release()
                    self.video_status = self.STATUS_STOP
                    self.timer_video.stop()
                    self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_replay + ')')
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
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_replay + ')')
                self.last_video_button.setEnabled(True)
                self.next_video_button.setEnabled(True)
                self.last_frame_button.setEnabled(True)
                self.next_frame_button.setEnabled(True)
                # 再重新加载视频(有可能视频播放完毕后, 需要往前进一帧)
                self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
        # QApplication.processEvents() # 界面刷新


# 暂停视频
    def template_label(self):
        time.sleep(0.3)
        # 暂停后不允许机械臂动作操作
        uArm_action.uArm_action_type = None
        robot_other.image = self.image
        # # 数据处理调用
        # if robot_other.data_process_flag is True:
        #     mask_image_path = os.path.join(self.get_path, 'mask')
        # else:
        #     mask_image_path = None
        mask_image_path = self.picture_path
        robot_other.mask_path = mask_image_path


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
                robot_other.select_template_flag = False
                self.label_video.setCursor(Qt.ArrowCursor)
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_pause + ')')
                logger('<打开视频流>')
            elif self.video_status is self.STATUS_PLAYING:
                self.timer_video.stop()
                self.video_status = self.STATUS_PAUSE
                robot_other.select_template_flag = True
                self.label_video.setCursor(Qt.CrossCursor)
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
                self.template_label()
                logger('<暂停视频流>')
            elif self.video_status is self.STATUS_PAUSE:
                self.timer_video.start()
                self.label_video_title.setStyleSheet('color:white')
                self.video_status = self.STATUS_PLAYING
                robot_other.select_template_flag = False
                self.label_video.setCursor(Qt.ArrowCursor)
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_pause + ')')
                logger('<打开视频流>')
        else: # 如果是录播模式
            if self.video_status is self.STATUS_INIT:
                self.timer_video.start()
                self.last_frame_button.setEnabled(False)
                self.next_frame_button.setEnabled(False)
                self.last_video_button.setEnabled(False)
                self.next_video_button.setEnabled(False)
                self.label_video_title.setStyleSheet('color:white')
                self.video_status = self.STATUS_PLAYING
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_pause + ')')
                robot_other.select_template_flag = False
                self.label_video.setCursor(Qt.ArrowCursor)
                logger('<播放视频>')
            elif self.video_status is self.STATUS_PLAYING:
                self.timer_video.stop()
                # 暂停后/使能上下一帧
                self.last_frame_button.setEnabled(True)
                self.next_frame_button.setEnabled(True)
                self.last_video_button.setEnabled(True)
                self.next_video_button.setEnabled(True)
                self.video_status = self.STATUS_PAUSE
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
                robot_other.select_template_flag = True
                self.label_video.setCursor(Qt.CrossCursor)
                self.template_label()
                logger('<暂停视频>')
            elif self.video_status is self.STATUS_PAUSE:
                self.timer_video.start()
                self.last_frame_button.setEnabled(False)
                self.next_frame_button.setEnabled(False)
                self.last_video_button.setEnabled(False)
                self.next_video_button.setEnabled(False)
                self.label_video_title.setStyleSheet('color:white')
                self.video_status = self.STATUS_PLAYING
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_pause + ')')
                robot_other.select_template_flag = False
                self.label_video.setCursor(Qt.ArrowCursor)
                logger('<播放视频>')
            elif self.video_status is self.STATUS_STOP:
                self.current_frame = 0
                self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
                _, self.image = self.video_cap.read()
                show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
                self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
                self.label_video_title.setStyleSheet('color:white')
                self.label_frame_show.setText(str(self.current_frame+1)+'F/'+str(self.frame_count))
                self.label_frame_show.setStyleSheet('color:white')
                # 开启视频流
                self.timer_video.start()
                self.video_status = self.STATUS_PLAYING
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_pause + ')')
                self.last_video_button.setEnabled(False)
                self.next_video_button.setEnabled(False)
                self.last_frame_button.setEnabled(False)
                self.next_frame_button.setEnabled(False)
                logger('<重新播放视频>')
        time.sleep(0.1)  # 延时防抖
        self.status_video_button.setEnabled(True)


    # 切换到上个视频
    def last_video(self):
        # 防抖(首末行)
        self.last_video_button.setEnabled(False)
        if self.video_play_flag is True:
            self.timer_video.stop()
            self.video_status = self.STATUS_INIT
            self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
            if self.current_video > 0:
                self.current_video = self.current_video - 1
            else:
                self.current_video = len(self.videos) - 1
            # 加载离线视频
            self.current_frame = 0
            self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            # 需要获取视频尺寸
            self.offline_video_width = int(self.video_cap.get(3))
            self.offline_video_height = int(self.video_cap.get(4))
            # 获取视频总帧数
            self.frame_count = int(self.video_cap.get(7))
            # 设置视频进度滑动条范围
            self.video_progress_bar.setRange(0, self.frame_count-1)
            # 获取第一帧
            _, self.image = self.video_cap.read()
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
            # 设置帧数显示
            self.label_frame_show.setText(str(self.current_frame+1) + 'F/' + str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
            # 设置视频title
            self.label_video_title.setText('['+str(self.current_video+1)+'/'+str(len(self.videos))+']'+self.videos_title[self.current_video])
            self.label_video_title.setStyleSheet('color:white')
            self.last_frame_button.setEnabled(True)
            self.next_frame_button.setEnabled(True)
        self.last_video_button.setEnabled(True)
        self.next_video_button.setEnabled(True)
        self.status_video_button.setEnabled(True)
        self.label_video.setCursor(Qt.ArrowCursor)
        # 通过离线视频尺寸自适应视频播放窗口
        self.video_label_adaptive(self.offline_video_width, self.offline_video_height)
        self.last_video_button.setEnabled(True)


    # 切换到下个视频
    def next_video(self):
        # 防抖(首末行)
        self.next_video_button.setEnabled(False)
        if self.video_play_flag is True:
            self.timer_video.stop()
            self.video_status = self.STATUS_INIT
            self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
            if self.current_video < len(self.videos) - 1:
                self.current_video = self.current_video + 1
            else:
                self.current_video = 0
            # 加载离线视频
            self.current_frame = 0
            self.video_cap = cv2.VideoCapture(self.videos[self.current_video])
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            # 需要获取视频尺寸
            self.offline_video_width = int(self.video_cap.get(3))
            self.offline_video_height = int(self.video_cap.get(4))
            # 获取视频总帧数
            self.frame_count = int(self.video_cap.get(7))
            # 设置视频进度滑动条范围
            self.video_progress_bar.setRange(0, self.frame_count - 1)
            # 获取第一帧
            _, self.image = self.video_cap.read()
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
            # 设置帧数显示
            self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
            # 设置视频title
            self.label_video_title.setText('['+str(self.current_video+1)+'/'+str(len(self.videos))+']'+self.videos_title[self.current_video])
            self.label_video_title.setStyleSheet('color:white')
            self.last_frame_button.setEnabled(True)
            self.next_frame_button.setEnabled(True)
        self.last_video_button.setEnabled(True)
        self.next_video_button.setEnabled(True)
        self.status_video_button.setEnabled(True)
        self.label_video.setCursor(Qt.ArrowCursor)
        # 通过离线视频尺寸自适应视频播放窗口
        self.video_label_adaptive(self.offline_video_width, self.offline_video_height)
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
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
            self.label_frame_show.setText(str(self.current_frame+1)+'F/'+str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
            # 当遇到当前视频播放完毕时, 需要回退帧的时候
            if self.video_status == self.STATUS_STOP:
                self.video_status = self.STATUS_PAUSE
                self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_play + ')')
        else:
            self.video_cap.release()
            self.video_status = self.STATUS_STOP
            self.timer_video.stop()
            self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_replay + ')')
            self.video_progress_bar.setValue(self.frame_count-1)
        # self.last_frame_button.setEnabled(True)


    # 切换到下一帧(不能防抖, 如果防抖的话就不能左右键快速播帧)
    def next_frame(self):
        # self.next_frame_button.setEnabled(False)
        if self.current_frame < self.frame_count - 1:
            self.current_frame = self.current_frame + 1
        else:
            self.current_frame = self.frame_count - 1
        flag, self.image = self.video_cap.read()
        if flag is True:
            show = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            show_image = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(show_image))
            self.label_frame_show.setText(str(self.current_frame+1)+'F/'+str(self.frame_count))
            self.label_frame_show.setStyleSheet('color:white')
            self.video_progress_bar.setValue(self.current_frame)
        else:
            self.video_cap.release()
            self.video_status = self.STATUS_STOP
            self.timer_video.stop()
            self.status_video_button.setStyleSheet('border-image: url(' + icon_path.Icon_player_replay + ')')
            self.video_progress_bar.setValue(self.frame_count-1)
        # self.next_frame_button.setEnabled(True)


    # 连接到视频进度栏
    def connect_video_progress_bar(self):
        self.current_frame = self.video_progress_bar.value()
        self.label_frame_show.setText(str(self.current_frame + 1) + 'F/' + str(self.frame_count))
        self.label_frame_show.setStyleSheet('color:white')
        self.slider_flag = True


    # 视频标签自适应
    def video_label_adaptive(self, video_width, video_height):
        # 第一次触发实在窗口生成的时候, 没有意义
        if self.first_window_zoom_flag is True:
            self.first_window_zoom_flag = False
            # 通过中心widget计算初始视频标签的大小(同时减去的50代表widget的边界部分)
            # video_label高度和self.central_widget的高度大致相同
            # video_label宽度为self.central_widget的宽度大3/4, 通过栅格布局可知
            self.video_label_size_width = int((self.central_widget.size().width() - 50) * 0.75)
            self.video_label_size_height = int((self.central_widget.size().height() - 50) * 1.00)
        else:  # (距离边框还有30左右)
            self.video_label_size_width = self.video_frame.size().width() - 50
            self.video_label_size_height = self.video_frame.size().height() - 50
        # 更改label_video大小以确保视频展示不失比例
        # 真实视频比例
        video_size_scale = float(video_height / video_width)
        # 临界比例(根据页面网格布局得到, 不可随便修改)
        # limit_size_scale = float(982/1477)
        limit_size_scale = float(self.video_label_size_height / self.video_label_size_width)
        if video_size_scale >= limit_size_scale:
            self.video_label_size_height = self.video_label_size_height
            self.video_label_size_width = int((self.video_label_size_height / video_height) * video_width)
        else:
            self.video_label_size_width = self.video_label_size_width
            self.video_label_size_height = int((self.video_label_size_width / video_width) * video_height)
        self.label_video.setFixedSize(self.video_label_size_width, self.video_label_size_height)
        # 计算视频和label_video之间比例因子(框选保存图片需要用到)
        self.label_video.x_unit = float(video_width / self.video_label_size_width)
        self.label_video.y_unit = float(video_height / self.video_label_size_height)
        # 重新计算框选的车机屏幕大小(可以适应不同大小屏幕)
        if sum(self.label_video.box_screen_size) > 0:
            self.label_video.box_screen_size[0] = int(self.label_video.size().width()  * self.label_video.box_screen_scale[0])
            self.label_video.box_screen_size[1] = int(self.label_video.size().height() * self.label_video.box_screen_scale[1])
            self.label_video.box_screen_size[2] = int(self.label_video.size().width()  * (self.label_video.box_screen_scale[2]-self.label_video.box_screen_scale[0]))
            self.label_video.box_screen_size[3] = int(self.label_video.size().height() * (self.label_video.box_screen_scale[3]-self.label_video.box_screen_scale[1]))


    # 重写窗口关闭时间
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '本程序', '是否要退出程序?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 杀死python_server
            if self.python_server_pid is not None:
                os.system('taskkill -f -pid %s' % self.python_server_pid)
            # 关闭摄像头
            self.camera_status = self.camera_closed
            self.timer_window_status.stop()
            self.slider_thread.stop()
            event.accept()
        else:
            event.ignore()


    # 监听窗口缩放事件
    def resizeEvent(self, event):
        if self.video_play_flag is False:
            self.video_label_adaptive(self.real_time_video_width, self.real_time_video_height)
        else:
            self.video_label_adaptive(self.offline_video_width, self.offline_video_height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = UiMainWindow()
    gui.setupUi()
    gui.show()
    sys.exit(app.exec_())