# Form implementation generated from reading ui file '.\MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from Trading_Systeam import Trading_systeam
import threading
import sys
from utils.Debug_tool import debug
import time


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1083, 662)
        self.btn_trade = QtWidgets.QPushButton(Form)
        self.btn_trade.setGeometry(QtCore.QRect(30, 30, 141, 91))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.btn_trade.setFont(font)
        self.btn_trade.setStyleSheet("background-color: rgb(140, 215, 144);\n"
                                     "color: rgb(255, 255, 255);")
        self.btn_trade.setObjectName("btn_trade")
        self.btn_trade.clicked.connect(self.click_btn_trade)

        self.trade_info = QtWidgets.QTextEdit(Form)
        self.trade_info.setGeometry(QtCore.QRect(190, 30, 871, 601))
        self.trade_info.setReadOnly(True)
        self.trade_info.setObjectName("trade_info")
        self.btn_savedata = QtWidgets.QPushButton(Form)
        self.btn_savedata.setGeometry(QtCore.QRect(30, 140, 141, 91))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.btn_savedata.setFont(font)
        self.btn_savedata.setStyleSheet("background-color: rgb(238, 119, 133);\n"
                                        "color: rgb(255, 255, 255);")
        self.btn_savedata.setObjectName("btn_savedata")
        self.btn_savedata.clicked.connect(self.click_save_data)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Binance trade systeam"))
        self.btn_trade.setText(_translate("Form", "啟動程序"))
        self.trade_info.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'Microsoft JhengHei UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                           "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.trade_info.setPlaceholderText(_translate("Form", "程序尚未運行..."))
        self.btn_savedata.setText(_translate("Form", "關閉程序"))







if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
