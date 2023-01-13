""" all data and transformer active """
import Data
from Database import SQL_operate
import pandas as pd
from Datatransformer import Datatransformer
from typing import Optional
from utils.Debug_tool import debug


class DataProvider:
    """
        用來整合 binance 的 API
        MYSQL
        和資料轉換
    """

    def __init__(self, time_type: Optional[str] = None, formal=False):
        self.app = Data.custom.Binance_server(formal)
        self.SQL = SQL_operate.DB_operate()
        self.transformer = Datatransformer()
        self.time_type = time_type

    def reload_data(self, symbol_name='BTCUSDT', iflower=True):
        # 先檢查是否有相關資料 取得目前所有列
        symbol_name_list = self.SQL.get_db_data('show tables;')
        symbol_name_list = [y[0] for y in symbol_name_list]

        if self.time_type == 'D':
            tb_symbol_name = symbol_name + '-F-D'
        else:
            tb_symbol_name = symbol_name + '-F'

        if iflower:
            tb_symbol_name = tb_symbol_name.lower()

        if tb_symbol_name in symbol_name_list:
            print(f'{tb_symbol_name}-已經有存在的資料')
            # 當實時交易的時候減少 讀取數量
            if self.__class__.__name__ == 'DataProvider_online':
                df = self.SQL.read_Dateframe(f'SELECT * FROM `{tb_symbol_name}` where Datetime > "2022-09-26"')
            else:
                df = self.SQL.read_Dateframe(tb_symbol_name)
            
            
            df['Datetime'] = df['Datetime'].astype(str)
        else:
            print('創建資料')
            self.SQL.change_db_data(
                f"""
                CREATE TABLE `crypto_data`.`{tb_symbol_name}`(
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

        if self.time_type == 'D':
            catch_time = '1d'
        else:
            catch_time = '1m'

        # 這邊的資料為原始的UTC資料 無任何加工
        original_df = Data.custom.BinanceDate.download(
            df, f"{symbol_name}", catch_time)

        return original_df

    def get_symboldata(self, symbol_name='BTCUSDT', freq: int = 15, save=True):
        """
            取得回補完整且已經轉換過指定時間區段台灣時區之資料
        """
        original_df = self.reload_data(symbol_name)
        if save:
            self.save_data(symbol_name, original_df)

        new_df = self.transformer.get_tradedata(original_df, freq=freq)
        return new_df

    def save_data(self, symbol_name, original_df, iflower=True):
        """
            保存資料到SQL
        """
        if self.time_type == 'D':
            tb_symbol_name = symbol_name + '-F-D'
        else:
            tb_symbol_name = symbol_name + '-F'

        if iflower:
            tb_symbol_name = tb_symbol_name.lower()

        self.SQL.write_Dateframe(original_df, tb_symbol_name)
        print(f"{tb_symbol_name}寫入完成")

    def reload_all_data(self):
        """
            用來回補所有symbol的歷史資料

        """
        for symbol_name in self.app.get_targetsymobls():
            original_df = self.reload_data(symbol_name)
            self.save_data(symbol_name, original_df)

    def get_symbols_history_data(self, iflower=True) -> list:
        """
            讀取所有日線資料 用來分析和排序

        Returns:
            list: 
                [[tb_symbol_name,each_df],
                 [tb_symbol_name,each_df],
                 ....
                ]
        """

        out_list = []
        for symbol_name in self.app.get_targetsymobls():
            if self.time_type == 'D':
                tb_symbol_name = symbol_name + '-F-D'
            else:
                tb_symbol_name = symbol_name + '-F'
            if iflower:
                tb_symbol_name = tb_symbol_name.lower()
            each_df = self.SQL.read_Dateframe(tb_symbol_name)
            out_list.append([tb_symbol_name, each_df])

        return out_list


class DataProvider_online(DataProvider):
    def get_symboldata(self, symbol_name='BTCUSDT', save=True):
        """
            回補原始資料 並且保存
        """
        original_df = self.reload_data(symbol_name)
        if save:
            self.save_data(symbol_name, original_df)

        return original_df

    def reload_data_online(self, df: pd.DataFrame, symbol_name):
        if self.time_type == 'D':
            catch_time = '1d'
        else:
            catch_time = '1m'

        df.reset_index(inplace=True)
        df['Datetime'] = df['Datetime'].astype(str)

        # 這邊的資料為原始的UTC資料 無任何加工
        original_df = Data.custom.BinanceDate.download(
            df, f"{symbol_name}", catch_time)

        return original_df

    def get_trade_data(self, original_df, freq):
        new_df = self.transformer.get_tradedata(original_df, freq=freq)
        return new_df


if __name__ == "__main__":
    # dataprovider = DataProvider(time_type='D')
    dataprovider = DataProvider_online()
    print(dataprovider.get_symboldata("ETHUSDT", save =True))
    # dataprovider.reload_all_data()
