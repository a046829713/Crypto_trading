from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QWidget, QLineEdit
import sys
import os
from GUI.MainWindow_TC import Ui_MainWindow
from GUI.Login import Ui_WourLogin
from GUI.Error_Login import Ui_Dialog_Error

from PyQt6.QtCore import pyqtSignal
from Trading_Systeam import GUI_Trading_systeam
from PyQt6.QtCore import QThread
from DataProvider import DataProvider
import pandas as pd
import asyncio


class Error_Dialog(QDialog, Ui_Dialog_Error):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.pushButton_Error.clicked.connect(self.accept)


class Login_Dialog(QDialog, Ui_WourLogin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.pushButton_login.clicked.connect(self.Get_Login_info)
        self.pushButton_login.clicked.connect(self.accept)

        # 如果資料都在直接將其寫入
        if os.path.isfile(r"C:/bi_.txt") and os.path.isfile(r"C:/LINE_TOEKN.txt"):
            with open(r"C:/bi_.txt", 'r') as file:
                data = file.read()
                account = data.split("\n")[0]
                passwd = data.split("\n")[1]

            with open(r"C:/LINE_TOEKN.txt", 'r') as file:
                LINE_TOEKN = file.read()
                LINE_TOEKN = LINE_TOEKN.replace("\n","")
                print(LINE_TOEKN)

            self.checkBox_remeberpa.setChecked(True)
            self.lineEdit_api_key.setText(account)
            self.lineEdit_secret_key.setText(passwd)
            self.lineEdit_LINE.setText(LINE_TOEKN)

    def Get_Login_info(self):
        """
            取得登入資訊
        """
        self.api_key = self.lineEdit_api_key.text()
        self.secret_key = self.lineEdit_secret_key.text()
        self.LINE = self.lineEdit_LINE.text()

        if self.checkBox_remeberpa.isChecked():
            with open(r"C:/bi_.txt", 'w') as file:
                file.write(self.api_key + "\n")
                file.write(self.secret_key + "\n")

            with open(r"C:/LINE_TOEKN.txt", 'w') as file:
                file.write(self.LINE )

    def closeEvent(self, event):
        """
            關閉畫面
        """
        Form = QWidget()
        msg_box = QMessageBox(Form)
        result = msg_box.question(Form, 'question', '確認關閉系統?')

        if result == QMessageBox.StandardButton.Yes:
            sys.exit()
        else:
            event.ignore()


class TradeUI(QMainWindow, Ui_MainWindow):
    # 建立 pyqtSignal 物件，傳遞字串格式內容
    update_trade_info_signal = pyqtSignal(str)
    clear_info_signal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.show()

        # 建立插槽監聽信號
        self.update_trade_info_signal.connect(self.showMsg)
        self.clear_info_signal.connect(self.clear_Msg)

        
        self.actionAutoTrading.triggered.connect(self.click_btn_trade)
        
    def clear_Msg(self):
        self.trade_info.clear()

    def showMsg(self, out_str: str):
        """
            將訊號傳給GUI

        Args:
            out_str (str): _description_
        """

        self.trade_info.append(out_str)

    def click_btn_trade(self):
        self.systeam = GUI_Trading_systeam(self)

        def run_subscriptionData():
            # 回補資料
            asyncio.run(self.systeam.asyncDataProvider.subscriptionData(
                self.systeam.symbol_name))

        self.run_subscrip_Thread = QThread()
        self.run_subscrip_Thread.run = run_subscriptionData
        self.run_subscrip_Thread.start()

        self.Trading_systeam_Thread = QThread()
        self.Trading_systeam_Thread.setObjectName = "trade"
        self.Trading_systeam_Thread.run = self.systeam.main
        self.Trading_systeam_Thread.start()

    def reload_data_day(self):
        self.dataprovider = DataProvider(time_type='D')
        self.data_Thread = QThread()
        self.data_Thread.run = self.dataprovider.reload_all_data
        self.data_Thread.start()

    def reload_data_min(self):
        self.dataprovider = DataProvider()
        self.data_Thread = QThread()
        self.data_Thread.run = self.dataprovider.reload_all_data
        self.data_Thread.start()

    def click_save_data(self):
        """ 
        保存資料並關閉程序 注意不能使用replace 資料長短問題

        """

        def mergefunc():
            for name, each_df in self.systeam.new_symbol_map.items():
                # 不保存頭尾 # 異步模式 需要檢查這樣是否OK
                each_df.drop(
                    [each_df.index[0], each_df.index[-1]], inplace=True)

                each_df = each_df.astype(float)
                if len(each_df) != 0:
                    # 準備寫入資料庫裡面
                    self.systeam.dataprovider_online.save_data(
                        symbol_name=name, original_df=each_df, exists="append")

            print("保存資料完成-退出程序")
            sys.exit()

        self.save_data_Thread = QThread()
        self.save_data_Thread.run = mergefunc
        self.save_data_Thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    while True:
        dialog = Login_Dialog()

        # 如果用戶是執行登入
        if dialog.exec() == 1:
            if dialog.api_key and dialog.secret_key and dialog.LINE:
                BeginTDsys = TradeUI()
                sys.exit(app.exec())
            else:
                error_dialog = Error_Dialog()
                error_dialog.exec()
