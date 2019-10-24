import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QLabel, QVBoxLayout, QFileSystemModel, QLineEdit
from PyQt5.QtCore import Qt


class ProjectBar(QWidget):
    def __init__(self, parent):
        super(ProjectBar, self).__init__(parent)
        self.parent = parent
        self.path = 'D:/Code/Robot/robot'

        self.model = QFileSystemModel(self)
        # self.model.setData()
        self.model.setHeaderData(0, Qt.Horizontal, "123455")
        self.model.setRootPath(self.path)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    project_bar = ProjectBar(None)
    project_bar.show()
    sys.exit(app.exec_())