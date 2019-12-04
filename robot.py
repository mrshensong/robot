import os
import sys
import cv2
import time
import datetime
from threading import Thread
from processdata.get_startup_time import GetStartupTime
from uiclass.stream import Stream
from uiclass.timer import Timer
from uiclass.show_tab_widget import ShowTabWidget
from uiclass.controls import CameraParamAdjustControl, FrameRateAdjustControl
from uiclass.main_show_tab_widget import MainShowTabWidget
from uiclass.project_bar import ProjectBar
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon, QTextOption, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QVBoxLayout, QWidget, QMessageBox, QFileDialog, QLabel, QTextEdit, QAction, QApplication, QSplitter
from GlobalVar import GloVar, IconPath, RobotArmAction, RobotArmParam, Logger, RobotOther, MotionAction, RecordAction, SleepAction, MergePath, WindowStatus, Profile
from uarm_action.action import ArmAction


class UiMainWindow(QMainWindow):
    # 字体 'Microsoft YaHei'
    font = 'Times New Roman'
    # icon文件
    icon_file = IconPath.Icon_file
    # background文件
    background_file = IconPath.background_file


    def setupUi(self):
        """初始化参数"""
        # 摄像机图像尺寸
        # self.camera_image_width = 1280
        # self.camera_image_height = 720
        self.camera_image_width = int(Profile(type='read', file=GloVar.config_file_path, section='param', option='camera_size_width').value)
        self.camera_image_height = int(Profile(type='read', file=GloVar.config_file_path, section='param', option='camera_size_height').value)
        # 从配置文件中读取基准点
        base_point = eval(Profile(type='read', file=GloVar.config_file_path, section='param', option='base_point').value)
        RobotArmParam.base_x_point, RobotArmParam.base_y_point, RobotArmParam.base_z_point = base_point
        # 获取到的视频根目录
        self.get_path = None
        # 获取截图保存路径
        self.picture_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='picture_path').value
        GloVar.project_picture_path = self.picture_path
        # 视频所在的路径
        self.videos_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='videos_path').value
        # 窗口状态栏显示的固定格式
        self.window_status_text = '机械臂:[%s];    视频帧率:[%s];    action_tab页面:[%s];    case_tab页面:[%s]' \
                                  % (WindowStatus.robot_connect_status, WindowStatus.video_frame_rate,
                                     WindowStatus.action_tab_status, WindowStatus.case_tab_status)
        # 如果需要检测, 数据处理需要用到的模板, 是否准备完成(True:确认需要检测/False:退出检测)
        self.need_detect_data_flag = False
        # 今天的日期(用作文件夹名)
        self.today_data = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # 获取当前工程路径(连接符标准化为正斜杠模式)
        GloVar.project_path = MergePath(section_path=[os.path.abspath(os.getcwd())]).merged_path
        # 获取工程视频保存路径
        GloVar.project_video_path = MergePath(section_path=[os.path.abspath(os.getcwd()), 'video', self.today_data]).merged_path

        # 显示窗口状态栏
        self.timer_window_status = Timer(frequent=3)
        self.timer_window_status.timeSignal[str].connect(self.show_window_status)
        self.timer_window_status.start()

        self.setObjectName("MainWindow")
        self.setGeometry(260, 70, 1400, 900)
        # self.resize(1400, 900)
        self.setMinimumSize(QSize(1200, 700))
        self.setWindowTitle("Auto Robot")
        self.setWindowIcon(QIcon(self.icon_file))
        # 中间widget区域
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)

        ## 定义UI 字体 和 字号大小
        self.setFont(QFont(self.font, 13))
        # 设置UI背景颜色为灰色
        # self.central_widget.setStyleSheet('background-color:lightgrey')
        # 视频播放框架
        self.video_play_frame()
        # case展示
        self.show_case()
        # 工程栏
        self.project_bar()
        # 控制台输出框架
        self.output_text()
        # 菜单栏
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setObjectName('menu_bar')
        self.setMenuBar(self.menu_bar)
        # 状态栏 & 状态栏显示
        self.status_bar = QStatusBar(self)
        self.status_bar.setObjectName('status_bar')
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.window_status_text)
        # 状态栏颜色
        # self.status_bar.setStyleSheet('color:green')
        self.status_bar.setFont(QFont(self.font, 13))
        # 工具栏
        # 实时流工具栏
        self.live_video_toolbar = self.addToolBar('live_video_toolbar')
        # 机械臂工具栏
        self.robot_toolbar = self.addToolBar('robot_toolbar')
        # 本地视频工具栏
        self.local_video_toolbar = self.addToolBar('local_video_toolbar')
        # 数据处理工具栏
        self.data_process_toolbar = self.addToolBar('data_process_toolbar')
        # 视频实时流参数设置框
        self.camera_param_setting_widget = CameraParamAdjustControl(self)
        self.camera_param_setting_widget.signal[str].connect(self.recv_camera_param_setting_widget)
        # 本地视频帧率调节
        self.frame_rate_adjust_widget = FrameRateAdjustControl(self)
        self.frame_rate_adjust_widget.signal[str].connect(self.recv_frame_rate_adjust_widget)
        # 接收进程打印的信息
        sys.stdout = Stream(newText=self.update_text)
        sys.stderr = Stream(newText=self.update_text)
        # 菜单栏
        self.menu_bar_show()
        # 工具栏
        self.tool_bar()

        # 全局竖直布局
        self.general_v_layout = QVBoxLayout(self.central_widget)
        # 分割窗口布局
        self.splitter_h_general = QSplitter(Qt.Horizontal)
        self.splitter_v_part_1 = QSplitter(Qt.Vertical)
        self.splitter_v_part_2 = QSplitter(Qt.Vertical)
        self.splitter_v_part_1.addWidget(self.project_bar_widget)
        self.splitter_v_part_1.addWidget(self.show_tab_widget)
        # 设置QSplitter中的两个widget的高度(第一个不显示, 剩余高度全部显示第二个)
        self.splitter_v_part_1.setSizes([0, 100])
        # 通过比例显示QSplitter中的两个widget的所占比例
        # self.splitter_v_part_1.setStretchFactor(0, 0)
        # self.splitter_v_part_1.setStretchFactor(1, 1)
        self.splitter_v_part_2.addWidget(self.main_show_tab_widget)
        self.splitter_v_part_2.addWidget(self.console)
        self.splitter_v_part_2.setStretchFactor(0, 4)
        self.splitter_v_part_2.setStretchFactor(1, 3)
        self.splitter_h_general.addWidget(self.splitter_v_part_1)
        self.splitter_h_general.addWidget(self.splitter_v_part_2)
        self.splitter_h_general.setStretchFactor(0, 6)
        self.splitter_h_general.setStretchFactor(1, 13)
        self.general_v_layout.addWidget(self.splitter_h_general)
        self.setLayout(self.general_v_layout)

        # 机械臂处理
        self.robot = ArmAction(camera_width=self.camera_image_width, camera_height=self.camera_image_height)


    '''以下部分为界面各个控件信息'''
    # 菜单栏
    def menu_bar_show(self):
        # 菜单栏显示
        self.test_action = QAction('exit', self)
        self.file_bar = self.menu_bar.addMenu('File')
        self.file_bar.addAction(self.test_action)


    # 工具栏
    def tool_bar(self):
        # 实时流相关action
        self.live_video_toolbar_label = QLabel(self)
        self.live_video_toolbar_label.setText('实时流:')
        self.live_video_toolbar_label.setStyleSheet('color:blue')
        self.live_video_toolbar_label.setFont(QFont(self.font, 13))
        self.live_video_setting_action               = QAction(QIcon(IconPath.Icon_live_video_setting), 'setting', self)
        self.live_video_switch_camera_status_action  = QAction(QIcon(IconPath.Icon_live_video_open_camera), 'open_camera', self)
        self.live_video_capture_action               = QAction(QIcon(IconPath.Icon_live_video_capture), 'capture', self)
        self.live_video_box_screen_action            = QAction(QIcon(IconPath.Icon_live_video_box_screen), 'box_screen', self)
        # 绑定触发函数
        self.live_video_switch_camera_status_action.triggered.connect(self.switch_camera_status)
        self.live_video_capture_action.triggered.connect(self.screen_shot)
        self.live_video_box_screen_action.triggered.connect(self.box_screen)
        self.live_video_setting_action.triggered.connect(self.set_camera_param)
        # robot相关action
        self.robot_toolbar_label = QLabel(self)
        self.robot_toolbar_label.setText('机械臂:')
        self.robot_toolbar_label.setStyleSheet('color:blue')
        self.robot_toolbar_label.setFont(QFont(self.font, 13))
        self.robot_click_action        = QAction(QIcon(IconPath.Icon_robot_click), 'click', self)
        self.robot_double_click_action = QAction(QIcon(IconPath.Icon_robot_double_click), 'double_click', self)
        self.robot_long_click_action   = QAction(QIcon(IconPath.Icon_robot_long_click), 'long_click', self)
        self.robot_slide_action        = QAction(QIcon(IconPath.Icon_robot_slide), 'slide', self)
        self.robot_lock_action         = QAction(QIcon(IconPath.Icon_robot_lock), 'lock', self)
        self.robot_unlock_action       = QAction(QIcon(IconPath.Icon_robot_unlock), 'unlock', self)
        self.robot_get_base_position_action = QAction(QIcon(IconPath.Icon_robot_get_base_position), 'get_position', self)
        self.robot_with_record_action  = QAction(QIcon(IconPath.Icon_robot_with_record), 'with_record', self)
        # 绑定触发函数
        self.robot_click_action.triggered.connect(lambda: self.uArm_action_event(RobotArmAction.uArm_click))
        self.robot_double_click_action.triggered.connect(lambda: self.uArm_action_event(RobotArmAction.uArm_double_click))
        self.robot_long_click_action.triggered.connect(lambda: self.uArm_action_event(RobotArmAction.uArm_long_click))
        self.robot_slide_action.triggered.connect(lambda: self.uArm_action_event(RobotArmAction.uArm_slide))
        self.robot_lock_action.triggered.connect(lambda: self.uArm_action_event(RobotArmAction.uArm_lock))
        self.robot_unlock_action.triggered.connect(lambda: self.uArm_action_event(RobotArmAction.uArm_unlock))
        self.robot_get_base_position_action.triggered.connect(lambda: self.uArm_action_event(RobotArmAction.uArm_get_position))
        self.robot_with_record_action.triggered.connect(lambda: self.switch_uArm_with_record_status(record_status=None))
        # 视频播放工具栏
        self.local_video_toolbar_label = QLabel(self)
        self.local_video_toolbar_label.setText('本地视频:')
        self.local_video_toolbar_label.setStyleSheet('color:blue')
        self.local_video_toolbar_label.setFont(QFont(self.font, 13))
        self.local_video_import_video_action = QAction(QIcon(IconPath.Icon_local_import_video), 'import_video', self)
        self.local_video_setting_action      = QAction(QIcon(IconPath.Icon_local_video_setting), 'setting', self)
        self.local_video_setting_action.setEnabled(False)
        # 绑定函数
        self.local_video_import_video_action.triggered.connect(self.import_local_video)
        self.local_video_setting_action.triggered.connect(self.set_frame_rate)
        # 数据处理工具栏
        self.data_process_toolbar_label = QLabel(self)
        self.data_process_toolbar_label.setText('数据处理:')
        self.data_process_toolbar_label.setStyleSheet('color:blue')
        self.data_process_toolbar_label.setFont(QFont(self.font, 13))
        self.data_process_import_video_action = QAction(QIcon(IconPath.Icon_data_process_import_video), 'import_video', self)
        self.data_process_setting_action      = QAction(QIcon(IconPath.Icon_data_process_setting), 'setting', self)
        self.data_process_execute_action      = QAction(QIcon(IconPath.Icon_data_process_execute), 'execute', self)
        self.data_process_setting_action.setEnabled(False)
        self.data_process_execute_action.setEnabled(False)
        # 绑定函数
        self.data_process_import_video_action.triggered.connect(self.data_process_import_video)
        self.data_process_setting_action.triggered.connect(self.set_frame_rate)
        self.data_process_execute_action.triggered.connect(self.data_process_execute)
        # 实时流工具栏
        self.live_video_toolbar.addWidget(self.live_video_toolbar_label)
        self.live_video_toolbar.addAction(self.live_video_switch_camera_status_action)
        self.live_video_toolbar.addAction(self.live_video_box_screen_action)
        self.live_video_toolbar.addAction(self.live_video_capture_action)
        self.live_video_toolbar.addAction(self.live_video_setting_action)
        self.live_video_toolbar.addSeparator()
        # robot工具栏
        self.robot_toolbar.addWidget(self.robot_toolbar_label)
        self.robot_toolbar.addAction(self.robot_lock_action)
        self.robot_toolbar.addAction(self.robot_unlock_action)
        self.robot_toolbar.addAction(self.robot_get_base_position_action)
        self.robot_toolbar.addAction(self.robot_click_action)
        self.robot_toolbar.addAction(self.robot_double_click_action)
        self.robot_toolbar.addAction(self.robot_long_click_action)
        self.robot_toolbar.addAction(self.robot_slide_action)
        self.robot_toolbar.addAction(self.robot_with_record_action)
        # 本地视频播放工具栏
        self.local_video_toolbar.addWidget(self.local_video_toolbar_label)
        self.local_video_toolbar.addAction(self.local_video_import_video_action)
        self.local_video_toolbar.addAction(self.local_video_setting_action)
        # 数据处理工具栏
        self.data_process_toolbar.addWidget(self.data_process_toolbar_label)
        self.data_process_toolbar.addAction(self.data_process_import_video_action)
        self.data_process_toolbar.addAction(self.data_process_setting_action)
        self.data_process_toolbar.addAction(self.data_process_execute_action)
        # 关闭此时不能打开的控件
        self.robot_toolbar.setEnabled(False)
        self.live_video_box_screen_action.setEnabled(False)
        self.live_video_capture_action.setEnabled(False)
        self.live_video_setting_action.setEnabled(False)


    # 展示窗口状态栏
    def show_window_status(self):
        self.window_status_text = '机械臂:[%s];    视频帧率:[%s];    action_tab页面:[%s];    case_tab页面:[%s]' \
                                  % (WindowStatus.robot_connect_status, WindowStatus.video_frame_rate,
                                     WindowStatus.action_tab_status, WindowStatus.case_tab_status)
        self.status_bar.showMessage(self.window_status_text)


    # 视频播放框架
    def video_play_frame(self):
        self.main_show_tab_widget = MainShowTabWidget(self.central_widget, camera_width=self.camera_image_width, camera_height=self.camera_image_height)
        self.main_show_tab_widget.signal[str].connect(self.recv_video_label_signal)


    # case展示
    def show_case(self):
        self.show_tab_widget = ShowTabWidget(self.central_widget)
        self.show_tab_widget.setEnabled(False)
        self.show_tab_widget.signal[str].connect(self.recv_show_tab_widget_signal)


    # 工程栏
    def project_bar(self):
        self.project_bar_widget = ProjectBar(self.central_widget, GloVar.project_path)
        self.project_bar_widget.signal[str].connect(self.recv_project_bar_signal)


    # 控制台输出
    def output_text(self):
        self.console = QTextEdit(self.central_widget)
        # 滚动条宽度设置
        # self.console.verticalScrollBar().setStyleSheet("QScrollBar{width:10px;}")
        self.console.horizontalScrollBar().setStyleSheet("QScrollBar{height:10px;}")
        self.console.setReadOnly(True)
        self.console.ensureCursorVisible()
        self.console.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.console.setWordWrapMode(QTextOption.NoWrap)
        # 字体型号
        self.console.setFont(QFont('monospaced', 13))
        # 字体粗细
        self.console.setStyleSheet('font-weight:bold')


    # 更新控制台内容
    def update_text(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()


    # 接收实时流的相关参数调整(暂时没有用到)
    def recv_camera_param_setting_widget(self, signal_str):
        if signal_str.startswith('exposure_time>'):
            pass
        elif signal_str.startswith('gain>'):
            gain = int(signal_str.split('gain>')[1])
            Thread(target=self.robot.video.cam.Gain.set, args=(gain,)).start()
        elif signal_str.startswith('picture_path>'):
            self.picture_path = signal_str.split('>')[1]
            self.main_show_tab_widget.video_tab.video_label.picture_path = self.picture_path
            GloVar.project_picture_path = self.picture_path


    # 接收本地视频帧率调整的信号
    def recv_frame_rate_adjust_widget(self, signal_str):
        if signal_str.startswith('frame_rate_adjust>'):
            frame_rate = int(signal_str.split('frame_rate_adjust>')[1])
            self.main_show_tab_widget.video_tab.video_label.timer_video.frequent = frame_rate
            WindowStatus.video_frame_rate = str(frame_rate) + 'fps'


    # 视频标签控件接收函数(接收到信息后需要进行的操作)
    def recv_video_label_signal(self, info_str):
        # 先将字符串转化为list
        # 当list为两个元素时 : 第一个为点击动作类型, 第二个为点击动作坐标
        # 当list为三个元素时 : 第一个为滑动动作类型, 第二个为起点坐标, 第三个为终止点坐标
        info_list = eval(info_str)
        # 如果是添加动作时, 不作操作(只添加动作)
        if MotionAction.add_action_flag is True:
            if info_list[0] in [RobotArmAction.uArm_click, RobotArmAction.uArm_double_click, RobotArmAction.uArm_long_click, RobotArmAction.uArm_slide]:
                position_str = str(info_list[1])
                position_tuple = info_list[1]
            else: # 为了不让position_str有警告(无具体意义)
                position_str = '0, 0'
                position_tuple = (0.0, 0.0)
            # 添加动作取完坐标后, 需要在子窗口中添加坐标信息, 以及回传坐标信息
            self.show_tab_widget.action_tab.add_action_window.widget.action_tab.points.setText(position_str)
            self.show_tab_widget.action_tab.add_action_window.widget.action_tab.info_dict[MotionAction.points] = position_tuple
            self.show_tab_widget.action_tab.add_action_window.setHidden(False)
            MotionAction.add_action_flag = False
        # 正常点击时会直接执行动作
        else:
            # 根据返回值形成info_dict字典
            info_dict = {MotionAction.des_text: info_list[0],
                         MotionAction.action_type: info_list[0],
                         MotionAction.speed: 150,
                         MotionAction.points: info_list[1],
                         MotionAction.leave: 1,
                         MotionAction.trigger: 0}
            if GloVar.request_status is None:
                Logger('[当前还有正在执行的动作, 请稍后执行!]')
                return
            # 脚本录制操作
            if RobotArmAction.uArm_with_record is True:
                self.show_tab_widget.action_tab.add_action_item(info_dict=info_dict)
            info_dict['execute_action'] = 'motion_action'
            info_dict['base'] = (RobotArmParam.base_x_point, RobotArmParam.base_y_point, RobotArmParam.base_z_point)
            GloVar.post_info_list = []
            GloVar.post_info_list.append('start')
            GloVar.post_info_list.append(info_dict)
            GloVar.post_info_list.append('stop')
            Thread(target=self.robot.execute_actions, args=(GloVar.post_info_list,)).start()


    # 接收show_tab_widget的信号
    def recv_show_tab_widget_signal(self, signal_str):
        # 执行选中所有动作动作
        if signal_str.startswith('play_actions>'):
            Thread(target=self.robot.execute_actions, args=(GloVar.post_info_list,)).start()
        # 执行一条case动作
        elif signal_str.startswith('play_single_case>'):
            Thread(target=self.robot.execute_actions, args=(GloVar.post_info_list,)).start()
        # 添加action控件时候, 设置动作标志位
        elif signal_str.startswith('action_tab_action>'):
            # 消除留在视频界面的印记
            self.main_show_tab_widget.video_tab.video_label.x1 = self.main_show_tab_widget.video_tab.video_label.x0
            self.main_show_tab_widget.video_tab.video_label.y1 = self.main_show_tab_widget.video_tab.video_label.y0
            RobotArmAction.uArm_action_type = signal_str.split('>')[1]
        else:
            pass


    # 接收工具栏信号
    def recv_project_bar_signal(self, signal_str):
        # 打开图片
        if signal_str.startswith('open_picture>'):
            self.main_show_tab_widget.picture_tab.picture_path = signal_str.split('open_picture>')[1]
            # 自动跳转到picture页面
            self.main_show_tab_widget.setCurrentWidget(self.main_show_tab_widget.picture_tab)
            self.main_show_tab_widget.picture_tab.show_picture()
        # 打开报告(同时打开报告页面和文本页面)
        elif signal_str.startswith('open_report>'):
            self.main_show_tab_widget.report_tab.report_path = signal_str.split('open_report>')[1]
            # 自动跳转到report页面
            self.main_show_tab_widget.setCurrentWidget(self.main_show_tab_widget.report_tab)
            self.main_show_tab_widget.report_tab.show_html()
        # 打开文本
        elif signal_str.startswith('open_text>'):
            self.main_show_tab_widget.text_tab.text_path = signal_str.split('open_text>')[1]
            # 自动跳到text页面
            self.main_show_tab_widget.setCurrentWidget(self.main_show_tab_widget.text_tab)
            self.main_show_tab_widget.text_tab.show_text()


    '''以下内容为实时流工具栏相关操作'''
    # 切换摄像头状态
    def switch_camera_status(self):
        # 本地视频工具栏&数据处理工具栏(关闭一些按钮)
        self.local_video_setting_action.setEnabled(False)
        self.data_process_setting_action.setEnabled(False)
        self.data_process_execute_action.setEnabled(False)
        # 是否需要进行数据检测的标志位复位
        self.need_detect_data_flag = False
        if self.main_show_tab_widget.video_tab.video_label.camera_status == self.main_show_tab_widget.video_tab.video_label.camera_closed:
            # 设置当前tab页为视频页面
            self.main_show_tab_widget.setCurrentWidget(self.main_show_tab_widget.video_tab)
            # 打开此时需要打开的控件
            self.robot_toolbar.setEnabled(True)
            self.live_video_box_screen_action.setEnabled(True)
            self.live_video_capture_action.setEnabled(True)
            self.live_video_setting_action.setEnabled(True)
            # 侧边case框
            self.show_tab_widget.setEnabled(True)
            self.local_video_setting_action.setEnabled(False)
            self.live_video_switch_camera_status_action.setIcon(QIcon(IconPath.Icon_live_video_close_camera))
            # 设置提示
            self.live_video_switch_camera_status_action.setToolTip('close_camera')
        else:
            # 关闭此时不能打开的控件
            self.robot_toolbar.setEnabled(False)
            self.live_video_box_screen_action.setEnabled(False)
            self.live_video_capture_action.setEnabled(False)
            self.live_video_setting_action.setEnabled(False)
            self.show_tab_widget.setEnabled(False)
            self.live_video_switch_camera_status_action.setIcon(QIcon(IconPath.Icon_live_video_open_camera))
            self.live_video_switch_camera_status_action.setToolTip('open_camera')
        self.main_show_tab_widget.video_tab.video_label.switch_camera_status()


    # 拍照/截屏 动作
    def screen_shot(self):
        # 视频流未打开时不允许拍照
        if self.main_show_tab_widget.video_tab.video_label.camera_status == self.main_show_tab_widget.video_tab.video_label.camera_closed:
            QMessageBox.warning(self, "警告", "还没有开启视频流! 请打开视频流!", QMessageBox.Yes | QMessageBox.No)
        else:
            Thread(target=self.screen_capture_thread, args=()).start()


    # 摄像头截屏线程
    def screen_capture_thread(self, capture_type='jpg'):
        capture_path = MergePath([self.picture_path, 'screen_shot']).merged_path
        if os.path.exists(capture_path) is False:
            os.makedirs(capture_path)
        capture_name = str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + '.' + capture_type
        capture_name = MergePath([capture_path, capture_name]).merged_path
        image = self.main_show_tab_widget.video_tab.video_label.image.copy()
        cv2.imencode('.' + capture_type, image)[1].tofile(capture_name)
        Logger('[截取的图片为]: %s' % capture_name)


    # 框选车机屏幕大小
    def box_screen(self):
        # 视频流未打开时不允许框选车机屏幕
        if self.main_show_tab_widget.video_tab.video_label.camera_status == self.main_show_tab_widget.video_tab.video_label.camera_closed:
            QMessageBox.warning(self, "警告", "请先打开视频流! 之后再框选屏幕!", QMessageBox.Yes | QMessageBox.No)
        else:
            reply = QMessageBox.question(self, '提示', '是否要框选车机屏幕?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                # 清除上次无关的鼠标操作产生的起止点
                self.main_show_tab_widget.video_tab.video_label.y1 = self.main_show_tab_widget.video_tab.video_label.y0
                self.main_show_tab_widget.video_tab.video_label.x1 = self.main_show_tab_widget.video_tab.video_label.x0
                self.main_show_tab_widget.video_tab.video_label.setCursor(Qt.CrossCursor)
                RobotOther.select_template_flag = True
                GloVar.box_screen_flag = True
                RobotArmAction.uArm_action_type = None


    # 设置实时流相机参数
    def set_camera_param(self):
        self.camera_param_setting_widget.show()
        self.camera_param_setting_widget.exec()


    '''以下为机械臂工具栏相关操作'''
    # 机械臂动作线程
    def uArm_action_event_thread(self, action):
        if action == RobotArmAction.uArm_click:
            # 单击标志
            RobotArmAction.uArm_action_type = RobotArmAction.uArm_click
        elif action == RobotArmAction.uArm_double_click:
            # 双击标志
            RobotArmAction.uArm_action_type = RobotArmAction.uArm_double_click
        elif action == RobotArmAction.uArm_long_click:
            # 长按标志
            RobotArmAction.uArm_action_type = RobotArmAction.uArm_long_click
        elif action == RobotArmAction.uArm_slide:
            # 滑动标志(避免出现乱画直线的情况)
            self.main_show_tab_widget.video_tab.video_label.x1 = self.main_show_tab_widget.video_tab.video_label.x0
            self.main_show_tab_widget.video_tab.video_label.y1 = self.main_show_tab_widget.video_tab.video_label.y0
            RobotArmAction.uArm_action_type = RobotArmAction.uArm_slide
        elif action == RobotArmAction.uArm_lock:
            # 机械臂锁定
            Thread(target=self.robot.servo_attach, args=()).start()
        elif action == RobotArmAction.uArm_unlock:
            # 机械臂解锁
            Thread(target=self.robot.servo_detach, args=()).start()
        elif action == RobotArmAction.uArm_get_position:
            # 获取机械臂当前坐标
            Thread(target=self.robot.get_position, args=()).start()
        else:
            Logger('当前不支持[%s]这个动作' % action)


    # 机械臂动作事件(需要先框选屏幕大小)
    def uArm_action_event(self, action):
        if sum(self.main_show_tab_widget.video_tab.video_label.box_screen_size) == 0:
            QMessageBox.about(self, "提示", "请先框选屏幕大小")
            return
        else:
            Thread(target=self.uArm_action_event_thread, args=(action,)).start()


    # 正在进行的操作是否需要录入脚本(默认参数为None; 当有参数时, 将record_status的状态传给uArm_action.uArm_with_record)
    def switch_uArm_with_record_status(self, record_status=None):
        # 视频流状态下, 按下录制脚本按钮(脚本录制状态切换)
        if record_status is not None:
            # 状态反转
            RobotArmAction.uArm_with_record = bool(1 - record_status)
        if RobotArmAction.uArm_with_record is False:
            RobotArmAction.uArm_with_record = True
            self.robot_with_record_action.setIcon(QIcon(IconPath.Icon_robot_without_record))
            self.robot_with_record_action.setToolTip('without_record')
            if self.main_show_tab_widget.video_tab.video_label.video_play_flag is False:
                Logger('<脚本录制打开--以下操作将会被保存为action>')
        else:
            RobotArmAction.uArm_with_record = False
            self.robot_with_record_action.setIcon(QIcon(IconPath.Icon_robot_with_record))
            self.robot_with_record_action.setToolTip('with_record')
            if self.main_show_tab_widget.video_tab.video_label.video_play_flag is False:
                Logger('<脚本录制关闭--以下操作将不会被保存为action>')


    '''本地视频播放工具栏相关操作'''
    # 本地视频播放
    def import_local_video(self):
        # 先停掉视频
        self.main_show_tab_widget.video_tab.video_label.timer_video.stop()
        # 在选择视频的时候判断此时实时流是否开启, 如果为True说明开启着, 如果False说明关闭着
        camera_opened_flag = False
        # 按下选择视频按钮, 判断当前视频流是否开启, 若开启着, 则先停止视频流/再判断是否有选择目录(没有选择目录的话, 再次恢复开启实时流状态)
        # 停止视频流, 并切换视频流按钮(打开/关闭视频流)状态
        if self.main_show_tab_widget.video_tab.video_label.camera_status == self.main_show_tab_widget.video_tab.video_label.camera_opened:
            camera_opened_flag = True
            self.switch_camera_status()
        self.get_path = QFileDialog.getExistingDirectory(self, '选择文件夹', self.videos_path)
        if self.get_path:
            if self.videos_path != self.get_path:
                # 保存此次打开的路径(路径默认上一次)
                self.videos_path = self.get_path
                Profile(type='write', file=GloVar.config_file_path, section='param', option='videos_path', value=self.get_path)
            RobotArmAction.uArm_action_type = None
            videos, videos_title = [], []
            for home, dirs, files in os.walk(self.get_path):
                for file in files:
                    # 判断视频文件(通过后缀名)
                    (file_text, extension) = os.path.splitext(file)
                    if extension in ['.mp4', '.MP4', '.avi', '.AVI']:
                        # 文件名列表, 包含完整路径
                        file = MergePath([home, file]).merged_path
                        videos.append(file)
                        videos_title.append(file)
            # 传入videos & videos_title
            self.main_show_tab_widget.video_tab.video_label.videos = videos
            self.main_show_tab_widget.video_tab.video_label.videos_title = videos_title
            # 关闭此时不能打开的控件
            self.robot_toolbar.setEnabled(False)
            self.live_video_box_screen_action.setEnabled(False)
            self.live_video_capture_action.setEnabled(False)
            self.live_video_setting_action.setEnabled(False)
            self.show_tab_widget.setEnabled(False)

            self.local_video_setting_action.setEnabled(True)
            # 此时可以非使能设置按钮和执行数据处理按钮
            self.data_process_execute_action.setEnabled(False)
            self.data_process_setting_action.setEnabled(False)
            # 是否需要进行数据检测的标志位复位
            self.need_detect_data_flag = False

            # 强制关闭脚本录制状态
            self.switch_uArm_with_record_status(record_status=False)
            # 离线视频播放
            self.main_show_tab_widget.video_tab.video_label.import_local_video()
        else:
            Logger('没有选择视频路径!')
            # 如果没有选择路径, 实时视频流恢复之前状态
            if camera_opened_flag is True:
                self.switch_camera_status()
            # 如果没有选择路径, 定时器恢复之前状态
            if self.main_show_tab_widget.video_tab.video_label.video_status == self.main_show_tab_widget.video_tab.video_label.STATUS_PLAYING:
                self.main_show_tab_widget.video_tab.video_label.timer_video.start()


    # 设置本地视频帧率
    def set_frame_rate(self):
        self.frame_rate_adjust_widget.show()
        self.frame_rate_adjust_widget.exec()


    '''数据处理相关操作'''
    # 数据处理导入视频
    def data_process_import_video(self):
        # 先停掉视频
        self.main_show_tab_widget.video_tab.video_label.timer_video.stop()
        # 在选择视频的时候判断此时实时流是否开启, 如果为True说明开启着, 如果False说明关闭着
        camera_opened_flag = False
        # 按下选择视频按钮, 判断当前视频流是否开启, 若开启着, 则先停止视频流/再判断是否有选择目录(没有选择目录的话, 再次恢复开启实时流状态)
        # 停止视频流, 并切换视频流按钮(打开/关闭视频流)状态
        if self.main_show_tab_widget.video_tab.video_label.camera_status == self.main_show_tab_widget.video_tab.video_label.camera_opened:
            camera_opened_flag = True
            self.switch_camera_status()
        # 获取需要处理的视频所在路径
        self.get_path = QFileDialog.getExistingDirectory(self, '选择文件夹', self.videos_path)
        if self.get_path:
            if self.videos_path != self.get_path:
                # 保存此次打开的路径(路径默认上一次)
                self.videos_path = self.get_path
                Profile(type='write', file=GloVar.config_file_path, section='param', option='videos_path', value=self.get_path)
            RobotArmAction.uArm_action_type = None
            # 设置不可框选模板&鼠标变为标准鼠标
            self.main_show_tab_widget.video_tab.video_label.setCursor(Qt.ArrowCursor)
            RobotOther.select_template_flag = False
            # 关闭此时不能打开的控件
            self.robot_toolbar.setEnabled(False)
            self.live_video_box_screen_action.setEnabled(False)
            self.live_video_capture_action.setEnabled(False)
            self.live_video_setting_action.setEnabled(False)
            self.show_tab_widget.setEnabled(False)
            self.local_video_setting_action.setEnabled(False)
            self.data_process_setting_action.setEnabled(True)
            self.data_process_execute_action.setEnabled(False)
            # 是否需要进行数据检测的标志位复位
            self.need_detect_data_flag = False
            # 获取需要展示出来的视频
            videos, videos_title, videos_without_template = [], [], []
            for home, dirs, files in os.walk(self.get_path):
                if len(files) > 0:
                    # 合并路径
                    file = MergePath([home, '1.mp4']).merged_path
                    videos.append(file)
                    videos_title.append(file)
            # 遍历出来没有对应模板的视频文件
            for video in videos:
                template_path = video.replace('/video/', '/picture/').split('.')[0] + '.jpg'
                # 模板图片不存在
                if os.path.exists(template_path) is False:
                    videos_without_template.append(video)
            if len(videos_without_template) > 0:
                # 将videos_without_template作为videos
                self.main_show_tab_widget.video_tab.video_label.videos = videos_without_template
                self.main_show_tab_widget.video_tab.video_label.videos_title = videos_without_template
                self.main_show_tab_widget.video_tab.video_label.import_data_process_with_video()
                # 强制关闭脚本录制状态
                self.switch_uArm_with_record_status(record_status=False)
                # 同时启动模板检测
                self.need_detect_data_flag = True
                # 打开数据处理标志位
                RobotOther.data_process_flag = True
                Thread(target=self.detect_data_is_ready, args=()).start()
            else:
                Logger('所有视频都有其对应的模板图片, 可以开始处理数据!')
                # 此时可以使能执行数据处理按钮
                self.data_process_execute_action.setEnabled(True)
                self.data_process_setting_action.setEnabled(False)
                self.live_video_switch_camera_status_action.setIcon(QIcon(IconPath.Icon_live_video_open_camera))
                self.live_video_switch_camera_status_action.setToolTip('open_camera')
                self.main_show_tab_widget.video_tab.video_label.import_data_process_without_video()
        else:
            Logger('没有选择视频路径, 数据处理取消!')
            # 如果没有选择路径, 实时视频流恢复之前状态
            if camera_opened_flag is True:
                self.switch_camera_status()
            # 如果没有选择路径, 定时器恢复之前状态
            if self.main_show_tab_widget.video_tab.video_label.video_status == self.main_show_tab_widget.video_tab.video_label.STATUS_PLAYING:
                self.main_show_tab_widget.video_tab.video_label.timer_video.start()


    # 数据处理执行函数
    def data_process_execute(self):
        # 先关掉正在播放的视频
        self.main_show_tab_widget.video_tab.video_label.timer_video.stop()
        self.live_video_switch_camera_status_action.setIcon(QIcon(IconPath.Icon_live_video_open_camera))
        self.live_video_switch_camera_status_action.setToolTip('open_camera')
        # 调用video_label中的数据执行操作
        self.main_show_tab_widget.video_tab.video_label.data_process_execute()
        # 此处调用数据处理函数
        video_path = self.get_path
        test = GetStartupTime(video_path=video_path)
        Thread(target=test.data_processing, args=()).start()
        Thread(target=self.data_process_finished, args=()).start()


    # 检测数据有没有准备(准备好就可以开始执行数据处理)
    def detect_data_is_ready(self):
        # 用来判断数据是否准备完毕(也就是视频对应的模板图片是否全部存在)
        flag = False
        while self.need_detect_data_flag is True:
            # 没有相应模板的视频文件列表(用来判断是否可以进行数据处理)
            videos_without_template = []
            # 遍历出来没有对应模板的视频文件
            for video in self.main_show_tab_widget.video_tab.video_label.videos:
                # template_path = video.replace('/video/', '/picture/').split('.')[0] + '.jpg'
                # 适应数据处理
                template_path = os.path.split(video.replace('/video/', '/picture/'))[0] + '.jpg'
                # 模板图片不存在
                if os.path.exists(template_path) is False:
                    videos_without_template.append(video)
            if len(videos_without_template) > 0:
                time.sleep(0.2)
            else:
                flag = True
                break
        # 是否需要进行数据检测的标志位复位
        self.need_detect_data_flag = False
        if flag is True:
            # 跳出后(显示数据已经准备好)
            Logger('所有视频都有其对应的模板图片, 可以开始处理数据!')
            # 此时可以使能执行数据处理按钮
            self.data_process_execute_action.setEnabled(True)
            self.data_process_setting_action.setEnabled(False)
            self.live_video_switch_camera_status_action.setIcon(QIcon(IconPath.Icon_live_video_open_camera))
            self.live_video_switch_camera_status_action.setToolTip('open_camera')
            self.main_show_tab_widget.video_tab.video_label.import_data_process_without_video()


    # 数据处理结束
    def data_process_finished(self):
        while True:
            if RobotOther.data_process_finished_flag is True:
                flag = True
                RobotOther.data_process_finished_flag = False
                break
            else:
                time.sleep(0.2)
        if flag is True:
            # 关闭视频展示定时器
            self.main_show_tab_widget.video_tab.video_label.timer_video.stop()
            # 此时可以使能执行数据处理按钮
            self.data_process_execute_action.setEnabled(False)
            self.data_process_setting_action.setEnabled(False)
            self.live_video_switch_camera_status_action.setIcon(QIcon(IconPath.Icon_live_video_open_camera))
            self.live_video_switch_camera_status_action.setToolTip('open_camera')
            self.main_show_tab_widget.video_tab.video_label.data_process_finished()


    '''以下重写窗口事件'''
    # 重写窗口关闭时间
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '本程序', '是否要退出程序?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 关闭摄像头
            self.robot.video.stop_record_thread()
            self.main_show_tab_widget.video_tab.video_label.timer_camera_image.stop()
            self.timer_window_status.stop()
            self.main_show_tab_widget.video_tab.video_label.slider_thread.stop()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = UiMainWindow()
    gui.setupUi()
    gui.show()
    sys.exit(app.exec_())