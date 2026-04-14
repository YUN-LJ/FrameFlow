"""UI工作流"""
from SubWidget.ImportPack import *


class WaitInfoLoadWorkFlow(QThread):
    finished = Signal()  # 完成信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isFinished = False
        self.parent = parent

    def run(self):
        while self.isRunning():
            if KeyWord.is_loaded() and ImageInfo.is_loaded():
                for key_word in WP.Config.IMAGE_CHOICE_KEY:
                    self.parent.selected_cells.append(key_word)
                self.isFinished = True
                self.finished.emit()
                break
            time.sleep(1)
