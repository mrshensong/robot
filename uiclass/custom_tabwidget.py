import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GlobalVar import icon_path
from uiclass.custom_control import Custom_Control

class Custom_TabWidget(QTabWidget):
    def __init__(self, parent, tab1='action', tab2='edit'):
        super(Custom_TabWidget, self).__init__(parent)
        self.index = -1
        self.setTabPosition(self.South)
        self.tab1 = QWidget()  # 1
        self.tab2 = QTextEdit()
        self.tab1_init()  # 2
        # self.tab2_init()
        self.addTab(self.tab1, tab1)
        self.addTab(self.tab2, tab2)
        # 自定义控件列表
        self.custom_control_list = []
        # item列表
        self.item_list = []


    def tab1_init(self):
        self.add_button = QToolButton()
        self.add_button.setToolTip('add')
        self.add_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_add + ')}')
        self.add_button.clicked.connect(self.add_item)
        self.delete_button = QToolButton()
        self.delete_button.setToolTip('delete')
        self.delete_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_delete + ')}')
        self.delete_button.clicked.connect(self.clear)
        self.select_all_button = QToolButton()
        self.select_all_button.setToolTip('select_all')
        self.select_all_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_all_select + ')}')
        self.execute_button = QToolButton()
        self.execute_button.setToolTip('execute')
        self.execute_button.setStyleSheet('QToolButton{border-image: url(' + icon_path.Icon_tab_widget_execute + ')}')
        h_box = QHBoxLayout()
        h_box.addWidget(self.add_button)
        h_box.addWidget(self.delete_button)
        h_box.addWidget(self.select_all_button)
        h_box.addWidget(self.execute_button)
        h_box.addStretch(1)

        self.list_widget = QListWidget(self.tab1)
        v_box = QVBoxLayout()
        v_box.addLayout(h_box)
        v_box.addWidget(self.list_widget)
        self.tab1.setLayout(v_box)


    def add_item(self, type='click'):
        self.index += 1
        item = QListWidgetItem()
        item.setSizeHint(QSize(330, 80))
        obj = Custom_Control(parent=None, id=self.index, type=type)
        obj.id = self.index
        obj.play_botton.clicked.connect(lambda : self.play_item(obj.id))
        obj.delete_botton.clicked.connect(lambda : self.delete_item(obj.id))
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, obj)
        print('the totle item is : ', self.list_widget.count())
        self.item_list.append(obj)
        self.custom_control_list.append(obj)


    def play_item(self, id):
        print('play', id)


    def delete_item(self, id):
        print('delete', id)
        self.list_widget.takeItem(id)
        self.item_list.pop(id)
        self.custom_control_list.pop(id)
        for i in range(id, self.index):
            self.custom_control_list[i].id = i
        self.index -= 1


    def clear(self):
        self.list_widget.clear()
        self.item_list = []
        self.custom_control_list = []
        self.index = -1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Custom_TabWidget(None)
    demo.show()
    sys.exit(app.exec_())