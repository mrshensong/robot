import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GlobalVar import icon_path

class Custom_Tools(QWidget):
    def __init__(self, parent, id, type='click'):
        super(Custom_Tools, self).__init__(parent)
        self.id = id
        self.type = type
        self.initUI()

    def initUI(self):

        self.check_box = QCheckBox()

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
        self.delte_botton = QToolButton(self)
        self.delte_botton.setStyleSheet('border-image: url(' + icon_path.Icon_custom_delete + ')')

        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.check_box)
        self.h_box.addWidget(self.type_label)
        self.h_box.addLayout(self.v_box)
        self.h_box.addWidget(self.play_botton)
        self.h_box.addWidget(self.delte_botton)
        self.setLayout(self.h_box)


    # def main():
    #     app = QApplication(sys.argv)
    #     ex = Custom_Tools(type='click')
    #     ex.show()
    #     sys.exit(app.exec_())


# class Demo(QWidget):
#     def __init__(self, parent):
#         super(Demo, self).__init__(parent)
#
#         self.tab_widget = QTabWidget(self)
#         self.tab_widget.setTabPosition(QTabWidget.South)
#
#         self.tab1 = QWidget()  # 1
#         self.tab2 = QTextEdit()
#
#         self.tab1_init()  # 2
#         # self.tab2_init()
#
#         self.tab_widget.addTab(self.tab1, 'action')
#         self.tab_widget.addTab(self.tab2, 'edit')
#
#
#         self.tab_widget.currentChanged.connect(lambda: print(self.tab_widget.currentIndex()))  # 4
#         self.setMinimumSize(400, 400)
#
#     def tab1_init(self):
#         button1 = QToolButton()
#         # button1.triggered.connect(self.add)
#         button1.clicked.connect(self.add)
#         button2 = QToolButton()
#         button3 = QToolButton()
#         button4 = QToolButton()
#         hbox = QHBoxLayout()
#         hbox.addWidget(button1)
#         hbox.addWidget(button2)
#         hbox.addWidget(button3)
#         hbox.addWidget(button4)
#         hbox.addStretch(1)
#
#         self.topFiller = QWidget()
#         # topFiller.setMinimumSize(350, 2000)  #######设置滚动条的尺寸
#         self.topFiller.setMinimumWidth(350)
#         self.topFiller.setMinimumHeight(180)
#         for filename in range(1):
#             MapButton = Custom_Tools(parent=self.topFiller, type='click')
#             MapButton.move(0, filename * 80)
#         ##创建一个滚动条
#         self.scroll = QScrollArea()
#         self.scroll.setWidget(self.topFiller)
#
#         vbox = QVBoxLayout()
#         vbox.addLayout(hbox)
#         vbox.addWidget(self.scroll)
#         self.tab1.setLayout(vbox)
#
#
#     def add(self):
#         print('into')
#         self.topFiller.setMinimumHeight(2000)
#         MapButton = Custom_Tools(parent=self.topFiller, type='click')
#         MapButton.move(0, 2 * 80)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     demo = Demo(None)
#     demo.show()
#     sys.exit(app.exec_())










class Demo(QWidget):
    def __init__(self, parent):
        super(Demo, self).__init__(parent)

        self.index = 0

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.South)

        self.tab1 = QWidget()  # 1
        self.tab2 = QTextEdit()

        self.tab1_init()  # 2
        # self.tab2_init()

        self.tab_widget.addTab(self.tab1, 'action')
        self.tab_widget.addTab(self.tab2, 'edit')


        self.tab_widget.currentChanged.connect(lambda: print(self.tab_widget.currentIndex()))  # 4
        self.setMinimumSize(400, 400)

    def tab1_init(self):
        button1 = QToolButton()
        button1.clicked.connect(self.add)
        button2 = QToolButton()
        button3 = QToolButton()
        button4 = QToolButton()
        hbox = QHBoxLayout()
        hbox.addWidget(button1)
        hbox.addWidget(button2)
        hbox.addWidget(button3)
        hbox.addWidget(button4)
        hbox.addStretch(1)

        self.topFiller = QListWidget()
        self.topFiller.setMinimumWidth(350)
        # self.topFiller.clicked.connect(self.connect_item)
        self.topFiller.setMouseTracking(True)
        self.topFiller.entered.connect(self.connect_item)
        ##创建一个滚动条
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.topFiller)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.scroll)
        self.tab1.setLayout(vbox)


    def add(self, type='click'):
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 80))
        MapButton = Custom_Tools(parent=None, id=self.index, type=type)
        self.topFiller.addItem(item)
        self.topFiller.setItemWidget(item, MapButton)
        print('the totle item is : ', self.topFiller.count())
        # MapButton.check_box.clicked.connect(lambda : self.connect_item(self.index))
        self.index += 1


    def connect_item(self):
        print('current index is : ', self.topFiller.currentIndex().row())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo(None)
    demo.show()
    sys.exit(app.exec_())