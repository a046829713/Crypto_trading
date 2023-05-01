# Form implementation generated from reading ui file '.\GUI\disclamier.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_DisCalmier_Dialog(object):
    def setupUi(self, DisCalmier_Dialog):
        DisCalmier_Dialog.setObjectName("DisCalmier_Dialog")
        DisCalmier_Dialog.resize(737, 617)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\GUI\\Images/binance.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        DisCalmier_Dialog.setWindowIcon(icon)
        DisCalmier_Dialog.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,\n"
"                                    stop: 0 #4c4c4c, stop: 1 #1f1f1f);")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(DisCalmier_Dialog)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.disclamier_label = QtWidgets.QLabel(parent=DisCalmier_Dialog)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.disclamier_label.setFont(font)
        self.disclamier_label.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgba(255, 255, 255,0);")
        self.disclamier_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.disclamier_label.setObjectName("disclamier_label")
        self.verticalLayout.addWidget(self.disclamier_label)
        self.disclamier_textEdit = QtWidgets.QTextEdit(parent=DisCalmier_Dialog)
        self.disclamier_textEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.disclamier_textEdit.setReadOnly(True)
        self.disclamier_textEdit.setObjectName("disclamier_textEdit")
        self.verticalLayout.addWidget(self.disclamier_textEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_agree = QtWidgets.QPushButton(parent=DisCalmier_Dialog)
        self.pushButton_agree.setMinimumSize(QtCore.QSize(0, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        self.pushButton_agree.setFont(font)
        self.pushButton_agree.setStyleSheet("background-color: rgb(0, 170, 127);\n"
"color: rgb(255, 255, 255);")
        self.pushButton_agree.setObjectName("pushButton_agree")
        self.horizontalLayout.addWidget(self.pushButton_agree)
        self.pushButton_disagree = QtWidgets.QPushButton(parent=DisCalmier_Dialog)
        self.pushButton_disagree.setMinimumSize(QtCore.QSize(0, 60))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.pushButton_disagree.setFont(font)
        self.pushButton_disagree.setStyleSheet("background-color: rgb(255, 85, 0);\n"
"color: rgb(255, 255, 255);")
        self.pushButton_disagree.setObjectName("pushButton_disagree")
        self.horizontalLayout.addWidget(self.pushButton_disagree)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(DisCalmier_Dialog)
        QtCore.QMetaObject.connectSlotsByName(DisCalmier_Dialog)

    def retranslateUi(self, DisCalmier_Dialog):
        _translate = QtCore.QCoreApplication.translate
        DisCalmier_Dialog.setWindowTitle(_translate("DisCalmier_Dialog", "Dialog"))
        self.disclamier_label.setText(_translate("DisCalmier_Dialog", "免責聲明"))
        self.disclamier_textEdit.setHtml(_translate("DisCalmier_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Microsoft JhengHei UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">本交易系統僅供參考和使用，並不構成任何投資建議或交易建議。任何人士在使用本交易系統前，應仔細評估其風險和適用性。使用本交易系統所造成的任何損失或損害，概不承擔任何責任。</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; font-weight:700;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">使用本交易系統前，您應該了解所有有關投資和交易的風險。投資和交易都帶有風險，可能導致資金損失。本交易系統作者和開發人員，不對使用本交易系統所造成的任何損失或損害負責。</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; font-weight:700;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">使用本交易系統前，您應該詳細閱讀本免責聲明，並在自己的風險承受能力範圍內進行操作。如有任何疑問，請勿猶豫，請尋求專業意見。</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; font-weight:700;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">以上免責聲明是本交易系統的一部分，如您不同意這些條款，請停止使用本交易系統。如果您繼續使用本交易系統，則視為您已接受本免責聲明的所有條款和條件。</span></p></body></html>"))
        self.pushButton_agree.setText(_translate("DisCalmier_Dialog", "同意"))
        self.pushButton_disagree.setText(_translate("DisCalmier_Dialog", "不同意"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DisCalmier_Dialog = QtWidgets.QDialog()
    ui = Ui_DisCalmier_Dialog()
    ui.setupUi(DisCalmier_Dialog)
    DisCalmier_Dialog.show()
    sys.exit(app.exec())
