from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from GlobalVar import icon_path

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
        self.play_botton.setStyleSheet('border-image: url(' + icon_path.Icon_custom_play + ')')
        self.delete_botton = QToolButton(self)
        self.delete_botton.setStyleSheet('border-image: url(' + icon_path.Icon_custom_delete + ')')

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.type_label)
        self.h_box.addLayout(self.v_box)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delete_botton)
        self.setLayout(self.h_box)


    def connect_check_box(self):
        print('the id is : ', self.id)