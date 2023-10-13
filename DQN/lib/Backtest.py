from AppSetting import AppSetting
import time
import numpy as np
from Plot_draw.Picture_Mode import Picture_maker
from Count import nb
from Base.Strategy_base import Np_Order_Info
from Base.Strategy_base import Strategy_base
import pandas as pd
from .common import Strategy_base_DQN


# 10/9 (並且再次懷疑在驗算的時候, 原本的系統沒有考慮到最後一根K棒還沒有完成這個問題,但印象中以前已經處理)


class Backtest(object):
    def __init__(self, Symbol_data, bars_count: int) -> None:
        assert isinstance(bars_count, int), "bars_count typr must be interger"

        self.Symbol_data = Symbol_data
        self.bars_count = bars_count

    def order_becktest(self, order: list):
        """ 

        order (list):
            類神經網絡所產生的訂單

        {'shiftorder': array([0, 0, 0, ..., 0, 0, 0], dtype=int64),
                'open_array': array([ 146.  ,  146.  ,  146.  , ..., 1631.48, 1627.78, 1628.54]),
                'Length': 135450,
                'init_cash': 10000.0,
                'slippage': 0.0025,
                'size': 1.0,
                'fee': 0.002}
        """
        # 從類神經網絡拿order的一個狀態
        self.shiftorder = np.array(order)
        self.shiftorder = np.roll(self.shiftorder, 1)
        self.shiftorder[0] = 0  # 一率將其歸零即可

        datetime_list = self.Symbol_data['Datetime'].to_list()
        # # 前面10個當樣本
        datetime_list = datetime_list[self.bars_count:]

        # # 最後一個不計算
        datetime_list = datetime_list[:-1]

        # open 平倉版本
        self.Open = self.Symbol_data['Open'].to_numpy()

        # # 前面10個當樣本
        self.Open = self.Open[self.bars_count:]

        # # 最後一個不計算
        self.Open = self.Open[:-1]

        params = {'shiftorder': self.shiftorder,
                  'open_array': self.Open,
                  'Length': len(self.Open),
                  'init_cash': 10000.0,
                  'slippage': setting['DEFAULT_SLIPPAGE'],
                  'size': 1.0,
                  'fee': setting['DEFAULT_COMMISSION_PERC']}

        orders, marketpostion_array, entryprice_array, buy_Fees_array, sell_Fees_array, OpenPostionprofit_array, ClosedPostionprofit_array, profit_array, Gross_profit_array, Gross_loss_array, all_Fees_array, netprofit_array = nb.logic_order(
            **params
        )

        Order_Info = Np_Order_Info(datetime_list,
                                   orders,
                                   marketpostion_array,
                                   entryprice_array,
                                   buy_Fees_array,
                                   sell_Fees_array,
                                   OpenPostionprofit_array,
                                   ClosedPostionprofit_array,
                                   profit_array,
                                   Gross_profit_array,
                                   Gross_loss_array,
                                   all_Fees_array,
                                   netprofit_array)

        Order_Info.register(Strategy_base(
            'ETHUSDT-15K-OB-DQN', 'DQNStrategy', 'NOUSEUSDT', 15,  1.0,  0.002, 0.0025, use_data=False))

        Picture_maker(Order_Info)


class PortfolioTrader_DQN(object):
    """
        應該還是會有兩種狀況
        (回測 和 即時交易)

    Args:
        PortfolioTrader (_type_): _description_
    """

    def __init__(self, Portfolio_initcash: int) -> None:
        self.strategys = []
        self.strategys_maps = {}
        self.Portfolio_initcash = Portfolio_initcash  # 投資組合起始資金
        self.setting = AppSetting.get_DQN_setting()  # 取得類神經網絡的相關配置
        
    def register(self, strategy_info: Strategy_base_DQN):
        """
            將所有的商品資訊 合併做總回測

        Args:
            strategy_info (Strategy_atom): 策略基本資料

        """
        self.strategys.append(strategy_info)

        self.strategys_maps.update(
            {strategy_info.strategy_name: strategy_info})

    def time_min_scale(self):
        """
            用來取得最密集的時間序列
        """
        all_datetimes = []
        for strategy in self.strategys:
            all_datetimes.extend(strategy.get_datetimes())

        self.min_scale = list(set(all_datetimes))
        self.min_scale.sort()
        
    def add_data(self):
        """
            將訂單的買賣方向匯入
        """
        for strategy in self.strategys:
            # 在取得之前必須要完全配置好
            pf = ordermap.logic_order()

            out_list = []
            for datetime_ in strategy.df.index:
                if datetime_ in pf.order.index:
                    out_list.append(pf.order['Order'][datetime_])
                else:
                    out_list.append(0)
            strategy.df = strategy.df.copy()
            strategy.df['Order'] = out_list

            # 添加想要分析的參數
            strategy.df['avgloss'] = pf.avgloss
            
    def logic_order(self):
        """ 
        產生投資組合的order

            採用對抗模式
        Returns:
            _type_: _description_
        """
        strategys_count = len(self.strategys)  # 策略總數

        # 當資料流入並改變時
        self.time_min_scale()
        self.add_data()
        # self.data = self.get_data()

        # levelage = 2  # 槓桿倍數
        # rsikpercent = 0.01  # 風險百分比
        # ClosedPostionprofit = [self.Portfolio_initcash]

        # strategy_order_info = {}  # 專門用來保存資料
        # datetimelist = []  # 保存時間
        # orders = []  # 保存訂單
        # stragtegy_names = []  # 保存策略名稱
        # Portfolio_ClosedPostionprofit = []  # 保存已平倉損益
        # Portfolio_profit = []  # 保存單次已平倉損益
        # sizes = []  # 用來買入部位
        # # 單次已平倉損益init
        # profit = 0
        # for each_index, each_row in self.data.items():
        #     for each_strategy_index, each_strategy_value in each_row.items():
        #         # 如果那個時間有資料的話 且有訂單的話
        #         if each_strategy_value:
        #             Order = each_strategy_value['Order']
        #             Open = each_strategy_value['Open']
        #             if Order:
        #                 # 這邊開始判斷單一資訊 # 用來編寫系統權重
        #                 if Order > 0:
        #                     # 當 ClosedPostionprofit[-1] 為負數時 給予最低委託單位
        #                     if ClosedPostionprofit[-1] < 0:
        #                         size = 1 * levelage / Open / strategys_count
        #                     else:
        #                         # size = self.leverage_model(
        #                         #     ClosedPostionprofit[-1], levelage, Open, strategys_count)

        #                         size = self.risk_model(
        #                             ClosedPostionprofit[-1], rsikpercent, each_strategy_value['avgloss'])
        #                 else:
        #                     size = 0
        #                 # size = 1

        #                 # =========================================================================================
        #                 new_value = copy.deepcopy(each_strategy_value)

        #                 # 進場價格(已加滑價)
        #                 if Order > 0:
        #                     new_value['Entryprice'] = Open * \
        #                         (1 +
        #                          self.strategys_maps[each_strategy_index].slippage)

        #                     new_value['buy_size'] = size
        #                     new_value['buy_fee'] = Open * new_value['buy_size'] * \
        #                         self.strategys_maps[each_strategy_index].fee

        #                 # 出場價格(已加滑價)
        #                 if Order < 0:
        #                     new_value['Exitsprice'] = Open * \
        #                         (1 -
        #                          self.strategys_maps[each_strategy_index].slippage)
        #                     new_value['sell_size'] = strategy_order_info[each_strategy_index][-1]['buy_size']
        #                     new_value['sell_fee'] = Open * new_value['sell_size'] * \
        #                         self.strategys_maps[each_strategy_index].fee

        #                 # 將資料保存下來
        #                 if each_strategy_index in strategy_order_info:
        #                     last_order = strategy_order_info[each_strategy_index][-1]
        #                     # 如果最後一次是多單
        #                     if Order < 0 and last_order['Order'] > 0:
        #                         # 取得已平倉損益(單次)
        #                         profit = (
        #                             new_value['Exitsprice'] - last_order['Entryprice']) * new_value['sell_size'] - last_order['buy_fee'] - new_value['sell_fee']

        #                         ClosedPostionprofit.append(
        #                             ClosedPostionprofit[-1] + profit)
        #                     else:
        #                         profit = 0
        #                     strategy_order_info[each_strategy_index].append(
        #                         new_value)
        #                 else:
        #                     strategy_order_info[each_strategy_index] = [
        #                         new_value]

        #                 datetimelist.append(each_index)
        #                 orders.append(Order)
        #                 stragtegy_names.append(each_strategy_index)
        #                 Portfolio_ClosedPostionprofit.append(
        #                     ClosedPostionprofit[-1])
        #                 Portfolio_profit.append(profit)
        #                 sizes.append(size)

        # # 系統資金校正 當差異值來到10% 發出賴通知
        # self.last_trade_money = Portfolio_ClosedPostionprofit[-1]

        # Order_Info = Portfolio_Order_Info(
        #     datetimelist, orders, stragtegy_names, Portfolio_profit, Portfolio_ClosedPostionprofit, self.Portfolio_initcash, sizes)

        # return Order_Info


class Quantify_systeam_DQN(object):
    def __init__(self, init_cash: int, formal: bool = True) -> None:
        """
            用來將類神經網絡所產生的訊號用來回測,此類職責判定是否採用歷史資料,並且可以即時交易

            1.檢查資料來源(回測,即時)
        """
        self.Trader = PortfolioTrader_DQN(Portfolio_initcash=init_cash)
        self.setting = AppSetting.get_DQN_setting()  # 取得類神經網絡的相關配置
        self.formal = formal

    def Portfolio_register(self, target_symobl: list):
        """
            正式投資組合上線環境
            先將基本資訊註冊
            並放入策略參數
            example :
                target_symobl
                    ['XMRUSDT', 'BTCUSDT', 'BTCDOMUSDT', 'BNBUSDT', 'ETHUSDT']
        """
        for each_symbol in target_symobl:
            # 這邊用來決定要運行甚麼策略
            for _strategy in ["DQNStrategy"]:
                strategyName = f"{each_symbol}-15K-OB-DQN"
                strategy = Strategy_base_DQN(
                    strategyName, _strategy, each_symbol, 15,  1.0,  self.setting['DEFAULT_COMMISSION_PERC'], self.setting['DEFAULT_SLIPPAGE'])

                self.Trader.register(strategy)

    def Portfolio_start(self):
        print("回測已經進入")
        pf = self.Trader.logic_order()
        return pf
