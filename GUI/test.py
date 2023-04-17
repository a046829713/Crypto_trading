from PyQt6 import QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)

Form = QtWidgets.QWidget()
Form.setWindowTitle('oxxo.studio')
Form.resize(300, 300)

def show():
    mbox = QtWidgets.QMessageBox()       # 加入對話視窗
    mbox.information('info', 'hello')  # 開啟資訊通知的對話視窗，標題 info，內容 hello

btn = QtWidgets.QPushButton(Form)
btn.move(10, 10)
btn.setText('彈出視窗')
btn.clicked.connect(show)

Form.show()
sys.exit(app.exec())