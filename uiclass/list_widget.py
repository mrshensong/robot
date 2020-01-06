from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import pyqtSignal

class ListWidget(QListWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ListWidget, self).__init__(parent)
        # 设置item可拖动
        self.setMovement(QListWidget.Free)
        self.setDragEnabled(True)


    def dropEvent(self, event):
        # 当前index
        current_index = self.currentRow()
        # 具体的item(根据此需要得到index索引)
        item = self.itemAt(event.pos())
        # 目标index
        aim_index = self.indexFromItem(item).row()
        if aim_index == current_index:
            return
        signal_str = str((current_index, aim_index))
        self.signal.emit('item_position_exchange>'+signal_str)