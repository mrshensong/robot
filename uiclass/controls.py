import time
from threading import Thread
from PyQt5.QtWidgets import QWidget, QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QCheckBox, QLineEdit, QLabel, QToolButton, QSlider, QSpinBox, QPushButton, QFileDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import GloVar, IconPath, RobotArmAction, RecordAction, SleepAction, Logger, MotionAction, Profile

# 自定义动作展示控件(action)
class ActionControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(ActionControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 动作类型
        self.action_type = info_dict[MotionAction.action_type]
        # 通过字典中的坐标信息, 来设置需要在控件中显示的坐标信息(字符串类型)
        self.other_param = '速度:' + str(info_dict[MotionAction.speed]) +\
                           ' 收回:' + str(info_dict[MotionAction.leave]) +\
                           ' 触发:' + str(info_dict[MotionAction.trigger])
        # 先将坐标元素转为字符串类型
        points = info_dict[MotionAction.points]
        if points:
            self.points_text = str(tuple(points))
        else:  # 无实际意义(单纯为了不让代码出现警告)
            self.points_text = '(0.0, 0.0)'
        # 描述text
        self.des_text = info_dict[MotionAction.des_text]
        # 判断是真的新建action还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.initUI()
        self.describe_action()

    def initUI(self):

        self.check_box = QCheckBox()

        if self.action_type == RobotArmAction.uArm_click:
            pix_map = QPixmap(IconPath.Icon_robot_click)
        elif self.action_type == RobotArmAction.uArm_double_click:
            pix_map = QPixmap(IconPath.Icon_robot_double_click)
        elif self.action_type == RobotArmAction.uArm_long_click:
            pix_map = QPixmap(IconPath.Icon_robot_long_click)
        elif self.action_type == RobotArmAction.uArm_slide:
            pix_map = QPixmap(IconPath.Icon_robot_slide)
        else:
            pix_map = QPixmap(IconPath.Icon_robot_click)
        self.type_label = QLabel(self)
        self.type_label.setPixmap(pix_map)

        self.des_line_edit = QLineEdit(self)
        self.des_line_edit.setReadOnly(True)
        self.des_line_edit.setText(self.des_text)
        self.points_line_edit = QLineEdit(self)
        self.points_line_edit.setReadOnly(True)
        self.points_line_edit.setText(self.points_text)
        self.other_param_edit = QLineEdit(self)
        self.other_param_edit.setReadOnly(True)
        self.other_param_edit.setText(self.other_param)
        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.des_line_edit)
        self.v_box.addWidget(self.points_line_edit)
        self.v_box.addWidget(self.other_param_edit)

        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.action_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.action_delete_item)

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.type_label)
        self.h_box.addLayout(self.v_box)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)

        self.setLayout(self.h_box)
        self.setMaximumWidth(400)


    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)


    # 执行单个动作的具体操作
    def play_action_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('action_execute_item>' + str(self.id))


    # 执行单个动作(新建线程/控件中的执行按钮)
    def action_execute_item(self):
        Thread(target=self.play_action_item, args=()).start()


    # 删除单个动作(控件中的删除按钮)
    def action_delete_item(self):
        # 打印删除信息
        if self.des_line_edit.text() == '':
            Logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: 无描述信息'.format(self.str_decorate(self.id), self.str_decorate(self.action_type), str(self.points_text)))
        else:
            Logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: {}'.format(self.str_decorate(self.id), self.str_decorate(self.action_type), str(self.points_text), self.des_line_edit.text()))
        self.signal.emit('action_delete_item>' + str(self.id))


    # 打印控件信息
    def describe_action(self):
        # 如果确实是添加动作(而非导入case中的动作)
        if self.new_control_flag is True:
            # 打印新建动作信息
            if self.des_text == '':
                Logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: 无描述信息'.format(self.str_decorate(self.id), self.str_decorate(self.action_type), self.points_text))
            else:
                Logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: {}'.format(self.str_decorate(self.id), self.str_decorate(self.action_type), self.points_text, self.des_text))

# 摄像头录制开始和停止动作展示控件(camera_start/camera_stop)
class RecordControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(RecordControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        # 视频绝对路径
        self.video_type = info_dict[RecordAction.video_type]
        # 视频名称
        self.video_name = info_dict[RecordAction.video_name] + '.mp4'
        # 录像类型(record_start/record_stop)
        self.record_type = info_dict[RecordAction.record_status]
        # 标准时间
        self.standard_time = info_dict[RecordAction.standard_time]
        self.initUI()
        self.describe_record()


    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 摄像机图标
        self.video_camera_label = QLabel(self)
        self.video_camera_label.setPixmap(QPixmap(IconPath.Icon_custom_video_camera))
        # 显示视频类型和name(如:type/name.mp4)
        self.video_type_and_name_text = QLineEdit(self)
        self.video_type_and_name_text.setReadOnly(True)
        text = self.video_type + '/' + self.video_name
        self.video_type_and_name_text.setText(text)
        # 显示视频标准时间
        self.video_standard_time_text = QLineEdit(self)
        self.video_standard_time_text.setReadOnly(True)
        self.video_standard_time_text.setText('标准时间(ms): ' + self.standard_time)
        # 摄像机录像开始和停止text显示
        self.video_camera_status_text = QLineEdit(self)
        self.video_camera_status_text.setReadOnly(True)
        # 视频开始和停止显示
        if self.record_type == RecordAction.record_start:
            status = 'record: Start'
        else:
            status = 'record: Stop'
        self.video_camera_status_text.setText(status)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.record_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.record_delete_item)
        # 竖向布局
        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.video_type_and_name_text)
        self.v_box.addWidget(self.video_standard_time_text)
        self.v_box.addWidget(self.video_camera_status_text)
        # 横向布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.video_camera_label)
        self.h_box.addLayout(self.v_box)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)


    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)


    # 执行单个动作的具体操作
    def play_record_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('record_execute_item>' + str(self.id))


    # 执行单个动作(新建线程/控件中的执行按钮)
    def record_execute_item(self):
        # 每执行一次都需要获取当前时间(作为文件夹)
        GloVar.current_time = time.strftime('%H-%M-%S', time.localtime(time.time()))
        Thread(target=self.play_record_item, args=()).start()


    # 删除单个动作(控件中的删除按钮)
    def record_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}录像动作{}'.format(self.str_decorate(self.id), self.str_decorate(RecordAction.record_status), self.str_decorate(self.record_type)))
        self.signal.emit('record_delete_item>' + str(self.id))


    # 打印控件信息
    def describe_record(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}录像动作{}'.format(self.str_decorate(self.id), self.str_decorate(RecordAction.record_status), self.str_decorate(self.record_type)))

# 延时动作展示控件(sleep)
class SleepControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(SleepControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.sleep_time = info_dict[SleepAction.sleep_time]
        self.initUI()
        self.describe_sleep()


    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 延时图标
        self.sleep_icon_label = QLabel(self)
        self.sleep_icon_label.setPixmap(QPixmap(IconPath.Icon_custom_sleep))
        # 延时text显示
        status = 'sleep(s): ' + str(self.sleep_time)
        self.sleep_des_text = QLineEdit(self)
        self.sleep_des_text.setReadOnly(True)
        self.sleep_des_text.setText(status)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.sleep_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.sleep_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.sleep_icon_label)
        self.h_box.addWidget(self.sleep_des_text)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)


    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)


    # 执行单个动作的具体操作
    def play_sleep_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('sleep_execute_item>' + str(self.id))


    # 执行单个动作(新建线程/控件中的执行按钮)
    def sleep_execute_item(self):
        Thread(target=self.play_sleep_item, args=()).start()


    # 删除单个动作(控件中的删除按钮)
    def sleep_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}延时时间{}'.format(self.str_decorate(self.id), self.str_decorate(SleepAction.sleep_time), self.str_decorate(self.sleep_time)))
        self.signal.emit('sleep_delete_item>' + str(self.id))


    # 打印控件信息
    def describe_sleep(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}延时时间{}'.format(self.str_decorate(self.id), self.str_decorate(SleepAction.sleep_time), self.str_decorate(self.sleep_time)))

# 自定义动作展示控件(case)
class CaseControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, case_file):
        super(CaseControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        self.case_file = case_file
        self.initUI()


    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # case名
        case_name = self.case_file.split('/')[-1]
        self.case_name_edit = QLineEdit(self)
        self.case_name_edit.setReadOnly(True)
        self.case_name_edit.setText(case_name)
        # case图标
        self.case_icon_label = QLabel(self)
        self.case_icon_label.setPixmap(QPixmap(IconPath.Icon_custom_case))
        # 播放按钮
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.play_single_case)
        # 删除按钮
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.delete_case)

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.case_icon_label)
        self.h_box.addWidget(self.case_name_edit)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(350)


    # 当前控件双击事件后(发送信号到父控件, 发送当前id)
    def mouseDoubleClickEvent(self, event):
        self.signal.emit('open_case>' + str(self.id))


    # 执行单个case
    def play_single_case(self):
        # 每执行一次都需要获取当前时间(作为文件夹)
        GloVar.current_time = time.strftime('%H-%M-%S', time.localtime(time.time()))
        self.signal.emit('play_single_case>' + str(self.id))


    # 删除单个case
    def delete_case(self):
        # 打印删除信息
        Logger('删除case: %s' % self.case_file)
        self.signal.emit('delete_case>' + str(self.id))


# 相机参数调节控件
class CameraParamAdjustControl(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent, use_external_camera_flag):
        super(CameraParamAdjustControl, self).__init__(parent)
        self.parent = parent
        self.use_external_camera_flag = use_external_camera_flag
        self.picture_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='picture_path').value
        self.exposure_time_value = 1000
        self.gain_value = 0
        self.stable_frame_rate_flag = True
        self.initUI()


    def initUI(self):
        # 控件总布局
        self.general_layout = QVBoxLayout()
        # 曝光增益使用栅格布局
        self.grid_layout = QGridLayout()
        # 确认button布局
        self.sure_button_layout = QHBoxLayout()

        # 设置曝光
        self.exposure_time_label = QLabel(self)
        self.exposure_time_label.setText('曝光: ')
        self.exposure_time_slider = QSlider(Qt.Horizontal, self)
        self.exposure_time_slider.setRange(1000, 100000)
        self.exposure_time_slider.valueChanged.connect(self.connect_exposure_time_slider)
        self.exposure_time_spinbox = QSpinBox(self)
        self.exposure_time_spinbox.setRange(1000, 100000)
        self.exposure_time_spinbox.valueChanged.connect(self.connect_exposure_time_spinbox)
        # 用户不可以修改曝光(关系到帧率)
        self.exposure_time_slider.setEnabled(False)
        self.exposure_time_spinbox.setEnabled(False)
        self.grid_layout.addWidget(self.exposure_time_label, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.exposure_time_slider, 0, 1, 1, 5)
        self.grid_layout.addWidget(self.exposure_time_spinbox, 0, 6, 1, 1)
        # 设置增益
        self.gain_label = QLabel(self)
        self.gain_label.setText('增益: ')
        self.gain_slider = QSlider(Qt.Horizontal, self)
        self.gain_slider.setRange(0, 24)
        self.gain_slider.valueChanged.connect(self.connect_gain_slider)
        self.gain_spinbox = QSpinBox(self)
        self.gain_spinbox.setRange(0, 24)
        self.gain_spinbox.valueChanged.connect(self.connect_gain_spinbox)
        if self.use_external_camera_flag is True:
            self.gain_slider.setEnabled(True)
            self.gain_spinbox.setEnabled(True)
        else:
            self.gain_slider.setEnabled(False)
            self.gain_spinbox.setEnabled(False)
        self.grid_layout.addWidget(self.gain_label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.gain_slider, 1, 1, 1, 5)
        self.grid_layout.addWidget(self.gain_spinbox, 1, 6, 1, 1)
        # 设置case执行过程中是否需要关闭界面实时流(关闭实时流可以保证录制视频不丢帧)
        self.stable_frame_rate_label = QLabel(self)
        self.stable_frame_rate_label.setText('稳定帧率: ')
        self.stable_frame_rate_des = QLineEdit(self)
        self.stable_frame_rate_des.setReadOnly(True)
        self.stable_frame_rate_des.setText('开启状态,执行case过程中会暂停实时流,帧率稳定')
        self.stable_frame_rate_button = QPushButton(self)
        self.stable_frame_rate_button.setMaximumWidth(40)
        self.stable_frame_rate_button.clicked.connect(self.change_stable_frame_rate_status)
        self.stable_frame_rate_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
        self.grid_layout.addWidget(self.stable_frame_rate_label, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.stable_frame_rate_des, 2, 1, 1, 5)
        self.grid_layout.addWidget(self.stable_frame_rate_button, 2, 6, 1, 1)
        # 设置图片路径
        self.picture_path_show_label = QLabel(self)
        self.picture_path_show_label.setText('图片路径: ')
        self.picture_path_show_edit = QLineEdit(self)
        self.picture_path_show_edit.setReadOnly(True)
        self.picture_path_show_edit.setText(self.picture_path)
        self.picture_path_change_button = QPushButton('更改')
        self.picture_path_change_button.clicked.connect(self.connect_change_picture_path)
        self.grid_layout.addWidget(self.picture_path_show_label, 3, 0, 1, 1)
        self.grid_layout.addWidget(self.picture_path_show_edit, 3, 1, 1, 5)
        self.grid_layout.addWidget(self.picture_path_change_button, 3, 6, 1, 1)
        # 确定按钮
        self.sure_button = QPushButton('确定')
        self.sure_button.clicked.connect(self.connect_sure_button)
        self.sure_button_layout.addStretch(1)
        self.sure_button_layout.addWidget(self.sure_button)
        self.sure_button_layout.addStretch(1)

        self.general_layout.addLayout(self.grid_layout)
        self.general_layout.addSpacing(40)
        self.general_layout.addLayout(self.sure_button_layout)
        self.setLayout(self.general_layout)
        # 设置最小尺寸
        self.setMinimumWidth(400)
        self.setFixedWidth(750)
        self.setWindowTitle('摄像头参数')


    def connect_exposure_time_slider(self):
        self.exposure_time_value = int(self.exposure_time_slider.value())
        self.exposure_time_spinbox.setValue(self.exposure_time_value)
        self.signal.emit('exposure_time>' + str(self.exposure_time_value))


    def connect_exposure_time_spinbox(self):
        self.exposure_time_value = int(self.exposure_time_spinbox.value())
        self.exposure_time_slider.setValue(self.exposure_time_value)


    def connect_gain_slider(self):
        self.gain_value = int(self.gain_slider.value())
        self.gain_spinbox.setValue(self.gain_value)
        self.signal.emit('gain>' + str(self.gain_value))


    def connect_gain_spinbox(self):
        self.gain_value = int(self.gain_spinbox.value())
        self.gain_slider.setValue(self.gain_value)


    def change_stable_frame_rate_status(self):
        if self.stable_frame_rate_flag is True:
            self.stable_frame_rate_flag = False
            self.stable_frame_rate_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_off + ')}')
            self.stable_frame_rate_des.setText('关闭状态,执行case过程中会播放实时流,帧率不稳定')
        else:
            self.stable_frame_rate_flag = True
            self.stable_frame_rate_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
            self.stable_frame_rate_des.setText('打开状态,执行case过程中会暂停实时流,帧率稳定')


    def connect_change_picture_path(self):
        # 如果取消为''值
        self.picture_path = QFileDialog.getExistingDirectory(self, "浏览", self.picture_path, options=QFileDialog.DontUseNativeDialog)
        if self.picture_path:
            self.picture_path_show_edit.setText(self.picture_path)
            Profile(type='write', file=GloVar.config_file_path, section='param', option='picture_path', value=self.picture_path)
            Logger('修改保存图片路径为: %s' % self.picture_path)
            self.signal.emit('picture_path>' + self.picture_path)


    # 确认按钮按下触发事件
    def connect_sure_button(self):
        self.close()


    # 重写窗口关闭事件
    def closeEvent(self, event):
        self.close()


# 离线视频帧率调节
class FrameRateAdjustControl(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(FrameRateAdjustControl, self).__init__(parent)
        self.parent = parent
        self.stable_value = 30
        self.initUI()


    def initUI(self):
        self.general_layout = QVBoxLayout(self)

        # 设置帧率
        self.frame_rate_label = QLabel(self)
        self.frame_rate_label.setText('帧率: ')
        self.frame_rate_slider = QSlider(Qt.Horizontal, self)
        self.frame_rate_slider.setRange(30, 180)
        self.frame_rate_slider.valueChanged.connect(self.connect_frame_rate_slider)
        self.frame_rate_spinbox = QSpinBox(self)
        self.frame_rate_spinbox.setRange(30, 180)
        self.frame_rate_spinbox.valueChanged.connect(self.connect_frame_rate_spinbox)
        # 帧率调节横向布局
        self.frame_rate_h_layout = QHBoxLayout(self)
        self.frame_rate_h_layout.addWidget(self.frame_rate_label)
        self.frame_rate_h_layout.addWidget(self.frame_rate_slider)
        self.frame_rate_h_layout.addWidget(self.frame_rate_spinbox)
        # 确定按钮横向调节
        self.sure_button = QPushButton('确定', self)
        self.sure_button.clicked.connect(self.connect_sure_button)
        self.sure_button_h_layout = QHBoxLayout(self)
        self.sure_button_h_layout.addStretch(1)
        self.sure_button_h_layout.addWidget(self.sure_button)
        self.sure_button_h_layout.addStretch(1)
        # 全局布局
        self.general_layout.addLayout(self.frame_rate_h_layout)
        self.general_layout.addLayout(self.sure_button_h_layout)

        self.setLayout(self.general_layout)
        # 设置最小尺寸
        self.setMinimumWidth(400)
        self.setWindowTitle('离线视频帧率参数')


    def connect_frame_rate_slider(self):
        self.stable_value = int(self.frame_rate_slider.value())
        self.frame_rate_spinbox.setValue(self.stable_value)
        self.signal.emit('frame_rate_adjust>' + str(self.stable_value))


    def connect_frame_rate_spinbox(self):
        self.stable_value = int(self.frame_rate_spinbox.value())
        self.frame_rate_slider.setValue(self.stable_value)


    def connect_sure_button(self):
        self.close()


    # 重写关闭窗口时间
    def closeEvent(self, event):
        self.close()


# 添加视频动作表单中的框选模板控件
class SelectTemplateControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(SelectTemplateControl, self).__init__(parent)
        self.parent = parent
        self.initUI()


    def initUI(self):
        # 单选框
        self.check_box = QCheckBox(self)
        self.check_box.setCheckState(Qt.Unchecked)
        self.check_box.stateChanged.connect(self.connect_check_box)
        # 模板路径展示
        self.template_path = QLineEdit(self)
        self.template_path.setReadOnly(True)
        self.template_path.setPlaceholderText('模板路径')
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.setContentsMargins(0, 0, 0, 0)
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.template_path)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_box)


    def connect_check_box(self):
        if self.check_box.checkState() == Qt.Checked:
            self.signal.emit('checked_check_box>')
        elif self.check_box.checkState() == Qt.Unchecked:
            self.signal.emit('unchecked_check_box>')


    def clear(self):
        self.check_box.setCheckState(Qt.Unchecked)
        self.template_path.clear()
        self.template_path.setPlaceholderText('模板路径')
