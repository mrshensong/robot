import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QVBoxLayout, QFileSystemModel, QLineEdit
from PyQt5.QtCore import pyqtSignal
from GlobalVar import Logger


class ProjectBar(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, path):
        super(ProjectBar, self).__init__(parent)
        self.parent = parent
        self.path = path

        self.model = QFileSystemModel(self)
        # 改表头名字(无效)
        # self.model.setHeaderData(0, Qt.Horizontal, "123455")
        self.model.setRootPath(self.path)
        # 文件过滤
        # self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        # 需要显示的文件
        filters = ['*.mp4', '*.html', '*.jpg', '*.png', '*.xlsx', '*.xml', '*.txt', '*.ini']
        self.model.setNameFilters(filters)
        self.model.setNameFilterDisables(False)

        # 树形视图
        self.tree = QTreeView(self)  # 2
        self.tree.setModel(self.model)
        # 后面的size/type/data不显示
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.setHeaderHidden(True)
        self.tree.setRootIndex(self.model.index(self.path))
        self.tree.clicked.connect(self.show_info)
        self.tree.doubleClicked.connect(lambda : self.operation_file(None))

        self.info_label = QLineEdit(self)
        self.info_label.setText(self.path)

        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        self.v_layout.addWidget(self.info_label)
        self.v_layout.addWidget(self.tree)

        self.setLayout(self.v_layout)

    def show_info(self):  # 4
        index = self.tree.currentIndex()
        file_name = self.model.fileName(index)
        file_path = self.model.filePath(index)
        self.info_label.setText(file_path)
        # path = self.dirModel.fileInfo(index).absoluteFilePath()
        # self.listview.setRootIndex(self.fileModel.setRootPath(path))


    # 双击操作
    def operation_file(self, file_path=None):
        if file_path is None:
            index = self.tree.currentIndex()
            file_path = self.model.filePath(index)
        else:
            file_path = file_path
        # 判断双击是否为文件(只对文件操作)
        if os.path.isfile(file_path) is True:
            # 展示图片
            if file_path.endswith('.jpg') or file_path.endswith('.png'):
                self.signal.emit('open_picture>' + str(file_path))
            # 展示报告
            elif file_path.endswith('.html'):
                self.signal.emit('open_report>' + str(file_path))
            # 展示text
            elif file_path.split('.')[1] in ['txt', 'py', 'xml', 'md', 'ini']:
                self.signal.emit('open_text>' + str(file_path))
            else:
                Logger('暂不支持此类型文件!!!')
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    project_bar = ProjectBar(None)
    project_bar.show()
    sys.exit(app.exec_())