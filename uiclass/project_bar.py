import os
import sys
import time
import shutil
from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QVBoxLayout, QFileSystemModel, QLineEdit, QMenu, QAction, QInputDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt, QDir
from GlobalVar import Logger, MergePath


class ProjectBar(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, path):
        super(ProjectBar, self).__init__(parent)
        # 设置工程栏背景颜色
        self.setStyleSheet('background-color: #F0F0F0;')
        self.parent = parent
        self.path = path

        self.model = QFileSystemModel(self)
        # 改表头名字(无效)
        # self.model.setHeaderData(0, Qt.Horizontal, "123455")
        # 文件过滤
        # self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        # 需要显示的文件
        # filters = ['*.mp4', '*.avi', '*.mov', '*.flv', '*.html', '*.jpg', '*.png', '*.xls', '*.xlsx', '*.xml', '*.txt', '*.ini']
        filters = ['*']
        self.model.setRootPath(self.path)
        self.model.setNameFilters(filters)
        self.model.setNameFilterDisables(False)

        # 树形视图
        self.tree = QTreeView(self)  # 2
        # 右键菜单
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_menu)
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
        self.info_label.setReadOnly(True)
        self.info_label.setText(self.path)

        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        self.v_layout.addWidget(self.info_label)
        self.v_layout.addWidget(self.tree)

        self.setLayout(self.v_layout)


    def show_menu(self, point):
        index = self.tree.indexAt(point)
        # 如果点击的非空白区域
        if index.isValid():
            # 当前节点路径以及名字
            # index = self.tree.currentIndex()
            node_name = self.model.fileName(index)
            node_path = self.model.filePath(index)
            blank_click_flag = False
        # 点击空白区域
        else:
            self.tree.clearSelection()
            node_name = os.path.split(self.path)[1]
            node_path = self.path
            blank_click_flag = True
        # 更新显示标签
        self.info_label.setText(node_path)
        # 菜单样式
        menu_qss = "QMenu{color: #E8E8E8; background: #4D4D4D; margin: 2px;}\
                    QMenu::item{padding:3px 20px 3px 20px;}\
                    QMenu::indicator{width:13px; height:13px;}\
                    QMenu::item:selected{color:#E8E8E8; border:0px solid #575757; background:#1E90FF;}\
                    QMenu::separator{height:1px; background:#757575;}"
        self.menu = QMenu(self)
        self.menu.setStyleSheet(menu_qss)
        # 新建文件
        self.new_file_action = QAction('新建文件', self)
        self.new_file_action.triggered.connect(lambda : self.new_file_dialog(index, node_path, blank_click_flag))
        # 新建文件夹
        self.new_folder_action = QAction('新建文件夹', self)
        self.new_folder_action.triggered.connect(lambda : self.new_folder_dialog(index, node_path, blank_click_flag))
        # 重命名
        self.rename_action = QAction('重命名', self)
        self.rename_action.triggered.connect(lambda : self.rename_dialog(node_path, node_name, blank_click_flag))
        # 删除
        self.delete_action = QAction('删除', self)
        self.delete_action.triggered.connect(lambda : self.delete_dialog(node_path, blank_click_flag))
        # 菜单添加action
        self.menu.addAction(self.new_file_action)
        self.menu.addAction(self.new_folder_action)
        self.menu.addAction(self.rename_action)
        self.menu.addAction(self.delete_action)
        self.menu.exec(self.tree.mapToGlobal(point))


    # 新建文件
    def new_file_dialog(self, index, node_path, blank_click_flag):
        title, prompt_text, default_name = '新建文件', '请输入文件名', ''
        file_name, ok = QInputDialog.getText(self, title, prompt_text, QLineEdit.Normal, default_name)
        if ok:
            if os.path.isdir(node_path) is True:
                root_path = node_path
                # 展开文件夹
                self.tree.setExpanded(index, True)
            else:
                root_path = os.path.dirname(node_path)
            file_path = MergePath([root_path, file_name]).merged_path
            f = open(file_path, 'w', encoding='utf-8')
            f.close()
            Logger('新建文件: %s' % file_path)
            # 判断是否在空白区域
            if blank_click_flag is True:
                # index = self.model.index(QDir.currentPath())
                # index = self.model.index(file_path)
                Thread(target=self.update_selecte_item, args=(file_path,)).start()
            else:
                # 更新选中item
                Thread(target=self.update_selecte_item, args=(file_path,)).start()


    # 新建文件夹
    def new_folder_dialog(self, index, node_path, blank_click_flag):
        title, prompt_text, default_name = '新建文件夹', '请输入文件夹名', ''
        folder_name, ok = QInputDialog.getText(self, title, prompt_text, QLineEdit.Normal, default_name)
        if ok:
            if os.path.isdir(node_path) is True:
                root_path = node_path
                # 展开文件夹
                self.tree.setExpanded(index, True)
            else:
                root_path = os.path.dirname(node_path)
            folder_path = MergePath([root_path, folder_name]).merged_path
            os.makedirs(folder_path)
            Logger('新建文件夹: %s' % folder_path)
            # 判断是否在空白区域
            if blank_click_flag is True:
                # index = self.model.index(QDir.currentPath())
                Thread(target=self.update_selecte_item, args=(folder_path,)).start()
            else:
                # 更新选中item
                Thread(target=self.update_selecte_item, args=(folder_path,)).start()


    # 重命名
    def rename_dialog(self, node_path, node_name, blank_click_flag):
        if blank_click_flag is True:
            return
        title, prompt_text, default_name = '重命名', '请输入新文件名', node_name
        new_name, ok = QInputDialog.getText(self, title, prompt_text, QLineEdit.Normal, default_name)
        if ok:
            root_path = os.path.dirname(node_path)
            new_name_path = MergePath([root_path, new_name]).merged_path
            os.rename(node_path, new_name_path)
            Logger('重命名 %s 为: %s' % (node_path, new_name_path))
            Thread(target=self.update_selecte_item, args=(new_name_path,)).start()


    # 删除文件
    def delete_dialog(self, node_path, blank_click_flag):
        if blank_click_flag is True:
            return
        # file_flag判断是文件还是文件夹(文件为True,文件夹为False)
        if os.path.isdir(node_path) is True:
            file_flag = False
            prompt_text = '确定要删除此文件夹吗？'
        else:
            file_flag = True
            prompt_text = '确定要删除此文件吗？'
        # 判断是否确定删除
        reply = QMessageBox.question(self, '删除栏', prompt_text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 获取删除项下一项名字
            name = self.tree.indexBelow(self.model.index(node_path)).data()
            parent_path = os.path.split(node_path)[0]
            # 确保路径存在
            selected_path = parent_path if name is None else MergePath([parent_path, name]).merged_path
            if os.path.exists(selected_path) is False:
                selected_path = parent_path
            Thread(target=self.update_selecte_item, args=(selected_path,)).start()
            self.info_label.setText(selected_path)
            if file_flag is True:
                os.remove(node_path)
                Logger('删除文件: %s' % node_path)
            else:
                shutil.rmtree(node_path)
                Logger('删除文件夹: %s' % node_path)


    # 更新选中item(必须异步线程才能选中, 也就是等待文件model更新完成, 延时时间不能太短)
    def update_selecte_item(self, path):
        time.sleep(0.04)
        new_index = self.model.index(path)
        self.tree.setCurrentIndex(new_index)
        self.info_label.setText(path)


    # 更新文件名字显示
    def show_info(self):  # 4
        index = self.tree.currentIndex()
        if index.isValid():
            file_name = self.model.fileName(index)
            file_path = self.model.filePath(index)
            self.info_label.setText(file_path)


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
            if file_path.endswith('.jpg') or file_path.endswith('.png') or file_path.endswith('.bmp'):
                self.signal.emit('open_picture>' + str(file_path))
            # 展示报告
            elif file_path.endswith('.html'):
                self.signal.emit('open_report>' + str(file_path))
            # 展示text
            elif file_path.split('.')[1] in ['txt', 'py', 'xml', 'md', 'ini']:
                self.signal.emit('open_text>' + str(file_path))
            # 播放视频
            elif file_path.split('.')[1] in ['mp4', 'MP4', 'avi', 'AVI', 'mov', 'MOV', 'flv', 'FLV']:
                self.signal.emit('open_video>' + str(file_path))
            # 展示excel文件
            elif file_path.split('.')[1] in ['xls', 'xlsx', 'XLS', 'XLSX']:
                self.signal.emit('open_excel>' + str(file_path))
            else:
                Logger('暂不支持此类型文件!!!')
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    project_bar = ProjectBar(None)
    project_bar.show()
    sys.exit(app.exec_())