import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import icon_path, uArm_action, add_action_window, video_action

# 自定义动作展示控件(action)
class Action_Control(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, type='click'):
        super(Action_Control, self).__init__(parent)
        self.parent = parent
        self.id = id
        self.type = type
        self.initUI()

    def initUI(self):

        self.check_box = QCheckBox()

        if self.type == uArm_action.uArm_click:
            pix_map = QPixmap(icon_path.Icon_robot_click)
        elif self.type == uArm_action.uArm_double_click:
            pix_map = QPixmap(icon_path.Icon_robot_double_click)
        elif self.type == uArm_action.uArm_long_click:
            pix_map = QPixmap(icon_path.Icon_robot_long_click)
        elif self.type == uArm_action.uArm_slide:
            pix_map = QPixmap(icon_path.Icon_robot_slide)
        else:
            pix_map = QPixmap(icon_path.Icon_robot_click)
        self.type_label = QLabel(self)
        self.type_label.setPixmap(pix_map)

        self.des_line_edit = QLineEdit(self)
        self.points_line_edit = QLineEdit(self)
        self.other_param_edit = QLineEdit(self)
        self.other_param_edit.setText('速度:150 收回:1 触发:1')
        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.des_line_edit)
        self.v_box.addWidget(self.points_line_edit)
        self.v_box.addWidget(self.other_param_edit)

        self.play_botton = QToolButton(self)
        self.play_botton.setToolTip('play')
        self.play_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_play + ')}')
        self.delete_botton = QToolButton(self)
        self.delete_botton.setToolTip('delete')
        self.delete_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_delete + ')}')

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.type_label)
        self.h_box.addLayout(self.v_box)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delete_botton)

        self.setLayout(self.h_box)


    def connect_check_box(self):
        print('the id is : ', self.id)


# 自定义动作展示控件(case)
class Case_Control(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id):
        super(Case_Control, self).__init__(parent)
        self.parent = parent
        self.id = id
        self.initUI()


    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # case名
        self.case_name_edit = QLineEdit(self)
        # 播放按钮
        self.play_botton = QToolButton(self)
        self.play_botton.setToolTip('play')
        self.play_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_play + ')}')

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.case_name_edit)
        self.setLayout(self.h_box)


    # 当前控件双击事件后(发送信号到父控件, 发送当前id)
    def mouseDoubleClickEvent(self, event):
        self.signal.emit('open_case>'+str(self.id))


# 摄像头录制开始和停止动作展示控件(camera_start/camera_stop)
class Camera_Record_Control(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, type=video_action.video_record_stop):
        super(Camera_Record_Control, self).__init__(parent)
        self.parent = parent
        self.id = id
        self.type = type
        self.initUI()


    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 摄像机图标
        self.video_camera_label = QLabel(self)
        self.video_camera_label.setPixmap(QPixmap(icon_path.Icon_custom_video_camera))
        # 摄像机录像开始和停止text显示
        self.video_camera_status_text = QLineEdit(self)
        # 视频开始和停止显示
        if self.type == video_action.video_record_start:
            status = 'record: Start'
        else:
            status = 'record: Stop'
        self.video_camera_status_text.setText(status)
        self.play_botton = QToolButton(self)
        self.play_botton.setToolTip('play')
        self.play_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_play + ')}')
        self.delete_botton = QToolButton(self)
        self.delete_botton.setToolTip('delete')
        self.delete_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_delete + ')}')
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.video_camera_label)
        self.h_box.addWidget(self.video_camera_status_text)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delete_botton)
        self.setLayout(self.h_box)

# 延时动作展示控件(sleep)
class Sleep_Control(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, sleep_time=0.0):
        super(Sleep_Control, self).__init__(parent)
        self.parent = parent
        self.id = id
        self.sleep_time = sleep_time
        self.initUI()


    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 延时图标
        self.sleep_icon_label = QLabel(self)
        self.sleep_icon_label.setPixmap(QPixmap(icon_path.Icon_custom_sleep))
        # 延时text显示
        status = 'sleep: ' + str(self.sleep_time)
        self.sleep_des_text = QLineEdit(self)
        self.sleep_des_text.setText(status)
        self.play_botton = QToolButton(self)
        self.play_botton.setToolTip('play')
        self.play_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_play + ')}')
        self.delete_botton = QToolButton(self)
        self.delete_botton.setToolTip('delete')
        self.delete_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_delete + ')}')
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.sleep_icon_label)
        self.h_box.addWidget(self.sleep_des_text)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delete_botton)
        self.setLayout(self.h_box)

# 相机参数调节控件
class Camera_Param_Adjust_Control(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(Camera_Param_Adjust_Control, self).__init__(parent)
        self.parent = parent
        self.initUI()


    def initUI(self):
        self.general_layout = QGridLayout()

        # 设置曝光
        self.exposure_time_label = QLabel(self)
        self.exposure_time_label.setText('曝光: ')
        self.exposure_time_slider = QSlider(Qt.Horizontal, self)
        # self.video_progress_bar.valueChanged.connect(self.connect_video_progress_bar)
        self.exposure_time_spinbox = QSpinBox(self)
        self.exposure_time_spinbox.setRange(1000, 100000)
        self.general_layout.addWidget(self.exposure_time_label, 0, 0, 1, 1)
        self.general_layout.addWidget(self.exposure_time_slider, 0, 1, 1, 3)
        self.general_layout.addWidget(self.exposure_time_spinbox, 0, 4, 1, 1)

        # 设置增益
        self.gain_label = QLabel(self)
        self.gain_label.setText('增益: ')
        self.gain_slider = QSlider(Qt.Horizontal, self)
        # self.video_progress_bar.valueChanged.connect(self.connect_video_progress_bar)
        self.gain_spinbox = QSpinBox(self)
        self.gain_spinbox.setRange(0, 100)
        self.general_layout.addWidget(self.gain_label, 1, 0, 1, 1)
        self.general_layout.addWidget(self.gain_slider, 1, 1, 1, 3)
        self.general_layout.addWidget(self.gain_spinbox, 1, 4, 1, 1)

        self.setLayout(self.general_layout)
        # 设置字体
        QFontDialog.setFont(self, QFont('Times New Roman', 11))
        # 设置最小尺寸
        self.setMinimumWidth(400)
        self.setWindowTitle('摄像头参数')