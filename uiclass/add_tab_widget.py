import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from uiclass.add_action_tab import AddActionTab
from uiclass.add_video_tab import AddVideoTab
from uiclass.add_sleep_tab import AddSleepTab
from GlobalVar import icon_path, uArm_action, add_action_window, video_action

class TabWidget(QTabWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, action_tab='action', video_tab='video', sleep_tab='other'):
        super(TabWidget, self).__init__(parent)
        self.parent = parent
        self.setTabPosition(self.North)
        self.action_tab = AddActionTab(self)
        self.video_tab = AddVideoTab(self)
        self.sleep_tab = AddSleepTab(self)
        self.addTab(self.action_tab, action_tab)
        self.addTab(self.video_tab, video_tab)
        self.addTab(self.sleep_tab, sleep_tab)
        # 设置字体
        QFontDialog.setFont(self, QFont('Times New Roman', 11))

class AddTabWidget(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(AddTabWidget, self).__init__(parent)
        self.parent = parent
        self.widget = TabWidget(self)
        self.general_layout = QVBoxLayout()
        self.general_layout.addWidget(self.widget)
        self.setLayout(self.general_layout)
        self.setWindowTitle('动作设置')
        self.widget.action_tab.signal[str].connect(self.recv_action_tab_signal)
        self.widget.video_tab.signal[str].connect(self.recv_video_tab_signal)
        self.widget.sleep_tab.signal[str].connect(self.recv_sleep_tab_signal)


    # 接收action_tab传来的信号
    def recv_action_tab_signal(self, signal_str):
        # 按下获取坐标(隐藏当前窗口)
        if signal_str.startswith('get_points>'):
            self.setHidden(True)
        # 选择动作后需要改变动作标志
        if signal_str.startswith('action>'):
            self.signal.emit(signal_str)
        # 按下确认按钮
        elif signal_str.startswith('sure>'):
            self.signal.emit(signal_str)
            self.close()


    # 接收video_tab传来的信号
    def recv_video_tab_signal(self, signal_str):
        pass


    # 接收sleep_tab传来的信号
    def recv_sleep_tab_signal(self, signal_str):
        pass


    def closeEvent(self, event):
        # 如果取消则恢复默认
        add_action_window.add_action_flag = False
        uArm_action.uArm_action_type = None
        self.widget.action_tab.info_dict = {add_action_window.des_text    : None,
                          add_action_window.action_type : uArm_action.uArm_click,
                          add_action_window.speed       : 150,
                          add_action_window.points      : None,
                          add_action_window.leave       : 1,
                          add_action_window.trigger     : 1}
        # action_tab复位
        self.widget.action_tab.des_text.setText('')
        self.widget.action_tab.des_text.setPlaceholderText('请输入动作描述(可不写)')
        self.widget.action_tab.com_box.setCurrentText(uArm_action.uArm_click)
        self.widget.action_tab.speed_text.setText('')
        self.widget.action_tab.speed_text.setPlaceholderText('请输入动作速度(可不写)')
        self.widget.action_tab.points.setText('')
        self.widget.action_tab.leave_check_box.setCheckState(Qt.Checked)
        self.widget.action_tab.camera_trigger_check_box.setCheckState(Qt.Unchecked)
        # video_tab复位
        self.widget.video_tab.start_record_video.setCheckState(Qt.Unchecked)
        self.widget.video_tab.stop_record_video.setCheckState(Qt.Unchecked)
        # sleep_tab复位
        self.widget.sleep_tab.sleep_time_edit.setText('')
        self.widget.sleep_tab.sleep_time_edit.setPlaceholderText('请输入睡眠时间(单位:ms)')
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AddTabWidget(None)
    gui.show()
    sys.exit(app.exec_())