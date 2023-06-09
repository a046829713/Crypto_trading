import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QProgressBar, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QThread, QTimer
from PyQt6 import QtCore


class ProgressThread(QThread):
    update_progress = QtCore.pyqtSignal(int)

    def run(self):
        for i in range(101):
            self.update_progress.emit(i)
            self.msleep(100)  # 模拟耗时操作


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.progress_bar = QProgressBar()
        self.progress_thread = ProgressThread()
        self.start_button = QPushButton("Start")

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.start_button)

        self.setCentralWidget(central_widget)

        self.progress_bar.setValue(0)
        self.progress_thread.update_progress.connect(self.update_progress_bar)
        self.start_button.clicked.connect(self.start_progress)

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def start_progress(self):
        self.progress_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
