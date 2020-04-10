import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.add_action_tab import AddActionTab
from uiclass.add_record_tab import AddRecordTab
from uiclass.add_sleep_tab import AddSleepTab
from uiclass.add_assert_tab import AddAssertTab
from uiclass.add_restore_tab import AddRestoreTab
from GlobalVar import *


class TabWidget(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent=None, case_name=None):
        super(TabWidget, self).__init__(parent)
        self.parent = parent
        self.setObjectName('LeftTabWidget')
        self.setWindowTitle('LeftTabWidget')
        # list_style样式
        self.list_style = 'QListWidget{padding: 0px 0px 0px 0px;}\
                           QListWidget::item{color: #242424;}\
                           QListWidget::Item:selected{background: #0099FF;}\
                           QListWidget::item:hover{background: #99CCFF;}'
        # 窗口的整体布局
        self.main_layout = QHBoxLayout(self, spacing=0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # 左侧选项列表
        self.left_widget = QListWidget()
        self.left_widget.setStyleSheet(self.list_style)
        self.main_layout.addWidget(self.left_widget)

        self.right_widget = QStackedWidget()
        self.stacked_style = 'QStackedWidget{ border: 1px solid #0099FF;}'
        self.right_widget.setStyleSheet(self.stacked_style)
        self.main_layout.addWidget(self.right_widget)
        # 设置比例
        self.main_layout.setStretch(0, 2)
        self.main_layout.setStretch(1, 9)
        # list和右侧窗口的index对应绑定
        self.left_widget.currentRowChanged.connect(self.right_widget.setCurrentIndex)
        # 去掉边框
        self.left_widget.setFrameShape(QListWidget.NoFrame)
        # 隐藏滚动条
        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 添加tab
        self.action_tab = AddActionTab(self)
        self.record_tab = AddRecordTab(self, case_name)
        self.assert_tab = AddAssertTab(self, case_name)
        self.restore_tab = AddRestoreTab(self)
        self.sleep_tab = AddSleepTab(self)
        self.add_tab(self.action_tab, 'action')
        self.add_tab(self.record_tab, 'video')
        self.add_tab(self.assert_tab, 'assert')
        self.add_tab(self.restore_tab, 'restore')
        self.add_tab(self.sleep_tab, 'sleep')
        # 设置当前行为第0行
        self.left_widget.setCurrentRow(0)


    def add_tab(self, widget, tab_name):
        item = QListWidgetItem(tab_name, self.left_widget)  # 左侧选项的添加
        # 居中显示
        # item.setTextAlignment(Qt.AlignCenter)
        item.setTextAlignment(Qt.AlignLeft)
        self.right_widget.addWidget(widget)


class AddTabWidget(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent=None, case_name=None):
        super(AddTabWidget, self).__init__(parent)
        self.parent = parent
        self.case_name = case_name
        self.widget = TabWidget(self, case_name)
        self.general_layout = QVBoxLayout()
        self.general_layout.setContentsMargins(0, 0, 0, 0)
        self.general_layout.addWidget(self.widget)
        self.setLayout(self.general_layout)
        self.setWindowTitle('动作设置')
        self.widget.action_tab.signal[str].connect(self.recv_action_tab_signal)
        self.widget.record_tab.signal[str].connect(self.recv_record_tab_signal)
        self.widget.assert_tab.signal[str].connect(self.recv_assert_tab_signal)
        self.widget.restore_tab.signal[str].connect(self.recv_restore_tab_signal)
        self.widget.sleep_tab.signal[str].connect(self.recv_sleep_tab_signal)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(500)

    # 接收action_tab传来的信号
    def recv_action_tab_signal(self, signal_str):
        # 按下获取坐标(隐藏当前窗口)
        if signal_str.startswith('action_tab_get_points>'):
            self.setHidden(True)
        # 选择动作后需要改变动作标志
        elif signal_str.startswith('action_tab_action>'):
            self.signal.emit(signal_str)
        # 按下确认按钮
        elif signal_str.startswith('action_tab_sure>'):
            self.signal.emit(signal_str)
            GloVar.add_action_window_opened_flag = False
            self.close()

    # 接收video_tab传来的信号
    def recv_record_tab_signal(self, signal_str):
        # 框选模板(隐藏当前窗口)
        if signal_str.startswith(GloVar.result_template):
            # 发送框选信号
            self.signal.emit(signal_str)
            self.setHidden(True)
        elif signal_str.startswith('record_tab_sure>'):
            self.signal.emit(signal_str)
            GloVar.add_action_window_opened_flag = False
            self.close()

    # 接收assert_tab传来的信号
    def recv_assert_tab_signal(self, signal_str):
        # 框选模板(隐藏当前窗口)
        if signal_str.startswith(GloVar.assert_template):
            # 发送框选信号
            self.signal.emit(signal_str)
            self.setHidden(True)
        elif signal_str.startswith('assert_tab_sure>'):
            self.signal.emit(signal_str)
            GloVar.add_action_window_opened_flag = False
            self.close()

    # 接收restore_tab传来的信号
    def recv_restore_tab_signal(self, signal_str):
        if signal_str.startswith('restore_tab_sure>'):
            self.signal.emit(signal_str)
            GloVar.add_action_window_opened_flag = False
            self.close()

    # 接收sleep_tab传来的信号
    def recv_sleep_tab_signal(self, signal_str):
        if signal_str.startswith('sleep_tab_sure>'):
            self.signal.emit(signal_str)
            GloVar.add_action_window_opened_flag = False
            self.close()

    def closeEvent(self, event):
        # 如果取消则恢复默认
        MotionAction.add_action_flag = False
        RobotArmAction.uArm_action_type = None
        self.widget.action_tab.info_dict = {MotionAction.des_text: None,
                                            MotionAction.action_type: RobotArmAction.uArm_click,
                                            MotionAction.speed: 150,
                                            MotionAction.points: None,
                                            MotionAction.leave: 1,
                                            MotionAction.trigger: 1}
        # action_tab复位
        self.widget.action_tab.des_text.setText('')
        self.widget.action_tab.des_text.setPlaceholderText('动作描述(选填)')
        self.widget.action_tab.com_box.setCurrentText(RobotArmAction.uArm_click)
        self.widget.action_tab.speed_text.setText('')
        self.widget.action_tab.speed_text.setPlaceholderText('动作速度(选填)')
        self.widget.action_tab.points.setText('')
        self.widget.action_tab.points.setPlaceholderText('自动获取(不填)')
        self.widget.action_tab.leave_check_box.setCheckState(Qt.Checked)
        self.widget.action_tab.camera_trigger_check_box.setCheckState(Qt.Unchecked)
        # video_tab复位
        self.widget.record_tab.start_record_video.setCheckState(Qt.Unchecked)
        self.widget.record_tab.stop_record_video.setCheckState(Qt.Unchecked)
        self.widget.record_tab.select_template.clear()
        self.widget.record_tab.video_type_edit.setText('')
        self.widget.record_tab.video_type_edit.setPlaceholderText('默认(启动)')
        self.widget.record_tab.video_name_edit.setText('')
        # self.widget.record_tab.video_name_edit.setPlaceholderText('默认(name)')
        self.widget.record_tab.video_name_edit.setPlaceholderText(self.case_name)
        self.widget.record_tab.standard_time_edit.setText('')
        self.widget.record_tab.standard_time_edit.setPlaceholderText('默认800(单位ms)')
        # sleep_tab复位
        self.widget.sleep_tab.sleep_time_edit.setText('')
        self.widget.sleep_tab.sleep_time_edit.setPlaceholderText('睡眠时间(单位:s)')
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AddTabWidget(None)
    gui.show()
    sys.exit(app.exec_())
