from DataProvider import DataProvider
from Major.Symbol_filter import get_symobl_filter_useful
class Trading_systeam():
    def __init__(self) -> None:
        self.main()
        
        
    def main(self):
        dataprovider = DataProvider(time_type='D')
        all_symbols = dataprovider.get_symbols_history_data()
        example = get_symobl_filter_useful(all_symbols)
        print(example)

        # 取得交易標的(頻率不需要太頻繁 一個月一次即可)
        
        
        
        
        
        # 取得交易標的資料
        
        
        
        
        # 取得回測參數
        # vecbot_backtest
        
        
        
        
        
        # 取得投資組合
        # vecbot_backtest.PortfolioBacktesting
        
        
        
        
        
        # 進行交易
        # online output


if __name__ == '__main__':
    systeam = Trading_systeam()