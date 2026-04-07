"""UI工作流"""
from SubWidget.WallPaper.ImportPack import *


class WaitInfoLoadWorkFlow(QThread):
    finished = Signal(object)  # 完成信号

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        while self.isRunning():
            if KeyWord.is_loaded() and ImageInfo.is_loaded():
                self.finished.emit(KeyWord.data())
                break
            time.sleep(1)
