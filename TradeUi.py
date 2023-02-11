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
            for name, each_df in self.systeam.symbol_map.items():
                print('目前商品', name)
                each_df.reset_index(inplace=True)

                print(
                    '**********************************原始資料*****************************')
                print(each_df.dtypes)
                print(each_df)
                print(
                    '**********************************原始資料*****************************')

                # 先將資料從DB撈取出來
                tb_symbol_name = name + '-F'
                tb_symbol_name = tb_symbol_name.lower()
                db_df = self.systeam.dataprovider_online.SQL.read_Dateframe(
                    tb_symbol_name)

                db_df['Datetime'] = pd.to_datetime(db_df['Datetime'])
                db_df.set_index('Datetime', inplace=True)
                db_df = db_df.astype(float)
                db_df.reset_index(inplace=True)

                print(
                    "*****************************資料庫資料******************************************")
                print(db_df.dtypes)
                print(db_df)
                print(
                    "*****************************資料庫資料******************************************")
                merge_df = pd.concat([db_df, each_df], ignore_index=True)
                print(
                    "*****************************合併資料前******************************************")
                print(merge_df)

                print(
                    "*****************************合併資料前******************************************")
                if 'index' in merge_df.columns:
                    print('刪除')
                    merge_df.drop(columns=['index'], inplace=True)

                # duplicated >> 重複 True 代表重複了
                merge_df.set_index('Datetime', inplace=True)
                merge_df = merge_df[~merge_df.index.duplicated(keep='last')]
                print(
                    "*****************************合併資料******************************************")
                print(merge_df)
                print(
                    "*****************************合併資料******************************************")

                print(
                    '********************************商品資料回補完成!*************************************')
                self.systeam.dataprovider_online.save_data(
                    symbol_name=name, original_df=merge_df)

            sys.exit()

        def newmerg():
            for name, each_df in self.systeam.new_symbol_map.items():
                print(name)
                print(each_df)

                # 不保存頭尾
                each_df.drop([each_df.index[0],each_df.index[-1]], inplace=True)
                if len(each_df) != 0:
                    # 準備寫入資料庫裡面
                    print('保存資料')
                    self.systeam.dataprovider_online.save_data(symbol_name=name, original_df=each_df,exists="append")
            sys.exit()
            
        self.save_data_Thread = QThread()
        self.save_data_Thread.run = newmerg
        self.save_data_Thread.start()


app = QApplication(sys.argv)
BeginTDsys = TradeUI()
sys.exit(app.exec())
