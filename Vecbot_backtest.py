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
from AppSetting import AppSetting


class Quantify_systeam(object):
    def __init__(self) -> None:
        """
            設定基礎時間跟基本資訊
        """

        self.setting = AppSetting.get_setting()['Quantify_systeam']['history']
        Attributes_data = self.setting['Attributes']

        # ///////////////////////////////////////////////////
        strategyName1 = "AVAXUSDT-15K-OB"
        strategyAt_Data1 = Attributes_data[strategyName1]

        self.strategy1 = Strategy_base(
            strategyName1, strategyAt_Data1['symbol'], strategyAt_Data1['freq_time'], strategyAt_Data1['size'], strategyAt_Data1['fee'], strategyAt_Data1['slippage'], lookback_date=strategyAt_Data1['lookback_date'])

        # ///////////////////////////////////////////////////
        strategyName2 = "COMPUSDT-15K-OB"
        strategyAt_Data2 = Attributes_data[strategyName2]

        self.strategy2 = Strategy_base(
            strategyName2, strategyAt_Data2['symbol'], strategyAt_Data2['freq_time'], strategyAt_Data2['size'], strategyAt_Data2['fee'], strategyAt_Data2['slippage'], lookback_date=strategyAt_Data2['lookback_date'])

        # ///////////////////////////////////////////////////
        # strategyName3 = "SOLUSDT-15K-OB"
        # strategyAt_Data3 = Attributes_data[strategyName3]

        # self.strategy3 = Strategy_base(
        #     strategyName3, strategyAt_Data3['symbol'], strategyAt_Data3['freq_time'], strategyAt_Data3['size'], strategyAt_Data3['fee'], strategyAt_Data3['slippage'], lookback_date=strategyAt_Data3['lookback_date'])

        # ///////////////////////////////////////////////////
        # strategyName4 = "AAVEUSDT-15K-OB"
        # strategyAt_Data4 = Attributes_data[strategyName4]

        # self.strategy4 = Strategy_base(
        #     strategyName4, strategyAt_Data4['symbol'], strategyAt_Data4['freq_time'], strategyAt_Data4['size'], strategyAt_Data4['fee'], strategyAt_Data4['slippage'], lookback_date=strategyAt_Data4['lookback_date'])

        # ///////////////////////////////////////////////////
        # strategyName5 = "DEFIUSDT-15K-OB"
        # strategyAt_Data5 = Attributes_data[strategyName5]

        # self.strategy5 = Strategy_base(
        #     strategyName5, strategyAt_Data5['symbol'], strategyAt_Data5['freq_time'], strategyAt_Data5['size'], strategyAt_Data5['fee'], strategyAt_Data5['slippage'], lookback_date=strategyAt_Data5['lookback_date'])

        parameter_data = self.setting['parameter']
        self.strategypa1 = parameter_data[strategyName1]
        self.strategypa2 = parameter_data[strategyName2]
        # self.strategypa3 = parameter_data[strategyName3]
        # self.strategypa4 = parameter_data[strategyName4]
        # self.strategypa5 = parameter_data[strategyName5]

    def optimize(self):
        """
            用來計算最佳化的參數
        """
        ordermap = Np_Order_Strategy(self.strategy5)
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
        ordermap = Np_Order_Strategy(self.strategy1)
        ordermap.set_parameter(self.strategypa1)
        pf = ordermap.logic_order()
        Picture_maker(pf)

    def PortfolioBacktesting(self):
        """
            投資組合模擬非正式
        """
        app = PortfolioTrader(Portfolio_initcash=18000)

        app.register(
            self.strategy1, self.strategypa1)
        app.register(
            self.strategy2, self.strategypa2)
        # app.register(
        #     self.strategy3, self.strategypa3)
        # app.register(
        #     self.strategy4, self.strategypa4)
        # app.register(
        #     self.strategy5, self.strategypa5)

        pf = app.logic_order()
        Picture_maker(pf)


class Quantify_systeam_online(object):
    """
        由於很多行為和回測的時候不相同
        所以獨立出來
    """

    def __init__(self) -> None:
        """
            這邊的lookback_date 是指策略最早的接收日期，如果資料讀取沒有這麼多不影響
            DataProvider 的資料提供的優先層級更大
        """
        self.setting = AppSetting.get_setting()['Quantify_systeam']['online']
        Attributes_data = self.setting['Attributes']

        # ///////////////////////////////////////////////////
        strategyName1 = "AVAXUSDT-15K-OB"
        strategyAt_Data1 = Attributes_data[strategyName1]

        self.strategy1 = Strategy_atom(
            strategyName1, strategyAt_Data1['symbol'], strategyAt_Data1['freq_time'], strategyAt_Data1['size'], strategyAt_Data1['fee'], strategyAt_Data1['slippage'], lookback_date=strategyAt_Data1['lookback_date'])

        # ///////////////////////////////////////////////////
        strategyName2 = "COMPUSDT-15K-OB"
        strategyAt_Data2 = Attributes_data[strategyName2]

        self.strategy2 = Strategy_atom(
            strategyName2, strategyAt_Data2['symbol'], strategyAt_Data2['freq_time'], strategyAt_Data2['size'], strategyAt_Data2['fee'], strategyAt_Data2['slippage'], lookback_date=strategyAt_Data2['lookback_date'])

        # ///////////////////////////////////////////////////
        strategyName3 = "SOLUSDT-15K-OB"
        strategyAt_Data3 = Attributes_data[strategyName3]

        self.strategy3 = Strategy_atom(
            strategyName3, strategyAt_Data3['symbol'], strategyAt_Data3['freq_time'], strategyAt_Data3['size'], strategyAt_Data3['fee'], strategyAt_Data3['slippage'], lookback_date=strategyAt_Data3['lookback_date'])

        # ///////////////////////////////////////////////////
        strategyName4 = "AAVEUSDT-15K-OB"
        strategyAt_Data4 = Attributes_data[strategyName4]

        self.strategy4 = Strategy_atom(
            strategyName4, strategyAt_Data4['symbol'], strategyAt_Data4['freq_time'], strategyAt_Data4['size'], strategyAt_Data4['fee'], strategyAt_Data4['slippage'], lookback_date=strategyAt_Data4['lookback_date'])

        # ///////////////////////////////////////////////////
        strategyName5 = "DEFIUSDT-15K-OB"
        strategyAt_Data5 = Attributes_data[strategyName5]

        self.strategy5 = Strategy_atom(
            strategyName5, strategyAt_Data5['symbol'], strategyAt_Data5['freq_time'], strategyAt_Data5['size'], strategyAt_Data5['fee'], strategyAt_Data5['slippage'], lookback_date=strategyAt_Data5['lookback_date'])

        parameter_data = self.setting['parameter']
        self.strategypa1 = parameter_data[strategyName1]
        self.strategypa2 = parameter_data[strategyName2]
        self.strategypa3 = parameter_data[strategyName3]
        self.strategypa4 = parameter_data[strategyName4]
        self.strategypa5 = parameter_data[strategyName5]

        # 創建即時交易模組
        self.Trader = PortfolioOnline(Portfolio_initcash=35000)

    def register_data(self, strategy_name: str, trade_data: pd.DataFrame):
        """
            將每一次更新的資料傳入 個別的策略當中
        """
        for each_strategy in self.Trader.strategys:
            each_strategy: Strategy_atom
            if strategy_name == each_strategy.strategy_name:
                each_strategy.df = trade_data
                each_strategy.data, each_strategy.array_data = each_strategy.simulationdata()
                each_strategy.datetimes = Event_count.get_index(
                    each_strategy.data)

    def Portfolio_online_register(self):
        """
            正式投資組合上線環境
            先將基本資訊註冊
            並放入策略參數
        """

        self.Trader.register(
            self.strategy1, self.strategypa1)
        self.Trader.register(
            self.strategy2, self.strategypa2)
        self.Trader.register(
            self.strategy3, self.strategypa3)
        self.Trader.register(
            self.strategy4, self.strategypa4)
        self.Trader.register(
            self.strategy5, self.strategypa5)

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
