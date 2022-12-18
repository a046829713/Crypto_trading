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

        # 取得交易標的
        
        
        
        
        
        
        
        
        
        # 取得回測參數
        
        
        
        
        
        
        # 取得投資組合
        
        
        
        
        
        
        # 進行交易



if __name__ == '__main__':
    systeam = Trading_systeam()