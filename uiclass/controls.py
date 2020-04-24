import time
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import *


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
            Logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: 无描述信息'.format(self.str_decorate(self.id),
                                                                            self.str_decorate(self.action_type),
                                                                            str(self.points_text)))
        else:
            Logger('删除-->id{:-<5}action{:-<16}坐标信息{:-<30}-->: {}'.format(self.str_decorate(self.id),
                                                                         self.str_decorate(self.action_type),
                                                                         str(self.points_text),
                                                                         self.des_line_edit.text()))
        self.signal.emit('action_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_action(self):
        # 如果确实是添加动作(而非导入case中的动作)
        if self.new_control_flag is True:
            # 打印新建动作信息
            if self.des_text == '':
                Logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: 无描述信息'.format(self.str_decorate(self.id),
                                                                                self.str_decorate(self.action_type),
                                                                                self.points_text))
            else:
                Logger('新建-->id{:-<5}action{:-<16}坐标信息{:-<35}-->: {}'.format(self.str_decorate(self.id),
                                                                             self.str_decorate(self.action_type),
                                                                             self.points_text, self.des_text))


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
        Logger('删除-->id{:-<5}action{:-<16}录像动作{}'.format(self.str_decorate(self.id),
                                                         self.str_decorate(RecordAction.record_status),
                                                         self.str_decorate(self.record_type)))
        self.signal.emit('record_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_record(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}录像动作{}'.format(self.str_decorate(self.id),
                                                             self.str_decorate(RecordAction.record_status),
                                                             self.str_decorate(self.record_type)))


# 断言模板图片控件(通过模板判断是否出现预期界面)
class AssertControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(AssertControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        # 断言模板绝对路径
        self.template_path = info_dict[AssertAction.assert_template_name]
        # 缩略图尺寸
        self.thumbnail_size = (60, 60)
        self.initUI()
        self.describe_assert()

    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 模板缩略图
        self.thumbnail_label = QLabel(self)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFixedSize(self.thumbnail_size[0], self.thumbnail_size[1])
        self.reload_thumbnail(self.template_path)
        # 显示模板路径
        self.template_path_text = QLineEdit(self)
        self.template_path_text.setReadOnly(True)
        self.template_path_text.setText(self.template_path)
        self.template_path_text.setCursorPosition(0)
        # 按钮
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.assert_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.assert_delete_item)
        # 横向布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.thumbnail_label)
        self.h_box.addWidget(self.template_path_text)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)

    # 重新载入缩略图
    def reload_thumbnail(self, image):
        origin_image = QImage(image)
        origin_width = origin_image.width()
        origin_height = origin_image.height()
        max_num = max(origin_width, origin_height)
        if max_num > self.thumbnail_size[0]:
            scale = self.thumbnail_size[0] / max_num
        else:
            scale = 1.0
        new_size = QSize(origin_width * scale, origin_height * scale)
        pix_map = QPixmap.fromImage(origin_image.scaled(new_size, Qt.IgnoreAspectRatio))
        self.thumbnail_label.setPixmap(pix_map)

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    # 执行单个动作的具体操作
    def play_assert_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('assert_execute_item>' + str(self.id))

    # 执行单个动作(新建线程/控件中的执行按钮)
    def assert_execute_item(self):
        # 每执行一次都需要获取当前时间(作为文件夹)
        GloVar.current_time = time.strftime('%H-%M-%S', time.localtime(time.time()))
        Thread(target=self.play_assert_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def assert_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}断言动作模板{}'.format(self.str_decorate(self.id),
                                                           self.str_decorate(AssertAction.assert_template_name),
                                                           self.str_decorate(self.template_path)))
        self.signal.emit('assert_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_assert(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}断言动作模板{}'.format(self.str_decorate(self.id),
                                                               self.str_decorate(AssertAction.assert_template_name),
                                                               self.str_decorate(self.template_path)))


# 恢复主页面展示控件(restore)
class RestoreControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(RestoreControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.restore_screen = info_dict[RestoreAction.restore_screen]
        self.initUI()
        self.describe_restore()

    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # restore图标
        self.restore_icon_label = QLabel(self)
        self.restore_icon_label.setPixmap(QPixmap(IconPath.Icon_custom_restore))
        # 恢复text显示
        status = '恢复: ' + str(self.restore_screen)
        self.restore_des_text = QLineEdit(self)
        self.restore_des_text.setReadOnly(True)
        self.restore_des_text.setText(status)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.restore_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.restore_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.restore_icon_label)
        self.h_box.addWidget(self.restore_des_text)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    # 执行单个动作的具体操作
    def play_restore_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('restore_execute_item>' + str(self.id))

    # 执行单个动作(新建线程/控件中的执行按钮)
    def restore_execute_item(self):
        Thread(target=self.play_restore_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def restore_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}恢复屏幕{}'.format(self.str_decorate(self.id),
                                                         self.str_decorate(RestoreAction.restore_screen),
                                                         self.str_decorate(self.restore_screen)))
        self.signal.emit('restore_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_restore(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}恢复屏幕{}'.format(self.str_decorate(self.id),
                                                             self.str_decorate(RestoreAction.restore_screen),
                                                             self.str_decorate(self.restore_screen)))


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


# 逻辑if展示控件(if)
class LogicControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(LogicControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.logic_type = info_dict[LogicAction.logic_action]
        self.initUI()
        self.describe_sleep()

    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 逻辑图标
        if self.logic_type == LogicAction.logic_if:
            icon_path = IconPath.Icon_logic_if
        elif self.logic_type == LogicAction.logic_then:
            icon_path = IconPath.Icon_logic_then
        elif self.logic_type == LogicAction.logic_else:
            icon_path = IconPath.Icon_logic_else
        elif self.logic_type == LogicAction.logic_end_if:
            icon_path = IconPath.Icon_logic_end_if
        else:
            icon_path = ''
        self.logic_icon_label = QLabel(self)
        self.logic_icon_label.setPixmap(QPixmap(icon_path))
        # 逻辑显示
        self.logic_des_text = QLineEdit(self)
        self.logic_des_text.setReadOnly(True)
        self.logic_des_text.setText(self.logic_type)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.logic_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.logic_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.logic_icon_label)
        self.h_box.addWidget(self.logic_des_text)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    def play_logic_item(self):
        self.signal.emit('logic_execute_item>' + str(self.id))

    # 执行单个动作(新建线程/控件中的执行按钮)
    def logic_execute_item(self):
        Thread(target=self.play_logic_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def logic_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}逻辑动作{}'.format(self.str_decorate(self.id),
                                                         self.str_decorate(LogicAction.logic_action),
                                                         self.str_decorate(self.logic_type)))
        self.signal.emit('logic_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_sleep(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}逻辑动作{}'.format(self.str_decorate(self.id),
                                                             self.str_decorate(LogicAction.logic_action),
                                                             self.str_decorate(self.logic_type)))


# 循环loop展示控件(if)
class LoopControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(LoopControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.loop_type = info_dict[LoopAction.loop_action]
        if LoopAction.loop_num in info_dict:
            self.loop_num = int(info_dict[LoopAction.loop_num])
        else:
            self.loop_num = 0
        self.initUI()
        self.describe_sleep()

    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 逻辑图标
        if self.loop_type == LoopAction.loop_start:
            icon_path = IconPath.Icon_loop_start
        elif self.loop_type == LoopAction.loop_end:
            icon_path = IconPath.Icon_loop_end
        else:
            icon_path = ''
        self.loop_icon_label = QLabel(self)
        self.loop_icon_label.setPixmap(QPixmap(icon_path))
        # 显示循环次数(只有loop_start显示次数)
        self.num_show = QSpinBox(self)
        self.num_show.setValue(self.loop_num)
        self.num_show.valueChanged.connect(self.loop_num_changed)
        if self.loop_type == LoopAction.loop_start:
            self.num_show.setHidden(False)
        else:
            self.num_show.setHidden(True)
        # 逻辑显示
        self.loop_des_text = QLineEdit(self)
        self.loop_des_text.setReadOnly(True)
        self.loop_des_text.setText(self.loop_type)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.loop_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.loop_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.loop_icon_label)
        self.h_box.addWidget(self.loop_des_text)
        self.h_box.addWidget(self.num_show)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)

    # 循环次数改变
    def loop_num_changed(self):
        self.loop_num = self.num_show.value()
        self.signal.emit('loop_num_changed>' + str(self.id))

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    def play_loop_item(self):
        self.signal.emit('loop_execute_item>' + str(self.id))

    # 执行单个动作(新建线程/控件中的执行按钮)
    def loop_execute_item(self):
        Thread(target=self.play_loop_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def loop_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}循环动作{}'.format(self.str_decorate(self.id),
                                                         self.str_decorate(LoopAction.loop_action),
                                                         self.str_decorate(self.loop_type)))
        self.signal.emit('loop_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_sleep(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}循环动作{}'.format(self.str_decorate(self.id),
                                                             self.str_decorate(LoopAction.loop_action),
                                                             self.str_decorate(self.loop_type)))


# break动作展示控件
class BreakControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(BreakControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.break_text = info_dict[BreakAction.break_action]
        self.initUI()
        self.describe_break()

    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 延时图标
        self.break_icon_label = QLabel(self)
        self.break_icon_label.setPixmap(QPixmap(IconPath.Icon_loop_break))
        # break_text显示
        self.break_des_text = QLineEdit(self)
        self.break_des_text.setReadOnly(True)
        self.break_des_text.setText(self.break_text)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.break_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.break_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.break_icon_label)
        self.h_box.addWidget(self.break_des_text)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    # 执行单个动作的具体操作
    def play_break_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('break_execute_item>' + str(self.id))

    # 执行单个动作(新建线程/控件中的执行按钮)
    def break_execute_item(self):
        Thread(target=self.play_break_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def break_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}'.format(self.str_decorate(self.id),
                                                         self.str_decorate(BreakAction.break_out)))
        self.signal.emit('break_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_break(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}'.format(self.str_decorate(self.id),
                                                             self.str_decorate(BreakAction.break_out)))


# 调用函数动作展示控件
class CallFunctionControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(CallFunctionControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.function_name = info_dict[CallFunctionAction.function_name]
        self.initUI()
        self.describe_break()

    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # 调用函数图标
        self.call_function_icon_label = QLabel(self)
        self.call_function_icon_label.setPixmap(QPixmap(IconPath.Icon_call_function_icon))
        # function_name显示
        self.call_function_des_text = QLineEdit(self)
        self.call_function_des_text.setReadOnly(True)
        self.call_function_des_text.setText(self.function_name)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.call_function_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.call_function_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.call_function_icon_label)
        self.h_box.addWidget(self.call_function_des_text)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    # 执行单个动作的具体操作
    def play_call_function_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('call_function_execute_item>' + str(self.id))

    # 执行单个动作(新建线程/控件中的执行按钮)
    def call_function_execute_item(self):
        Thread(target=self.play_call_function_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def call_function_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}函数名:{}'.format(self.str_decorate(self.id),
                                                         self.str_decorate(CallFunctionAction.call_function),
                                                         self.str_decorate(self.function_name)))
        self.signal.emit('call_function_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_break(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}函数名:{}'.format(self.str_decorate(self.id),
                                                             self.str_decorate(CallFunctionAction.call_function),
                                                             self.str_decorate(self.function_name)))


# 调用adb动作展示控件
class ADBControl(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, id, info_dict, new_control_flag=True):
        super(ADBControl, self).__init__(parent)
        self.parent = parent
        self.id = id
        # 判断是真的新建record还是通过脚本导入的case(new_control_flag:True新建, False导入)
        self.new_control_flag = new_control_flag
        self.adb_desc = info_dict[ADBAction.adb_desc]
        self.initUI()
        self.describe_adb()

    def initUI(self):
        # 选择框
        self.check_box = QCheckBox()
        # adb图标
        self.adb_icon_label = QLabel(self)
        self.adb_icon_label.setPixmap(QPixmap(IconPath.Icon_adb))
        # adb描述显示
        self.adb_des_text = QLineEdit(self)
        self.adb_des_text.setReadOnly(True)
        self.adb_des_text.setText(self.adb_desc)
        self.play_button = QToolButton(self)
        self.play_button.setToolTip('play')
        self.play_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_play + ')}')
        self.play_button.clicked.connect(self.adb_execute_item)
        self.delete_button = QToolButton(self)
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.Icon_custom_delete + ')}')
        self.delete_button.clicked.connect(self.adb_delete_item)
        # 布局
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.adb_icon_label)
        self.h_box.addWidget(self.adb_des_text)
        self.h_box.addWidget(self.play_button)
        self.h_box.addWidget(self.delete_button)
        self.setLayout(self.h_box)
        self.setMaximumWidth(400)

    # 此仅仅为美化字符串格式, decorate_str为一个对称字符串(如'()'/'[]'/'{}')
    def str_decorate(self, origin_str, decorate_str='[]'):
        return str(origin_str).join(decorate_str)

    # 执行单个动作的具体操作
    def play_adb_item(self):
        # 执行单个动作(需要判断上一次动作完成没有, 如果完成则可以进行此次动作, 否则就等待上次动作执行完成)
        # 发送触发信号以及详细信息到主程序(在主程序中执行动作)
        self.signal.emit('adb_execute_item>' + str(self.id))

    # 执行单个动作(新建线程/控件中的执行按钮)
    def adb_execute_item(self):
        Thread(target=self.play_adb_item, args=()).start()

    # 删除单个动作(控件中的删除按钮)
    def adb_delete_item(self):
        # 打印删除信息
        Logger('删除-->id{:-<5}action{:-<16}描述:{}'.format(self.str_decorate(self.id),
                                                         self.str_decorate(ADBAction.ADB),
                                                         self.str_decorate(self.adb_desc)))
        self.signal.emit('adb_delete_item>' + str(self.id))

    # 打印控件信息
    def describe_adb(self):
        if self.new_control_flag is True:
            # 打印新建video动作信息
            Logger('新建-->id{:-<5}action{:-<16}描述:{}'.format(self.str_decorate(self.id),
                                                             self.str_decorate(ADBAction.ADB),
                                                             self.str_decorate(self.adb_desc)))


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


# 设置控件
class SettingControl(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(SettingControl, self).__init__(parent)
        self.parent = parent
        self.picture_path = Profile(type='read', file=GloVar.config_file_path, section='param', option='picture_path').value
        self.stable_frame_rate_flag = True
        # 是否需要实时展示报告
        real_time_show_report = Profile(type='read', file=GloVar.config_file_path, section='param',
                                        option='real_time_show_report').value
        if real_time_show_report == 'True':
            GloVar.real_time_show_report_flag = True
        else:
            GloVar.real_time_show_report_flag = False
        self.initUI()

    def initUI(self):
        # 控件总布局
        self.general_layout = QVBoxLayout()
        # 曝光增益使用栅格布局
        self.grid_layout = QGridLayout()
        # 确认button布局
        self.sure_button_layout = QHBoxLayout()
        # 设置case执行过程中是否需要关闭界面实时流(关闭实时流可以保证录制视频不丢帧)
        self.real_time_show_report_label = QLabel(self)
        self.real_time_show_report_label.setText('实时报告: ')
        self.real_time_show_report_des = QLineEdit(self)
        self.real_time_show_report_des.setReadOnly(True)
        self.real_time_show_report_button = QPushButton(self)
        self.real_time_show_report_button.setMaximumWidth(40)
        self.real_time_show_report_button.clicked.connect(self.change_real_time_show_report_status)
        if GloVar.real_time_show_report_flag is True:
            self.real_time_show_report_button.setStyleSheet(
                 'QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
            self.real_time_show_report_des.setText('开启状态,每执行一条case后,会处理数据,会实时刷新报告')
        else:
            self.real_time_show_report_button.setStyleSheet(
                'QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_off + ')}')
            self.real_time_show_report_des.setText('关闭状态,所有case执行完成后,才会处理数据,不会实时刷新报告')
        self.grid_layout.addWidget(self.real_time_show_report_label, 0, 0, 1, 1)
        self.grid_layout.addWidget(self.real_time_show_report_des, 0, 1, 1, 5)
        self.grid_layout.addWidget(self.real_time_show_report_button, 0, 6, 1, 1)
        # 设置case执行过程中是否需要关闭界面实时流(关闭实时流可以保证录制视频不丢帧)
        self.stable_frame_rate_label = QLabel(self)
        self.stable_frame_rate_label.setText('稳定帧率: ')
        self.stable_frame_rate_des = QLineEdit(self)
        self.stable_frame_rate_des.setReadOnly(True)
        self.stable_frame_rate_des.setText('开启状态,执行case过程中会暂停实时流,帧率稳定')
        self.stable_frame_rate_button = QPushButton(self)
        self.stable_frame_rate_button.setMaximumWidth(40)
        self.stable_frame_rate_button.clicked.connect(self.change_stable_frame_rate_status)
        self.stable_frame_rate_button.setStyleSheet(
            'QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
        self.grid_layout.addWidget(self.stable_frame_rate_label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.stable_frame_rate_des, 1, 1, 1, 5)
        self.grid_layout.addWidget(self.stable_frame_rate_button, 1, 6, 1, 1)
        # 设置新建动作过程中机械臂是否随着动作的新建而动
        self.robot_follow_action_flag_label = QLabel(self)
        self.robot_follow_action_flag_label.setText('动作跟随:')
        self.robot_follow_action_flag_des = QLineEdit(self)
        self.robot_follow_action_flag_des.setReadOnly(True)
        self.robot_follow_action_flag_des.setText('打开状态,新建机械臂动作过程中,机械臂会随之而动')
        self.robot_follow_action_flag_button = QPushButton(self)
        self.robot_follow_action_flag_button.setMaximumWidth(40)
        self.robot_follow_action_flag_button.clicked.connect(self.change_robot_follow_action_flag)
        self.robot_follow_action_flag_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
        self.grid_layout.addWidget(self.robot_follow_action_flag_label, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.robot_follow_action_flag_des, 2, 1, 1, 5)
        self.grid_layout.addWidget(self.robot_follow_action_flag_button, 2, 6, 1, 1)
        # 机械臂动作默认收回与否
        self.robot_action_take_back_label = QLabel(self)
        self.robot_action_take_back_label.setText('动作收回:')
        self.robot_action_take_back_des = QLineEdit(self)
        self.robot_action_take_back_des.setReadOnly(True)
        self.robot_action_take_back_des.setText('关闭状态,新建机械臂动作默认操作完后不会收回到原点')
        self.robot_action_take_back_flag_button = QPushButton(self)
        self.robot_action_take_back_flag_button.setMaximumWidth(40)
        self.robot_action_take_back_flag_button.clicked.connect(self.change_robot_action_take_back_flag)
        self.robot_action_take_back_flag_button.setStyleSheet('QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_off + ')}')
        self.grid_layout.addWidget(self.robot_action_take_back_label, 3, 0, 1, 1)
        self.grid_layout.addWidget(self.robot_action_take_back_des, 3, 1, 1, 5)
        self.grid_layout.addWidget(self.robot_action_take_back_flag_button, 3, 6, 1, 1)
        # 设置屏幕真实尺寸
        self.screen_size_label = QLabel(self)
        self.screen_size_label.setText('屏幕尺寸:')
        self.screen_size_drop_down_box = QComboBox()
        self.screen_list = Profile().get_config_options(file=GloVar.config_file_path, section='screen_size')
        self.screen_size_list = []
        for screen_name in self.screen_list:
            screen_size = eval(Profile(type='read', file=GloVar.config_file_path, section='screen_size',
                                       option=screen_name).value)
            self.screen_size_list.append(screen_size)
            self.screen_size_drop_down_box.addItem(screen_name + str(screen_size))
        current_screen_size = eval(Profile(type='read', file=GloVar.config_file_path, section='param',
                                           option='actual_screen_size').value)
        current_screen_size_index = self.screen_size_list.index(current_screen_size)
        self.screen_size_drop_down_box.setCurrentIndex(current_screen_size_index)
        self.screen_size_drop_down_box.setEnabled(False)
        self.screen_size_button = QPushButton('修改')
        self.screen_size_button.clicked.connect(self.change_screen_size)
        self.grid_layout.addWidget(self.screen_size_label, 4, 0, 1, 1)
        self.grid_layout.addWidget(self.screen_size_drop_down_box, 4, 1, 1, 5)
        self.grid_layout.addWidget(self.screen_size_button, 4, 6, 1, 1)
        # 设置图片路径
        self.picture_path_show_label = QLabel(self)
        self.picture_path_show_label.setText('图片路径: ')
        self.picture_path_show_edit = QLineEdit(self)
        self.picture_path_show_edit.setReadOnly(True)
        self.picture_path_show_edit.setText(self.picture_path)
        self.picture_path_change_button = QPushButton('更改')
        self.picture_path_change_button.clicked.connect(self.connect_change_picture_path)
        self.grid_layout.addWidget(self.picture_path_show_label, 5, 0, 1, 1)
        self.grid_layout.addWidget(self.picture_path_show_edit, 5, 1, 1, 5)
        self.grid_layout.addWidget(self.picture_path_change_button, 5, 6, 1, 1)
        # 设置匹配模板的边界
        GloVar.template_border = int(Profile(type='read', file=GloVar.config_file_path, section='param',
                                             option='template_border').value)
        self.template_border_label = QLabel(self)
        self.template_border_label.setText('模板边界: ')
        self.template_border_edit = QLineEdit(self)
        self.template_border_edit.setReadOnly(True)
        self.template_border_edit.setText(str(GloVar.template_border))
        self.template_border_change_button = QPushButton('更改')
        self.template_border_change_button.clicked.connect(self.connect_template_border)
        self.grid_layout.addWidget(self.template_border_label, 6, 0, 1, 1)
        self.grid_layout.addWidget(self.template_border_edit, 6, 1, 1, 5)
        self.grid_layout.addWidget(self.template_border_change_button, 6, 6, 1, 1)
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
        self.setWindowTitle('设置参数')

    def change_real_time_show_report_status(self):
        if GloVar.real_time_show_report_flag is True:
            GloVar.real_time_show_report_flag = False
            self.real_time_show_report_button.setStyleSheet(
                'QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_off + ')}')
            self.real_time_show_report_des.setText('关闭状态,所有case执行完成后,才会处理数据,不会实时刷新报告')
        else:
            GloVar.real_time_show_report_flag = True
            self.real_time_show_report_button.setStyleSheet(
                'QPushButton{border-image: url(' + IconPath.Icon_tab_widget_switch_on + ')}')
            self.real_time_show_report_des.setText('开启状态,每执行一条case后,会处理数据,会实时刷新报告')
        Profile(type='write', file=GloVar.config_file_path, section='param', option='real_time_show_report',
                value=str(GloVar.real_time_show_report_flag))

    def change_stable_frame_rate_status(self):
        if self.stable_frame_rate_flag is True:
            self.stable_frame_rate_flag = False
            self.stable_frame_rate_button.setStyleSheet('QPushButton{border-image: url(' +
                                                        IconPath.Icon_tab_widget_switch_off + ')}')
            self.stable_frame_rate_des.setText('关闭状态,新建机械臂动作过程中,机械臂不会随之而动')
        else:
            self.stable_frame_rate_flag = True
            self.stable_frame_rate_button.setStyleSheet('QPushButton{border-image: url(' +
                                                        IconPath.Icon_tab_widget_switch_on + ')}')
            self.stable_frame_rate_des.setText('打开状态,新建机械臂动作过程中,机械臂会随之而动')

    def change_robot_follow_action_flag(self):
        if GloVar.robot_follow_action_flag is True:
            GloVar.robot_follow_action_flag = False
            self.robot_follow_action_flag_button.setStyleSheet('QPushButton{border-image: url(' +
                                                               IconPath.Icon_tab_widget_switch_off + ')}')
            self.robot_follow_action_flag_des.setText('关闭状态,执行case过程中会播放实时流,帧率不稳定')
        else:
            GloVar.robot_follow_action_flag = True
            self.robot_follow_action_flag_button.setStyleSheet('QPushButton{border-image: url(' +
                                                               IconPath.Icon_tab_widget_switch_on + ')}')
            self.robot_follow_action_flag_des.setText('打开状态,执行case过程中会暂停实时流,帧率稳定')

    def change_robot_action_take_back_flag(self):
        if GloVar.robot_action_take_back_flag is True:
            GloVar.robot_action_take_back_flag = False
            self.robot_action_take_back_flag_button.setStyleSheet('QPushButton{border-image: url(' +
                                                                  IconPath.Icon_tab_widget_switch_off + ')}')
            self.robot_action_take_back_des.setText('关闭状态,新建机械臂动作默认操作完后不会收回到原点')
        else:
            GloVar.robot_action_take_back_flag = True
            self.robot_action_take_back_flag_button.setStyleSheet('QPushButton{border-image: url(' +
                                                                  IconPath.Icon_tab_widget_switch_on + ')}')
            self.robot_action_take_back_des.setText('打开状态,新建机械臂动作默认操作完后会收回到原点')

    def change_screen_size(self):
        if self.screen_size_button.text() == '修改':
            self.screen_size_button.setText('保存')
            self.screen_size_drop_down_box.setEnabled(True)
        elif self.screen_size_button.text() == '保存':
            index = self.screen_size_drop_down_box.currentIndex()
            RobotArmParam.actual_screen_width, RobotArmParam.actual_screen_height = \
                current_screen_size = self.screen_size_list[index]
            Profile(type='write', file=GloVar.config_file_path, section='param', option='actual_screen_size',
                    value=str(current_screen_size))
            self.screen_size_button.setText('修改')
            self.screen_size_drop_down_box.setEnabled(False)

    def connect_change_picture_path(self):
        # 如果取消为''值
        self.picture_path = QFileDialog.getExistingDirectory(self, "浏览", self.picture_path,
                                                             options=QFileDialog.DontUseNativeDialog)
        if self.picture_path:
            self.picture_path_show_edit.setText(self.picture_path)
            Profile(type='write', file=GloVar.config_file_path, section='param', option='picture_path',
                    value=self.picture_path)
            Logger('修改保存图片路径为: %s' % self.picture_path)
            self.signal.emit('picture_path>' + self.picture_path)

    def connect_template_border(self):
        if self.template_border_change_button.text() == '更改':
            self.template_border_change_button.setText('保存')
            self.template_border_edit.setReadOnly(False)
        elif self.template_border_change_button.text() == '保存':
            GloVar.template_border = int(self.template_border_edit.text())
            Profile(type='write', file=GloVar.config_file_path, section='param', option='template_border',
                    value=str(GloVar.template_border))
            self.template_border_change_button.setText('更改')
            self.template_border_edit.setReadOnly(True)

    # 确认按钮按下触发事件
    def connect_sure_button(self):
        self.close()

    # 重写窗口关闭事件
    def closeEvent(self, event):
        self.close()


# 相机参数调节控件
class CameraParamAdjustControl(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent, use_external_camera_flag):
        super(CameraParamAdjustControl, self).__init__(parent)
        self.parent = parent
        self.use_external_camera_flag = use_external_camera_flag
        self.exposure_time_value = 1000
        self.gain_value = 0
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
            self.signal.emit(GloVar.result_template + '>')

    def clear(self):
        self.check_box.setCheckState(Qt.Unchecked)
        self.template_path.clear()
        self.template_path.setPlaceholderText('模板路径')
