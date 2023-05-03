from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QWidget, QLineEdit
import sys
import os
from GUI.MainWindow_TC import Ui_MainWindow
from GUI.Login import Ui_WourLogin
from GUI.Error_Login import Ui_Dialog_Error
from GUI.disclamier import Ui_DisCalmier_Dialog
from PyQt6.QtCore import pyqtSignal
from Trading_Systeam import GUI_Trading_systeam
from PyQt6.QtCore import QThread
from Major.DataProvider import DataProvider
import pandas as pd
import asyncio
from PyQt6.QtCore import  QPointF
from PyQt6.QtCharts import QChart, QChartView, QLineSeries

from PyQt6 import QtCore, QtGui, QtWidgets

class Error_Dialog(QDialog, Ui_Dialog_Error):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.pushButton_Error.clicked.connect(self.accept)

class DisCalmier_Dialog(QDialog,Ui_DisCalmier_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        
        self.pushButton_agree.clicked.connect(self.accept)
        self.pushButton_disagree.clicked.connect(self.reject)
        
class Login_Dialog(QDialog, Ui_WourLogin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.pushButton_login.clicked.connect(self.Get_Login_info)
        
        # 通常在對話框內使用「確定」或「確認」按鈕時，會在按下按鈕後呼叫 accept() 方法以關閉對話框並返回一個確認信號給父窗口，以通知已經成功執行動作。
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
    GUI_CloseProfit = pyqtSignal(list)
    
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.show()

        # 建立插槽監聽信號
        self.update_trade_info_signal.connect(self.showMsg)
        self.clear_info_signal.connect(self.clear_Msg)
        self.GUI_CloseProfit.connect(self.line_chart)
        self.actionAutoTrading.triggered.connect(self.click_btn_trade)
        
        self.actionSaveData.triggered.connect(self.click_save_data)
        self.actionReload_Day_Data.triggered.connect(self.reload_data_day)
        self.actionReload_Min_Data.triggered.connect(self.reload_data_min)
        
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
        
        def run_trading_systeam():
            asyncio.run(self.systeam.main())
            
        self.run_subscrip_Thread = QThread()
        self.run_subscrip_Thread.run = run_subscriptionData
        self.run_subscrip_Thread.start()

        self.Trading_systeam_Thread = QThread()
        self.Trading_systeam_Thread.setObjectName = "trade"
        self.Trading_systeam_Thread.run = run_trading_systeam
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

    def line_chart(self, data: list):
        print("取得line_chart傳送資料:",data)
        print("取得line_chart傳送資料的型態:",type(data))
        series = QLineSeries()

        for i, val in enumerate(data):
            series.append(QPointF(i+1, val))

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("CloseProfit")

        #adding animation
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)

        #adding theme
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)

        chartview = QChartView(chart)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.CloseProfit_tab)
        self.verticalLayout.addWidget(chartview)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    DisCalmier_dialog = DisCalmier_Dialog()
    if DisCalmier_dialog.exec() == 1:
        while True:
            
            
            Login_dialog = Login_Dialog()

            # 如果用戶是執行登入
            if Login_dialog.exec() == 1:
                if Login_dialog.api_key and Login_dialog.secret_key and Login_dialog.LINE:
                    BeginTDsys = TradeUI()
                    sys.exit(app.exec())
                else:
                    error_dialog = Error_Dialog()
                    error_dialog.exec()
    else:
        sys.exit()