""" all data and transformer active """
import Data
from Database import SQL_operate
import pandas as pd
from Datatransformer import Datatransformer


class DataProvider:
    def __init__(self):
        self.app = Data.custom.Binance_server()
        self.SQL = SQL_operate.DB_operate()
        self.transformer = Datatransformer()

    def reload_all_data(self):
        for symbol_name in self.app.get_targetsymobls():
            self.reload_data(symbol_name)

    def reload_data(self, symbol_name='BTCUSDT'):
        # 先檢查是否有相關資料 取得目前所有列
        symbol_list = self.SQL.get_db_data('show tables;')
        symbol_list = [y[0] for y in symbol_list]

        if symbol_name + '-F' in symbol_list:
            print(f'{symbol_name}-已經有存在的資料')
            df = self.SQL.read_Dateframe(f"{symbol_name}-F")
            df['Datetime'] = df['Datetime'].astype(str)
        else:
            print('創建資料')
            self.SQL.change_db_data(
                f"""
                CREATE TABLE `crypto_data`.`{symbol_name}-F`(
                `Datetime` DATETIME NOT NULL,
                `Open` FLOAT NOT NULL,
                `High` FLOAT NOT NULL,
                `Low` FLOAT NOT NULL,
                `Close` FLOAT NOT NULL,
                `Volume` FLOAT NOT NULL,
                `close_time` FLOAT NOT NULL,
                `quote_av` FLOAT NOT NULL,
                `trades` FLOAT NOT NULL,
                `tb_base_av` FLOAT NOT NULL,
                `tb_quote_av` FLOAT NOT NULL,
                `ignore` FLOAT NOT NULL,
                PRIMARY KEY(`Datetime`)
                );"""
            )

            df = pd.DataFrame()

        # 這邊的資料為原始的UTC資料 無任何加工
        original_df = Data.custom.BinanceDate.download(
            df, f"{symbol_name}", '1m')
        return original_df

    def get_symboldata(self, symbol_name='BTCUSDT', freq: int = 15, save=True):
        """
            取得回補完整且已經轉換過指定時間區段台灣時區之資料
        """
        original_df = self.reload_data(symbol_name)
        if save:
            self.save_data(symbol_name,original_df)            
            
        new_df =  self.transformer.get_tradedata(original_df, freq=freq)
        print('產生實驗資料 DataProvider - get_symboldata')
        new_df.to_csv(f"{symbol_name}-F-{freq}-Min.csv")
        return new_df

    def save_data(self, symbol_name, original_df):
        # ====================================================================
        # 保存舊的資料
        self.SQL.write_Dateframe(original_df, f"{symbol_name}-F")
        print(f"{symbol_name}-F寫入完成")
        


if __name__ == "__main__":
    dataprovider = DataProvider()
    print(dataprovider.get_symboldata("BTCUSDT", 15))