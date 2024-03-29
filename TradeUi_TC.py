from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QWidget, QLineEdit
import sys
import os
from GUI.MainWindow_TC import Ui_MainWindow
from GUI.Login import Ui_WourLogin
from GUI.Error_Login import Ui_Dialog_Error
from GUI.disclamier import Ui_DisCalmier_Dialog
from GUI.DeadLine import Ui_Dialog_DeadLine
from GUI.Phone_error import Ui_Dialog_Phone_error
from GUI.Accept import Ui_Accept_Dialog
from GUI.Reload import Ui_Reload_Dialog
from PyQt6.QtCore import pyqtSignal
from Trading_Systeam import GUI_Trading_systeam, Trading_systeam
from PyQt6.QtCore import QThread
from Major.DataProvider import DataProvider
import asyncio
from PyQt6.QtCore import QPointF
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6 import QtCore, QtGui, QtWidgets
from utils.Debug_tool import debug
from utils.ExecHash import GetHashKey
from AppSetting import AppSetting
import datetime
from Database.clients import checkIfDataBase
import time
from utils import BackUp

def checkifUserDeadlineEnd():
    with open(r'C:\PhoneNumber.txt', 'r') as file:
        number = file.read()

    UserDeadline = AppSetting.get_UserDeadline()
    if UserDeadline.get(GetHashKey(number), None) is not None:
        if UserDeadline[GetHashKey(number)] > str(datetime.date.today()):
            return True

    return False


class Reload_Dialog(QDialog, Ui_Reload_Dialog):
    update_info = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 將關閉按鈕移除
        self.setWindowFlags(self.windowFlags() & ~
                            QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.Main_progressBar.setValue(0)
        self.show()


class Accept_Dialog(QDialog, Ui_Accept_Dialog):
    def __init__(self, maincontent: str):
        """
        將要秀給使用者的訊息顯示出來
        Args:
            maincontent (str): 
        """
        super().__init__()
        self.setupUi(self)
        # 當設定對話模式之後,如果使用者不點擊確認按鈕會形成堵塞
        self.setModal(True)
        self.show()
        self.Main_label.setText(maincontent)
        self.check_buttonBox.accepted.connect(self.accept)


class Phone_error_Dialog(QDialog, Ui_Dialog_Phone_error):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.pushButton_accept.clicked.connect(self.accept)


class DeadLine_Dialog(QDialog, Ui_Dialog_DeadLine):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.pushButton_accept.clicked.connect(self.accept)


class Error_Dialog(QDialog, Ui_Dialog_Error):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.pushButton_Error.clicked.connect(self.accept)


class DisCalmier_Dialog(QDialog, Ui_DisCalmier_Dialog):
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

        # 輸入setting版本號碼
        self.label_version.setText(f"Version:{AppSetting.get_version()}")

        self.pushButton_login.clicked.connect(self.Get_Login_info)

        # 通常在對話框內使用「確定」或「確認」按鈕時，會在按下按鈕後呼叫 accept() 方法以關閉對話框並返回一個確認信號給父窗口，以通知已經成功執行動作。
        self.pushButton_login.clicked.connect(self.accept)

        # 如果資料都在直接將其寫入
        if os.path.isfile(r"C:/bi_.txt") and os.path.isfile(r"C:/LINE_TOEKN.txt") and os.path.isfile(r"C:/PhoneNumber.txt"):
            with open(r"C:/bi_.txt", 'r') as file:
                data = file.read()
                account = data.split("\n")[0]
                passwd = data.split("\n")[1]

            with open(r"C:/LINE_TOEKN.txt", 'r') as file:
                LINE_TOEKN = file.read()
                LINE_TOEKN = LINE_TOEKN.replace("\n", "")

            with open(r"C:/PhoneNumber.txt", 'r') as file:
                PhoneNumber = file.read()
                PhoneNumber = PhoneNumber.replace("\n", "")

            self.checkBox_remeberpa.setChecked(True)
            self.lineEdit_api_key.setText(account)
            self.lineEdit_secret_key.setText(passwd)
            self.lineEdit_LINE.setText(LINE_TOEKN)
            self.lineEdit_Phone.setText(PhoneNumber)

    def Get_Login_info(self):
        """
            取得登入資訊
        """
        self.api_key = self.lineEdit_api_key.text()
        self.secret_key = self.lineEdit_secret_key.text()
        self.LINE = self.lineEdit_LINE.text()
        self.PhoneNumber = self.lineEdit_Phone.text()

        if self.checkBox_remeberpa.isChecked():
            with open(r"C:/bi_.txt", 'w') as file:
                file.write(self.api_key + "\n")
                file.write(self.secret_key + "\n")

            with open(r"C:/LINE_TOEKN.txt", 'w') as file:
                file.write(self.LINE)

            with open(r"C:/PhoneNumber.txt", 'w') as file:
                file.write(self.PhoneNumber)

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

    def __init__(self, activate) -> None:
        super().__init__()
        self.setupUi(self)
        self.show()

        self.systeam = None
        self.chartview = None

        # 檢查資料庫是否存在
        checkIfDataBase()

        # 檢察系統是否啟動
        self.Trading_systeam_Thread = None
        # 取得起始日期
        # 進入日期檢查點
        self.GuiStartDay = str(datetime.date.today())
        self.DailyChange()

        # 建立插槽監聽信號
        self.update_trade_info_signal.connect(self.showMsg)
        self.clear_info_signal.connect(self.clear_Msg)
        self.GUI_CloseProfit.connect(self.line_chart)

        self.actionAutoTrading.triggered.connect(self.click_btn_trade)
        self.actionSaveData.triggered.connect(self.click_save_data)
        self.actionReload_Day_Data.triggered.connect(self.reload_data_day)
        self.actionReload_Min_Data.triggered.connect(self.reload_data_min)
        
        self.actionExport_all_tables.triggered.connect(self.export_all_tables)
        self.actionImport_all_talbes.triggered.connect(
            self.import_all_tables)

        # 優化結果保存
        self.actionimport.triggered.connect(self.importOptimizeResult)
        self.actionexport.triggered.connect(self.exportOptimizeResult)
        
        # 平均虧損
        self.actionExportavgloss.triggered.connect(self.exportavgloss)
        self.actionImportavgloss.triggered.connect(self.importavgloss)
        
        if activate == '--autostart':
            self.click_btn_trade()

    def DailyChange(self):
        """
            每天都要重新關閉,怕資料量過大,並且會重新讀取每天的強勢標的
        """
        def _dailyChange():
            while True:
                if self.Trading_systeam_Thread is not None:
                    if str(datetime.date.today()) != self.GuiStartDay:
                        self.click_save_data()
                # 每5分鐘判斷一次就好
                time.sleep(300)

        self.DailyChange_Thread = QThread()
        self.DailyChange_Thread.run = _dailyChange
        self.DailyChange_Thread.start()

    def thread_finished(self):
        self.exportOptimizeResultThread.quit()
        self.exportOptimizeResultThread.wait()

    def exportOptimizeResult(self):
        self.BuildSysteam("exportOptimizeResult")

    def _exportOptimizeResult(self):
        self.exportOptimizeResultThread = QThread()
        self.exportOptimizeResultThread.finished.connect(
            self.exportOptimizeResultThread.deleteLater)
        self.exportOptimizeResultThread.finished.connect(self.thread_finished)
        self.exportOptimizeResultThread.run = self.systeam.exportOptimizeResult
        self.exportOptimizeResultThread.start()

        self.Accept_dialog = Accept_Dialog("優化資料導出完成")
        self.Accept_dialog.exec()

    def importOptimizeResult(self):
        self.importOptimizeResultThread = QThread()
        self.importOptimizeResultThread.run = Trading_systeam().importOptimizeResult()
        self.importOptimizeResultThread.start()
        
    def importavgloss(self):
        self.importavglossThread = QThread()
        self.importavglossThread.run = Trading_systeam().importavgloss()
        self.importavglossThread.start()
        
    def exportavgloss(self):
        self.exportavglossThread = QThread()
        self.exportavglossThread.run = Trading_systeam().exportavgloss()
        self.exportavglossThread.start()

    def import_all_tables(self):
        """
            在設計的思考上,回補資料等不需要進入系統的操作應該要獨立出來
        """ 
        self.import_all_tables_Thread = QThread()
        self.import_all_tables_Thread.run = BackUp.DatabaseBackupRestore().import_all_tables()
        self.import_all_tables_Thread.start()
    
    def export_all_tables(self):        
        self.export_all_tables_Thread = QThread()
        self.export_all_tables_Thread.run = Trading_systeam().export_all_tables()
        self.export_all_tables_Thread.start()
    
    def _close_reload_dialog(self):
        # 當系統建置之後,關閉原本的畫面
        self.reload_dialog.close()

    def update_progress_bar(self, value):
        """
            用來更新回補畫面的進度條

        Args:
            value (_type_): _description_
        """
        self.reload_dialog.Main_progressBar.setValue(value)

    def BuildSysteam(self, judgeevent: str):
        """
            應該會有兩種情況
        Args:
            judgeevent (str): 事件名稱:

        """
        if self.systeam is None:
            self.reload_dialog = Reload_Dialog()
            self.reload_dialog.update_info.connect(self.update_progress_bar)

            def _run_systeam():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.systeam = GUI_Trading_systeam(self)

            self.run_systeam_Thread = QThread()
            self.run_systeam_Thread.run = _run_systeam

            if judgeevent == 'exportOptimizeResult':
                self.run_systeam_Thread.finished.connect(
                    self._close_reload_dialog)
                self.run_systeam_Thread.finished.connect(
                    self._exportOptimizeResult)
            elif judgeevent == 'Trading':
                self.run_systeam_Thread.finished.connect(
                    self._close_reload_dialog)
                self.run_systeam_Thread.finished.connect(
                    self._Trading)
            self.run_systeam_Thread.start()
        else:
            if judgeevent == 'exportOptimizeResult':
                self._exportOptimizeResult()
            elif judgeevent == 'Trading':
                self._Trading()

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
        self.BuildSysteam("Trading")

    def _Trading(self):
        def run_subscriptionData():
            try:
                asyncio.run(self.systeam.asyncDataProvider.subscriptionData(
                    self.systeam.symbol_name))
            except:
                debug.print_info()

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
        self.dataprovider = DataProvider()
        self.data_Thread = QThread()
        self.data_Thread.run = lambda: self.dataprovider.reload_all_data(
            time_type='D')
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
                # 不保存頭尾 # 異步模式
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

    def _inint_line_chart(self):
        """ 定義初始化的圖表"""
        # create the QVBoxLayout layout
        self.verticalLayout_Profit = QtWidgets.QVBoxLayout(
            self.CloseProfit_tab)

        # create the QChartView widget
        self.chartview = QChartView(self)

        # add the QChartView widget to the layout
        self.verticalLayout_Profit.addWidget(self.chartview)

    def line_chart(self, data: list):
        if self.chartview is None:
            self._inint_line_chart()

        series = QLineSeries()

        for i, val in enumerate(data):
            series.append(QPointF(i+1, val))

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("CloseProfit")

        # adding animation
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)

        # adding theme
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)

        # set the chart to the QChartView widget
        self.chartview.setChart(chart)


if __name__ == '__main__':
    try:
        if '--autostart' in sys.argv:
            # 檢查是否過期
            if checkifUserDeadlineEnd():
                app = QApplication(sys.argv)
                BeginTDsys = TradeUI('--autostart')
                sys.exit(app.exec())
            else:
                sys.exit()
        else:
            app = QApplication(sys.argv)
            DisCalmier_dialog = DisCalmier_Dialog()
            if DisCalmier_dialog.exec() == 1:
                while True:

                    Login_dialog = Login_Dialog()

                    # 如果用戶是執行登入
                    if Login_dialog.exec() == 1:
                        if Login_dialog.api_key and Login_dialog.secret_key and Login_dialog.LINE:
                            # 判斷到期時間
                            UserDeadline = AppSetting.get_UserDeadline()
                            if UserDeadline.get(GetHashKey(Login_dialog.PhoneNumber), None) is not None:
                                if UserDeadline[GetHashKey(Login_dialog.PhoneNumber)] > str(datetime.date.today()):
                                    BeginTDsys = TradeUI("--human")
                                    sys.exit(app.exec())
                                else:
                                    deadline_dialog = DeadLine_Dialog()
                                    deadline_dialog.exec()
                            else:
                                phone_error_Dialog = Phone_error_Dialog()
                                phone_error_Dialog.exec()
                        else:
                            error_dialog = Error_Dialog()
                            error_dialog.exec()
            else:
                sys.exit()
    except Exception as e:
        debug.print_info()
