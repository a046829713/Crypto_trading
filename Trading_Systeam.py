from DataProvider import DataProvider, DataProvider_online
from Major.Symbol_filter import get_symobl_filter_useful
from Vecbot_backtest import Quantify_systeam


class Trading_systeam():
    def __init__(self) -> None:
        self.symbol_map = {}
        self.engine = Quantify_systeam()
        self.dataprovider_online = DataProvider_online()
        self.main()

    def main(self):
        # dataprovider = DataProvider(time_type='D')
        # all_symbols = dataprovider.get_symbols_history_data()
        # example = get_symobl_filter_useful(all_symbols)
        # print(example)

        # 取得交易標的(頻率不需要太頻繁 一個月一次即可)
        
        # 取得回測參數
        # vecbot_backtest
        
        # 交易之前應該要先
        # 全部回補完成之後再進入迴圈
        
        
        self.engine.Portfolio_online()
        print("取得交易標的資料")
        symbol_name: list = self.engine.get_symbol_name()
        print(symbol_name)
        for name in symbol_name:            
            original_df = self.dataprovider_online.get_symboldata(name,save=False)
            self.symbol_map.update({symbol_name: original_df})

        info = self.engine.get_symbol_info()
        for strategy_name, symbol_name, freq_time in info:
            # taketradedata 
            # orderout = app.asin(taketradedata)
            # 取得投資組合
            # 進行交易
            # online output
            # trader_send_oout(orderout)
        




if __name__ == '__main__':
    systeam = Trading_systeam()
