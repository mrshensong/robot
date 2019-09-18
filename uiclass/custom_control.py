from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import icon_path

# 自定义动作展示控件
class Custom_Control(QWidget):
    def __init__(self, parent, id, type='click'):
        super(Custom_Control, self).__init__(parent)
        self.id = id
        self.type = type
        self.initUI()

    def initUI(self):

        self.check_box = QCheckBox()
        self.check_box.stateChanged.connect(self.connect_check_box)

        if self.type == 'click':
            pix_map = QPixmap(icon_path.Icon_robot_click)
        elif self.type == 'double_click':
            pix_map = QPixmap(icon_path.Icon_robot_double_click)
        elif self.type == 'long_click':
            pix_map = QPixmap(icon_path.Icon_robot_long_click)
        elif self.type == 'slide':
            pix_map = QPixmap(icon_path.Icon_robot_slide)
        else:
            pix_map = QPixmap(icon_path.Icon_robot_click)
        self.type_label = QLabel(self)
        self.type_label.setPixmap(pix_map)

        self.des_line_edit = QLineEdit(self)
        self.points_line_edit = QLineEdit(self)
        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.des_line_edit)
        self.v_box.addWidget(self.points_line_edit)

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


# 动作添加控件
class Add_Action_Control(QDialog):

    def __init__(self, parent):
        super(Add_Action_Control, self).__init__(parent)
        self.initUI()


    # 初始化
    def initUI(self):
        self.general_layout = QVBoxLayout()
        #创建一个表单布局
        self.from_layout = QFormLayout()
        self.button_layout = QHBoxLayout()
        #设置标签右对齐, 不设置是默认左对齐
        self.from_layout.setLabelAlignment(Qt.AlignCenter)
        items = ['click', 'double_click', 'long_click', 'slide']

        # 设置表单内容
        # 动作描述
        self.des_text = QLineEdit(self)
        self.des_text.setPlaceholderText('请输入动作描述(可不写)')
        # 动作选择
        self.com_box = QComboBox(self)
        self.com_box.addItems(items)
        # 坐标
        self.points = QLineEdit(self)
        # 是否收回
        self.check_box = QCheckBox(self)
        self.check_box.setCheckState(Qt.Checked)
        # 表单布局
        self.from_layout.addRow('描述: ', self.des_text)
        self.from_layout.addRow('动作: ', self.com_box)
        self.from_layout.addRow('坐标: ', self.points)
        self.from_layout.addRow('是否收回: ', self.check_box)

        # 获取坐标
        self.get_points_button = QPushButton('获取坐标', self)
        self.get_points_button.clicked.connect(self.connect_get_points)
        # 确定按钮
        self.sure_button = QPushButton('确定', self)
        self.sure_button.clicked.connect(self.connect_sure)
        # 两个button横向布局
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.get_points_button)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.sure_button)
        self.button_layout.addStretch(1)

        self.general_layout.addLayout(self.from_layout)
        self.general_layout.addLayout(self.button_layout)

        self.setLayout(self.general_layout)
        # 设置字体
        QFontDialog.setFont(self, QFont('Times New Roman', 11))
        # 设置最小尺寸
        self.setMinimumWidth(300)


    def connect_get_points(self):
        pass


    def connect_sure(self):
        self.close()


import sys
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Add_Action_Control(None)
    win.show()
    sys.exit(app.exec_())