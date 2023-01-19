from Base.Strategy_base import Strategy_base
from Base.Strategy_base import Np_Order_Strategy
from Base.Strategy_base import PortfolioTrader
from Base.Strategy_base import ALL_order_INFO
from Base.Strategy_base import PortfolioOnline
from Base.Strategy_base import Strategy_atom
from tqdm import tqdm
from Hyper_optimiza import Hyper_optimization
from Plot_draw.Picture_Mode import Picture_maker
import numpy as np
from utils import Debug_tool
import pandas as pd
from Count.Base import Event_count

class Quantify_systeam(object):
    def __init__(self) -> None:
        self.strategy1 = Strategy_base(
            "BTCUSDT-15K-OB", "BTCUSDT", 15, 1.0, 0.002, 0.0025, lookback_date='2021-01-01')

        self.strategy2 = Strategy_base(
            "ETHUSDT-15K-OB", "ETHUSDT", 15, 1.0, 0.002, 0.0025, lookback_date='2021-01-01')

        self.strategy3 = Strategy_base(
            "BTCUSDT-2K-OB", "BTCUSDT", 2, 1.0, 0.002, 0.0025, lookback_date='2021-01-01')

    def optimize(self):
        """
            用來計算最佳化的參數
        """
        ordermap = Np_Order_Strategy(self.strategy2)
        inputs_parameter = {"highest_n1": np.arange(50, 800, 20, dtype=np.int16),
                            "lowest_n2": np.arange(50, 800, 20, dtype=np.int16),
                            'ATR_short1': np.arange(10, 200, 10, dtype=np.float_),
                            'ATR_long2': np.arange(10, 200, 10, dtype=np.float_)}
        all_parameter = Hyper_optimization.generator_parameter(
            inputs_parameter)
        all_length = len(all_parameter)
        out_list = []
        num = 0
        all_i = 0
        for each_parameter in all_parameter:
            num += 1
            if num > 500 * all_i:
                all_i += 1
                print(f"總數量{all_length},目前完成進度: {(num / all_length) * 100} %")
            ordermap.set_parameter(each_parameter)
            UI = ordermap.more_fast_logic_order()

            if UI == 0:
                continue
            if UI < 0:
                continue
            out_list.append([each_parameter, UI])

        print(out_list)
        UI_list = [i[1] for i in out_list]
        max_data = max(UI_list)

        for i in out_list:
            if i[1] == max_data:
                print(i)

    def Backtesting(self):
        """
            普通回測模式
        """
        ordermap = Np_Order_Strategy(self.strategy2)
        ordermap.set_parameter(
            {'highest_n1': 490, 'lowest_n2': 370, 'ATR_short1': 90.0, 'ATR_long2': 170.0})
        pf = ordermap.logic_order()
        Picture_maker(pf)

    def PortfolioBacktesting(self):
        """
            投資組合模擬非正式
        """
        app = PortfolioTrader()
        app.register(
            self.strategy1, {'highest_n1': 570, 'lowest_n2': 370, 'ATR_short1': 100.0, 'ATR_long2': 190.0})
        app.register(
            self.strategy2, {'highest_n1': 570, 'lowest_n2': 470, 'ATR_short1': 50.0, 'ATR_long2': 160.0})

        pf = app.logic_order()
        Picture_maker(pf)


class Quantify_systeam_online(object):
    """
        由於很多行為和回測的時候不相同
        所以獨立出來
    """

    def __init__(self) -> None:
        self.strategy1 = Strategy_atom(
            "BTCUSDT-15K-OB", "BTCUSDT", 15, 1.0, 0.002, 0.0025, lookback_date='2021-01-01')

        self.strategy2 = Strategy_atom(
            "ETHUSDT-15K-OB", "ETHUSDT", 15, 1.0, 0.002, 0.0025, lookback_date='2021-01-01')

        self.strategy3 = Strategy_atom(
            "BTCUSDT-2K-OB", "BTCUSDT", 2, 1.0, 0.002, 0.0025, lookback_date='2021-01-01')

        # 創建即時交易模組
        self.Trader = PortfolioOnline()

    def register_data(self, strategy_name: str, trade_data: pd.DataFrame):
        """
            將每一次更新的資料傳入 個別的策略當中
        """
        for each_strategy in self.Trader.strategys:
            each_strategy:Strategy_atom
            if strategy_name == each_strategy.strategy_name:
                each_strategy.df = trade_data
                each_strategy.data, each_strategy.array_data = each_strategy.simulationdata()
                each_strategy.datetimes = Event_count.get_index(each_strategy.data)

    def Portfolio_online_register(self):
        """
            正式投資組合上線環境
            先將基本資訊註冊
        """

        self.Trader.register(
            self.strategy1, {'highest_n1': 570, 'lowest_n2': 370, 'ATR_short1': 100.0, 'ATR_long2': 190.0})

        self.Trader.register(
            self.strategy2, {'highest_n1': 570, 'lowest_n2': 470, 'ATR_short1': 50.0, 'ATR_long2': 160.0})

    def Portfolio_online_start(self):
        pf = self.Trader.logic_order()
        return pf
    
    def get_symbol_name(self) -> list:
        """
            to output symobol name
            to provider Dataprovider
        Returns:
            list: _description_
        """

        return set([each_strategy.symbol_name for each_strategy in self.Trader.strategys])

    def get_symbol_info(self) -> list:
        """
        Returns:
            list: [tuple,tuple]
        """

        return [(each_strategy.strategy_name, each_strategy.symbol_name, each_strategy.freq_time) for each_strategy in self.Trader.strategys]


if __name__ == "__main__":
    systeam = Quantify_systeam()
    systeam.PortfolioBacktesting()
