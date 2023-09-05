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
from utils.TimeCountMsg import TimeCountMsg
import json
from Datatransformer import Datatransformer


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
        elif self.strategy.strategytype == 'VCPStrategy':
            inputs_parameter = {"highest_n1": np.arange(50, 800, 50, dtype=np.int16),
                                "lowest_n2": np.arange(50, 800, 50, dtype=np.int16),
                                'std_n3': np.arange(50, 200, 10, dtype=np.int16),
                                'volume_n3': np.arange(50, 200, 10, dtype=np.int16)}
        elif self.strategy.strategytype == 'DynamicStrategy':
            inputs_parameter = {'ATR_short1': np.arange(10, 1000, 10, dtype=np.float_),
                                'ATR_long2': np.arange(10, 1000, 10, dtype=np.float_)}
        elif self.strategy.strategytype == 'DynamicVCPStrategy':
            inputs_parameter = {'std_n3': np.arange(10, 1000, 10, dtype=np.int16),
                                'volume_n3': np.arange(10, 1000, 10, dtype=np.int16)}

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

            print([each_parameter, UI])
            out_list.append([each_parameter, UI])

        UI_list = [i[1] for i in out_list]

        self.result.update({"updatetime": str(datetime.now()).split()[0]})

        # 當完全沒有參數可以決定的時候
        if UI_list:
            max_data = max(UI_list)
            print(max_data)
            for i in out_list:
                if i[1] == max_data:
                    self.result.update({"All_args": json.dumps(
                        Datatransformer().trans_int16(i[0]))})
        else:
            if self.strategy.strategytype == 'TurtleStrategy':
                self.result.update(
                    {"All_args": json.dumps({'highest_n1': 610, 'lowest_n2': 350, 'ATR_short1': 130.0, 'ATR_long2': 50.0})})
            elif self.strategy.strategytype == 'VCPStrategy':
                self.result.update(
                    {"All_args": json.dumps({'highest_n1': 300, 'lowest_n2': 600, 'std_n3': 50, 'volume_n3': 150})})
            elif self.strategy.strategytype == 'DynamicStrategy':
                self.result.update(
                    {"All_args": json.dumps({"ATR_short1": 300.0, "ATR_long2": 600.0})})
            elif self.strategy.strategytype == 'DynamicVCPStrategy':
                self.result.update(
                    {"All_args": json.dumps({'std_n3': 50, 'volume_n3': 150})})
        return self.result


class Quantify_systeam(object):
    def __init__(self) -> None:
        pass

    def Backtesting(self):
        """
            普通回測模式
        """
        ordermap = Np_Order_Strategy(Strategy_base(
            'ETHUSDT-15K-OB-VCP', 'VCPStrategy', 'ETHUSDT', 15,  1.0,  0.002, 0.0025))

        ordermap.set_parameter(
            {'std_n3': 10, 'volume_n3': 90}
        )

        pf = ordermap.logic_order()
        Picture_maker(pf)

    def Portfolio_online_register(self, target_symobl: list, argsdf: pd.DataFrame):
        """
            和正式略有不同(但是想查看模擬投資組合)
            example :
                target_symobl
                    ['XMRUSDT', 'BTCUSDT', 'BTCDOMUSDT', 'BNBUSDT', 'ETHUSDT']
        """
        argsdf.set_index('strategyName', inplace=True)
        argsData = argsdf.to_dict('index')

        for each_symbol in target_symobl:
            print(each_symbol)
            # 這邊用來決定要運行甚麼策略
            for _strategy in ['DynamicStrategy','VCPStrategy']:
                print("測試策略",_strategy)
                if _strategy == 'TurtleStrategy':
                    strategyName = f"{each_symbol}-15K-OB"
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_base(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = json.loads(eachargdata['All_args'])

                elif _strategy == 'VCPStrategy':
                    strategyName = f"{each_symbol}-15K-OB-VCP"
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_base(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = json.loads(eachargdata['All_args'])
                elif _strategy == 'DynamicStrategy':
                    strategyName = f"{each_symbol}-15K-OB-DY"
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_base(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = json.loads(eachargdata['All_args'])
                elif _strategy == 'DynamicVCPStrategy':
                    strategyName = f"{each_symbol}-15K-OB-DYVCP" # 
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_base(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = json.loads(eachargdata['All_args'])

                
                self.Trader.register(
                    strategy, strategypa)

    def PortfolioBacktesting(self):
        """
            投資組合模擬非正式
        """
        # self.Trader = PortfolioTrader(Portfolio_initcash=25000)
        # 用來查看正式的交易環境及狀況
        print("開始模擬交易")
        self.Trader = PortfolioOnline(Portfolio_initcash=25000)

        # ['LTCUSDT', 'KSMUSDT', 'MKRUSDT', 'BTCUSDT', 'BTCDOMUSDT', 'COMPUSDT', 'XMRUSDT', 'YFIUSDT', 'AAVEUSDT', 'ETHUSDT', 'BCHUSDT']
        self.Portfolio_online_register(
            ['LTCUSDT', 'KSMUSDT', 'MKRUSDT', 'BTCUSDT', 'BTCDOMUSDT', 'COMPUSDT', 'XMRUSDT', 'YFIUSDT', 'AAVEUSDT', 'ETHUSDT', 'BCHUSDT'], pd.read_csv("optimizeresult.csv"))
        pf = self.Trader.logic_order()
        Picture_maker(pf)


class Quantify_systeam_online(object):
    """
        由於很多行為和回測的時候不相同
        所以獨立出來
    """

    def __init__(self, initcash: int) -> None:
        """
            這邊的lookback_date 是指策略最早的接收日期，如果資料讀取沒有這麼多不影響
            DataProvider 的資料提供的優先層級更大
        """
        # 創建即時交易模組
        self.Trader = PortfolioOnline(Portfolio_initcash=initcash)
        self.CloseProfit = []

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
            # 這邊用來決定要運行甚麼策略
            for _strategy in ["VCPStrategy", 'TurtleStrategy']:
                if _strategy == 'TurtleStrategy':
                    strategyName = f"{each_symbol}-15K-OB"
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_atom(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = json.loads(eachargdata['All_args'])

                elif _strategy == 'VCPStrategy':
                    strategyName = f"{each_symbol}-15K-OB-VCP"
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_atom(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = json.loads(eachargdata['All_args'])
                
                elif _strategy == 'DynamicStrategy':
                    strategyName = f"{each_symbol}-15K-OB-DY"
                    eachargdata = argsData[strategyName]
                    strategy = Strategy_atom(
                        strategyName, eachargdata['Strategytype'], eachargdata['symbol'], eachargdata['freq_time'], eachargdata['size'], eachargdata['fee'], eachargdata['slippage'])
                    strategypa = json.loads(eachargdata['All_args'])

                self.Trader.register(
                    strategy, strategypa)

    @TimeCountMsg.record_timemsg
    def Portfolio_online_start(self):
        print("回測已經進入")
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
    systeam.PortfolioBacktesting()
