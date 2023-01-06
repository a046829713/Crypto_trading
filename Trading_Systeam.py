from DataProvider import DataProvider, DataProvider_online
from Major.Symbol_filter import get_symobl_filter_useful
from Vecbot_backtest import Quantify_systeam
import time


class Trading_systeam():
    def __init__(self) -> None:
        self.symbol_map = {}
        self.tradedata_map = {}
        self.engine = Quantify_systeam()
        self.dataprovider_online = DataProvider_online()
        self.main()

    def main(self):
        # dataprovider = DataProvider(time_type='D')
        # all_symbols = dataprovider.get_symbols_history_data()
        # example = get_symobl_filter_useful(all_symbols)
        # print(example)

        # 取得交易標的(頻率不需要太頻繁 一個月一次即可)
        # ['btcdomusdt-f-d', 0.061946189785725636], ['xmrusdt-f-d', 0.055462536626203374], ['btcstusdt-f-d', 0.0]

        # 取得回測參數
        # vecbot_backtest
        self.engine.Portfolio_online()
        symbol_name: list = self.engine.get_symbol_name()
        print(symbol_name)

        # 先將資料從DB撈取出來
        for name in symbol_name:
            original_df = self.dataprovider_online.get_symboldata(
                name, save=False)
            self.symbol_map.update({name: original_df})

        # 透過迴圈回補資料
        while True:
            # 取得原始資料
            for name, each_df in self.symbol_map.items():
                original_df = self.dataprovider_online.reload_data_online(
                    each_df, name)
                self.symbol_map.update({name: original_df})

            info = self.engine.get_symbol_info()
            for strategy_name, symbol_name, freq_time in info:
                print(strategy_name, symbol_name, freq_time)
                # 放入原始資料
                self.tradedata_map.update(
                    {strategy_name: self.dataprovider_online.get_trade_data(self.symbol_map[symbol_name], freq_time)})

            print(self.tradedata_map)
            time.sleep(30)# >> 想要將停止時間的方式 改成定點抓取>>

            # taketradedata
            # orderout = app.asin(taketradedata)
            # 取得投資組合
            # 進行交易
            # online output
            # trader_send_oout(orderout)


if __name__ == '__main__':
    systeam = Trading_systeam()
