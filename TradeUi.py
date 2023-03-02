from PyQt6.QtWidgets import QWidget, QApplication
import sys
from MainW import Ui_Form
from PyQt6.QtCore import pyqtSignal
from Trading_Systeam import GUI_Trading_systeam
from PyQt6.QtCore import QThread
from DataProvider import DataProvider
import pandas as pd


class TradeUI(QWidget, Ui_Form):
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
        """ 保存資料並關閉程序 注意不能使用replace 資料長短問題"""

        def mergefunc():
            for name, each_df in self.systeam.new_symbol_map.items():
                print(name)
                print(each_df)

                # 不保存頭尾
                each_df.drop(
                    [each_df.index[0], each_df.index[-1]], inplace=True)
                if len(each_df) != 0:
                    # 準備寫入資料庫裡面
                    print('保存資料')
                    self.systeam.dataprovider_online.save_data(
                        symbol_name=name, original_df=each_df, exists="append")
            sys.exit()

        self.save_data_Thread = QThread()
        self.save_data_Thread.run = mergefunc
        self.save_data_Thread.start()


app = QApplication(sys.argv)
BeginTDsys = TradeUI()
sys.exit(app.exec())
