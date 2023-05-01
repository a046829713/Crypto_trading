import sys
from PyQt6.QtCore import Qt, QBasicTimer
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget


class ProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Progress Bar')

        self.timer = QBasicTimer()
        self.step = 0

    def timerEvent(self, e):
        if self.step >= 100:
            self.timer.stop()
            return

        self.step = self.step + 1
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawProgress(qp)
        qp.end()

    def drawProgress(self, qp):
        qp.setPen(QColor(0, 0, 0))
        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(10, 40, 230, 30)

        progressWidth = (self.step / 100) * 230
        qp.setBrush(QColor(0, 200, 0))
        qp.drawRect(10, 40, progressWidth, 30)

    def startProgressBar(self):
        self.timer.start(100, self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    progressBar = ProgressBar()
    progressBar.show()
    progressBar.startProgressBar()
    sys.exit(app.exec())
