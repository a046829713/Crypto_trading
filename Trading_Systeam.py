from DataProvider import DataProvider, DataProvider_online
from Major.Symbol_filter import get_symobl_filter_useful
from Vecbot_backtest import Quantify_systeam_online
import time
from datetime import datetime
import sys


# 下單物件未完成測試
# 實際測試
# GUI閃退問題

class Trading_systeam():
    def __init__(self) -> None:
        self.symbol_map = {}
        self.engine = Quantify_systeam_online()
        # formal正式啟動環境
        self.dataprovider_online = DataProvider_online(formal=True)

    def get_target_symbol(self):
        dataprovider = DataProvider(time_type='D')
        all_symbols = dataprovider.get_symbols_history_data()
        example = get_symobl_filter_useful(all_symbols)
        return example

        # 取得交易標的(頻率不需要太頻繁 一個月一次即可)
        # ['btcdomusdt-f-d', 0.061946189785725636], ['xmrusdt-f-d', 0.055462536626203374], ['btcstusdt-f-d', 0.0]

    def main(self):
        print("開始交易!!!")
        self.engine.Portfolio_online_register()
        symbol_name: list = self.engine.get_symbol_name()

        # 初始化商品槓桿
        for each_symbol in symbol_name:
            Response = self.dataprovider_online.Binanceapp.client.futures_change_leverage(
                symbol=each_symbol, leverage=20)
            print(Response)

        # 先將資料從DB撈取出來
        for name in symbol_name:
            original_df = self.dataprovider_online.get_symboldata(
                name, save=False)
            self.symbol_map.update({name: original_df})

        last_min = None
        print("資料讀取結束")
        # 透過迴圈回補資料
        while True:
            print(datetime.now().minute)
            if datetime.now().minute != last_min or last_min is None:
                # if True:
                # 需要個別去計算每個loop所耗費的時間

                begin_time = time.time()
                # 取得原始資料
                for name, each_df in self.symbol_map.items():
                    original_df = self.dataprovider_online.reload_data_online(
                        each_df, name)
                    self.symbol_map.update({name: original_df})

                info = self.engine.get_symbol_info()
                for strategy_name, symbol_name, freq_time in info:
                    # 取得可交易之資料
                    trade_data = self.dataprovider_online.get_trade_data(
                        self.symbol_map[symbol_name], freq_time)

                    # ! 判斷是否要將trade_data資料減少
                    # 將資料注入
                    self.engine.register_data(strategy_name, trade_data)

                print("開始進入回測")
                # 註冊完資料之後進入回測
                pf = self.engine.Portfolio_online_start()
                print("最後資料表*************************************")
                last_status = pf.get_last_status()
                print('目前交易狀態', last_status)
                print("最後資料表*************************************")

                current_size = self.dataprovider_online.Binanceapp.getfutures_account_positions()
                print("目前binance交易所內的部位狀態:", current_size)

                # >>比對目前binance 內的部位狀態 進行交易
                order_finally = self.dataprovider_online.transformer.calculation_size(
                    last_status, current_size)
                print("差異單", order_finally)
                if order_finally:
                    self.dataprovider_online.Binanceapp.execute_orders(
                        order_finally)

                print("時間差", time.time() - begin_time)
                last_min = datetime.now().minute
            else:
                time.sleep(1)

            if self.dataprovider_online.Binanceapp.trade_count > 10:
                print("緊急狀況處理-交易次數過多")
                sys.exit()


if __name__ == '__main__':
    systeam = Trading_systeam()
    systeam.main()
