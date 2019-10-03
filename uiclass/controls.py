import time
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import gloVar, icon_path, uArm_action, record_action, logger, add_action_window, sleep_action

# 自定义动作展示控件(action)
class Action_Control(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, flag=True):
        super(Action_Control, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 动作类型
        self.action_type = info_dict[add_action_window.action_type]
        # 通过字典中的坐标信息, 来设置需要在控件中显示的坐标信息(字符串类型)
        self.other_param = '速度:' + str(info_dict[add_action_window.speed]) +\
                           ' 收回:' + str(info_dict[add_action_window.leave]) +\
                           ' 触发:' + str(info_dict[add_action_window.trigger])
        # 先将坐标元素转为字符串类型
        points = info_dict[add_action_window.points]
        if points:
            self.points_text = str(tuple(points))
        else:  # 无实际意义(单纯为了不让代码出现警告)
            self.points_text = '(0.0, 0.0)'
        # 描述text
        self.des_text = info_dict[add_action_window.des_text]
        # 判断是真的新建action还是通过脚本导入的case(flag:True新建, False导入)
        self.flag = flag
        self.initUI()
        self.descript_action()

    def initUI(self):

        self.check_box = QCheckBox()

        if self.action_type == uArm_action.uArm_click:
            pix_map = QPixmap(icon_path.Icon_robot_click)
        elif self.action_type == uArm_action.uArm_double_click:
            pix_map = QPixmap(icon_path.Icon_robot_double_click)
        elif self.action_type == uArm_action.uArm_long_click:
            pix_map = QPixmap(icon_path.Icon_robot_long_click)
        elif self.action_type == uArm_action.uArm_slide:
            pix_map = QPixmap(icon_path.Icon_robot_slide)
        else:
            pix_map = QPixmap(icon_path.Icon_robot_click)
        self.type_label = QLabel(self)
        self.type_label.setPixmap(pix_map)

        self.des_line_edit = QLineEdit(self)
        self.des_line_edit.setText(self.des_text)
        self.points_line_edit = QLineEdit(self)
        self.points_line_edit.setText(self.points_text)
        self.other_param_edit = QLineEdit(self)
        self.other_param_edit.setText(self.other_param)
        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.des_line_edit)
        self.v_box.addWidget(self.points_line_edit)
        self.v_box.addWidget(self.other_param_edit)

        self.play_botton = QToolButton(self)
        self.play_botton.setToolTip('play')
        self.play_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_play + ')}')
        self.play_botton.clicked.connect(self.action_execute_item)
        self.delete_botton = QToolButton(self)
        self.delete_botton.setToolTip('delete')
        self.delete_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_delete + ')}')
        self.delete_botton.clicked.connect(self.action_delete_item)

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.type_label)
        self.h_box.addLayout(self.v_box)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delete_botton)

        self.setLayout(self.h_box)


    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)


    # 执行单个动作的具体操作
    def play_action_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        while True:
            if gloVar.request_status == 'ok':
                gloVar.request_status = None
                self.signal.emit('action_execute_item>' + str(self.id))
                break
            else:
                # 降低cpu负债(使线程更加稳定)
                time.sleep(0.02)


    # 执行单个动作(新建线程/控件中的执行按钮)
    def action_execute_item(self):
        Thread(target=self.play_action_item, args=()).start()


    # 删除单个动作(控件中的删除按钮)
    def action_delete_item(self):
        # 打印删除信息
        if self.des_line_edit.text() == '':
            logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: 无描述信息'.format(self.str_decorate(self.id),
                                                                            self.str_decorate(self.action_type),
                                                                            str(self.points_text)))
        else:
            logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: {}'.format(self.str_decorate(self.id),
                                                                             self.str_decorate(self.action_type),
                                                                             str(self.points_text),
                                                                             self.des_line_edit.text()))
        self.signal.emit('action_delete_item>' + str(self.id))


    # 描述action
    def descript_action(self):
        # 如果确实是添加动作(而非导入case中的动作)
        if self.flag is True:
            # 打印新建动作信息
            if self.des_text == '':
                logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: 无描述信息'.format(self.str_decorate(self.id),
                                                                                self.str_decorate(self.action_type),
                                                                                self.points_text))
            else:
                logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: {}'.format(self.str_decorate(self.id),
                                                                             self.str_decorate(self.action_type),
                                                                             self.points_text,
                                                                             self.des_text))

# 摄像头录制开始和停止动作展示控件(camera_start/camera_stop)
class Record_Control(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, flag=True):
        super(Record_Control, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(flag:True新建, False导入)
        self.flag = flag
        self.record_type = info_dict[record_action.record_status]
        self.initUI()
        self.descript_record()


    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 摄像机图标
        self.video_camera_label = QLabel(self)
        self.video_camera_label.setPixmap(QPixmap(icon_path.Icon_custom_video_camera))
        # 摄像机录像开始和停止text显示
        self.video_camera_status_text = QLineEdit(self)
        # 视频开始和停止显示
        if self.record_type == record_action.record_start:
            status = 'record: Start'
        else:
            status = 'record: Stop'
        self.video_camera_status_text.setText(status)
        self.play_botton = QToolButton(self)
        self.play_botton.setToolTip('play')
        self.play_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_play + ')}')
        self.play_botton.clicked.connect(self.record_execute_item)
        self.delete_botton = QToolButton(self)
        self.delete_botton.setToolTip('delete')
        self.delete_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_delete + ')}')
        self.delete_botton.clicked.connect(self.record_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.video_camera_label)
        self.h_box.addWidget(self.video_camera_status_text)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delete_botton)
        self.setLayout(self.h_box)


    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)


    # 执行单个动作的具体操作
    def play_record_item(self):
        pass
        # # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        # while True:
        #     if gloVar.request_status == 'ok':
        #         gloVar.request_status = None
        #         self.signal.emit('action_execute_item>' + str(self.id))
        #         break
        #     else:
        #         # 降低cpu负债(使线程更加稳定)
        #         time.sleep(0.02)


    # 执行单个动作(新建线程/控件中的执行按钮)
    def record_execute_item(self):
        Thread(target=self.play_record_item, args=()).start()


    # 删除单个动作(控件中的删除按钮)
    def record_delete_item(self):
        # 打印删除信息
        logger('删除-->id{:-<5}action{:-<16}录像动作{}'.format(self.str_decorate(self.id),
                                                                        self.str_decorate(record_action.record_status),
                                                                        self.str_decorate(self.record_type)))
        self.signal.emit('record_delete_item>' + str(self.id))


    def descript_record(self):
        if self.flag is True:
            # 打印新建video动作信息
            logger('新建-->id{:-<5}action{:-<16}录像动作{}'.format(self.str_decorate(self.id),
                                                                      self.str_decorate(record_action.record_status),
                                                                      self.str_decorate(self.record_type)))

# 延时动作展示控件(sleep)
class Sleep_Control(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, flag=True):
        super(Sleep_Control, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(flag:True新建, False导入)
        self.flag = flag
        self.sleep_time = info_dict[sleep_action.sleep_time]
        self.initUI()
        self.descript_sleep()


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
        self.play_botton.clicked.connect(self.sleep_execute_item)
        self.delete_botton = QToolButton(self)
        self.delete_botton.setToolTip('delete')
        self.delete_botton.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_custom_delete + ')}')
        self.delete_botton.clicked.connect(self.sleep_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.sleep_icon_label)
        self.h_box.addWidget(self.sleep_des_text)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delete_botton)
        self.setLayout(self.h_box)


    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    # 执行单个动作的具体操作
    def play_sleep_item(self):
        pass
        # # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        # while True:
        #     if gloVar.request_status == 'ok':
        #         gloVar.request_status = None
        #         self.signal.emit('action_execute_item>' + str(self.id))
        #         break
        #     else:
        #         # 降低cpu负债(使线程更加稳定)
        #         time.sleep(0.02)

    # 执行单个动作(新建线程/控件中的执行按钮)
    def sleep_execute_item(self):
        Thread(target=self.play_sleep_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def sleep_delete_item(self):
        # 打印删除信息
        logger('删除-->id{:-<5}action{:-<16}延时时间{}'.format(self.str_decorate(self.id),
                                                              self.str_decorate(sleep_action.sleep_time),
                                                              self.str_decorate(self.sleep_time)))
        self.signal.emit('sleep_delete_item>' + str(self.id))


    def descript_sleep(self):
        if self.flag is True:
            # 打印新建video动作信息
            logger('新建-->id{:-<5}action{:-<16}延时时间{}'.format(self.str_decorate(self.id),
                                                                  self.str_decorate(sleep_action.sleep_time),
                                                                  self.str_decorate(self.sleep_time)))

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
        self.exposure_time_slider.setRange(1000, 100000)
        self.exposure_time_slider.valueChanged.connect(self.connect_exposure_time_slider)
        self.exposure_time_spinbox = QSpinBox(self)
        self.exposure_time_spinbox.setRange(1000, 100000)
        self.exposure_time_spinbox.valueChanged.connect(self.connect_exposure_time_spinbox)
        self.general_layout.addWidget(self.exposure_time_label, 0, 0, 1, 1)
        self.general_layout.addWidget(self.exposure_time_slider, 0, 1, 1, 3)
        self.general_layout.addWidget(self.exposure_time_spinbox, 0, 4, 1, 1)

        # 设置增益
        self.gain_label = QLabel(self)
        self.gain_label.setText('增益: ')
        self.gain_slider = QSlider(Qt.Horizontal, self)
        self.gain_slider.setRange(0, 100)
        self.gain_slider.valueChanged.connect(self.connect_gain_slider)
        self.gain_spinbox = QSpinBox(self)
        self.gain_spinbox.setRange(0, 100)
        self.gain_spinbox.valueChanged.connect(self.connect_gain_spinbox)
        self.general_layout.addWidget(self.gain_label, 1, 0, 1, 1)
        self.general_layout.addWidget(self.gain_slider, 1, 1, 1, 3)
        self.general_layout.addWidget(self.gain_spinbox, 1, 4, 1, 1)

        self.setLayout(self.general_layout)
        # 设置字体
        QFontDialog.setFont(self, QFont('Times New Roman', 11))
        # 设置最小尺寸
        self.setMinimumWidth(400)
        self.setWindowTitle('摄像头参数')


    def connect_exposure_time_slider(self):
        value = int(self.exposure_time_slider.value())
        self.exposure_time_spinbox.setValue(value)


    def connect_exposure_time_spinbox(self):
        value = int(self.exposure_time_spinbox.value())
        self.exposure_time_slider.setValue(value)


    def connect_gain_slider(self):
        value = int(self.gain_slider.value())
        self.gain_spinbox.setValue(value)


    def connect_gain_spinbox(self):
        value = int(self.gain_spinbox.value())
        self.gain_slider.setValue(value)