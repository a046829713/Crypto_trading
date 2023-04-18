from Base.Strategy_base import Strategy_base
from Base.Strategy_base import Np_Order_Strategy
from Base.Strategy_base import PortfolioTrader
from Base.Strategy_base import PortfolioOnline
from Base.Strategy_base import Strategy_atom
from Hyper_optimiza import Hyper_optimization
from Plot_draw.Picture_Mode import Picture_maker
import numpy as np
import pandas as pd
from Count.Base import Event_count
from AppSetting import AppSetting
import copy
from datetime import datetime
import time


class Optimizer(object):
    def __init__(self, strategyName: str, symbol: str, optimize_strategy_type: str) -> None:
        """

        Args:
            optimize_strategy_type (str): TurtleStrategy,VCPStrategy
            symbol (str): _description_
            strategyName (str): _description_
        """
        self.symbol = symbol
        self.setting = AppSetting.get_setting(
        )['Quantify_systeam']['sharemode']['Attributes']['SHARE-15K-OB']

        self.strategy = Strategy_base(strategyName, optimize_strategy_type, symbol, self.setting['freq_time'],
                                      self.setting['size'], self.setting['fee'], self.setting['slippage'])

        self.result = copy.deepcopy(self.setting)

        self.result.update(
            {'symbol': self.symbol, "Strategytype": optimize_strategy_type, "strategyName": strategyName})

    def optimize(self):
        """
            用來計算最佳化的參數
        """
        ordermap = Np_Order_Strategy(self.strategy)
        if self.strategy.strategytype == 'TurtleStrategy':
            inputs_parameter = {"highest_n1": np.arange(50, 800, 20, dtype=np.int16),
                                "lowest_n2": np.arange(50, 800, 20, dtype=np.int16),
                                'ATR_short1': np.arange(10, 200, 10, dtype=np.float_),
                                'ATR_long2': np.arange(10, 200, 10, dtype=np.float_)}
        else:
            inputs_parameter = {"highest_n1": np.arange(50, 800, 50, dtype=np.int16),
                                "lowest_n2": np.arange(50, 800, 50, dtype=np.int16),
                                'std_n3': np.arange(50, 200, 10, dtype=np.int16),
                                'volume_n3': np.arange(50, 200, 10, dtype=np.int16)}

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

        UI_list = [i[1] for i in out_list]

        # 當完全沒有參數可以決定的時候
        if UI_list:
            max_data = max(UI_list)

            for i in out_list:
                if i[1] == max_data:
                    print(i)
                    self.result.update(i[0])
        else:
            if self.strategy.strategytype == 'TurtleStrategy':
                self.result.update(
                    {'highest_n1': 610, 'lowest_n2': 350, 'ATR_short1': 130.0, 'ATR_long2': 50.0})
            else:
                self.result.update(
                    {'highest_n1': 300, 'lowest_n2': 600, 'std_n3': 50, 'volume_n3': 150})

        self.result.update({"updatetime": str(datetime.now()).split()[0]})
        return self.result


class Quantify_systeam(object):
    def __init__(self) -> None:
        """
            設定基礎時間跟基本資訊
        """

        # self.setting = AppSetting.get_setting()['Quantify_systeam']['history']
        # Attributes_data = self.setting['Attributes']

        self.strategy1 = Strategy_base(
            'BTCUSDT-15K-OB', 'VCPStrategy', 'BTCUSDT', 15,  1.0,  0.002, 0.0025)

        # ///////////////////////////////////////////////////
        # strategyName2 = "COMPUSDT-15K-OB"
        # strategyAt_Data2 = Attributes_data[strategyName2]

        # self.strategy2 = Strategy_base(
        #     strategyName2, strategyAt_Data2['symbol'], strategyAt_Data2['freq_time'], strategyAt_Data2['size'], strategyAt_Data2['fee'], strategyAt_Data2['slippage'], lookback_date=strategyAt_Data2['lookback_date'])

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

        # parameter_data = self.setting['parameter']
        # self.strategypa1 = parameter_data[strategyName1]
        # self.strategypa2 = parameter_data[strategyName2]
        # self.strategypa3 = parameter_data[strategyName3]
        # self.strategypa4 = parameter_data[strategyName4]
        # self.strategypa5 = parameter_data[strategyName5]

    def Backtesting(self):
        """
            普通回測模式
        """
        ordermap = Np_Order_Strategy(Strategy_base(
            'BTCUSDT-15K-OB', 'VCPStrategy', 'BTCUSDT', 15,  1.0,  0.002, 0.0025, lookback_date='2020-01-01'))
        # ordermap.set_parameter(self.strategypa1)
        ordermap.set_parameter(
            {'highest_n1': 300, 'lowest_n2': 600, 'std_n3': 50, 'volume_n3': 150}
        )

        pf = ordermap.logic_order()
        Picture_maker(pf)

    def PortfolioBacktesting(self):
        """
            投資組合模擬非正式
        """
        app = PortfolioTrader(Portfolio_initcash=15757)

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
        # 創建即時交易模組
        self.Trader = PortfolioOnline(Portfolio_initcash=21771)

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

    def Portfolio_online_register(self, target_symobl: list, argsdf: pd.DataFrame):
        """
            正式投資組合上線環境
            先將基本資訊註冊
            並放入策略參數
            example :
                target_symobl
                    ['XMRUSDT', 'BTCUSDT', 'BTCDOMUSDT', 'BNBUSDT', 'ETHUSDT']
        """
        argsdf.set_index('strategyName', inplace=True)
        argsData = argsdf.to_dict('index')

        for each_symbol in target_symobl:
            for _strategy in ["TurtleStrategy","VCPStrategy"]:
                if _strategy == 'TurtleStrategy':
                    strategyName = f"{each_symbol}-15K-OB"
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_atom(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = {"highest_n1": eachargdata['highest_n1'], "lowest_n2": eachargdata['lowest_n2'],
                                "ATR_short1": eachargdata['ATR_short1'], "ATR_long2": eachargdata['ATR_long2']}

                else:
                    strategyName = f"{each_symbol}-15K-OB-VCP"
                    eachargdata = argsData[strategyName]                    
                    strategy = Strategy_atom(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = {"highest_n1": eachargdata['highest_n1'], "lowest_n2": eachargdata['lowest_n2'],
                                "std_n3": int(eachargdata['std_n3']), "volume_n3": int(eachargdata['volume_n3'])}
                self.Trader.register(
                    strategy, strategypa)

    def Portfolio_online_start(self):
        pf = self.Trader.logic_order()
        return pf

    def get_symbol_name(self) -> set:
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
    systeam.optimize()
