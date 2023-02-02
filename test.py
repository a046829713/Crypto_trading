import sys
from PyQt6 import QtCore, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    updateSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel("Original Text")
        self.setCentralWidget(self.label)
        self.updateSignal.connect(self.updateLabel)

    def updateLabel(self, text):
        self.label.setText(text)

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    @QtCore.pyqtSlot()
    def work(self):
        # Do time-consuming work here
        # ...

        # Emit signal to update GUI
        self.main_window.updateSignal.emit("Updated Text")
        self.finished.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    worker = Worker(main_window)
    thread = QtCore.QThread()
    worker.moveToThread(thread)
    worker.finished.connect(thread.quit)
    thread.started.connect(worker.work)
    thread.start()

    sys.exit(app.exec_())
