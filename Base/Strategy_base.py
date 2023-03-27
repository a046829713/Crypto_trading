import pandas as pd
from Count.Base import Event_count, vecbot_count
import numpy as np
import pandas as pd
from Count import nb
import copy
import talib
import time
import typing
from Database.SQL_operate import DB_operate
from Datatransformer import Datatransformer


class Strategy_base(object):
    """ 
    取得策略的基本資料及訊息
    Args:
        object (_type_): _description_
    """

    def __init__(self,
                 strategy_name: str,
                 symbol_name: str,
                 freq_time: int,
                 size: float,
                 fee: float,
                 slippage: float,
                 init_cash: float = 10000.0,
                 symobl_type: str = "Futures",
                 lookback_date: str = None) -> None:
        """ 
        to get strategy info msg

        Args:
            strategy_name (str): distinguish symbol 
            symbol_name (int): _description_
                like : BTCUSDT
            freq_time (int): _description_
            fee (float): _description_
            slippage (float): _description_
            lookback_date (str): "2022-01-01"
        """
        self.strategy_name = strategy_name
        self.symbol_name = symbol_name
        self.freq_time = freq_time
        self.size = size
        self.fee = fee
        self.slippage = slippage
        self.init_cash = init_cash
        self.symobl_type = symobl_type
        self.lookback_date = lookback_date

        self.data, self.array_data = self.simulationdata()
        self.datetimes = Event_count.get_index(self.data)

    def simulationdata(self):
        """

        Args:
            data_type (str, optional): _description_. Defaults to 'event_data'.

        Returns:
            _type_: _description_
        """
        if self.symobl_type == 'Futures':
            self.symobl_type = "F"

        # self.df = pd.read_csv(
        #     f"{self.symbol_name}-{self.symobl_type}-{self.freq_time}-Min.csv")

        self.df = DB_operate().read_Dateframe(
            f"select Datetime, Open, High, Low, Close, Volume from `{self.symbol_name.lower()}-{self.symobl_type.lower()}`;")

        self.df.set_index("Datetime", inplace=True)

        self.df = Datatransformer().get_tradedata(
            original_df=self.df, freq=self.freq_time)
        self.df.index = self.df.index.astype(str)
        if self.lookback_date:
            self.df = self.df[self.df.index > self.lookback_date]

        return self.df.to_dict("index"), self.df.to_numpy()


class Strategy_atom(object):
    """ 
    取得策略的基本訊息
    Args:
        object (_type_): _description_
    """

    def __init__(self,
                 strategy_name: str,
                 symbol_name: str,
                 freq_time: int,
                 size: float,
                 fee: float,
                 slippage: float,
                 init_cash: float = 10000.0,
                 symobl_type: str = "Futures",
                 lookback_date: str = None) -> None:
        """ 
        to get strategy info msg

        Args:
            strategy_name (str): distinguish symbol 
            symbol_name (int): _description_
                like : BTCUSDT
            freq_time (int): _description_
            fee (float): _description_
            slippage (float): _description_
            lookback_date (str): "2022-01-01"
        """
        self.strategy_name = strategy_name
        self.symbol_name = symbol_name
        self.freq_time = freq_time
        self.size = size
        self.fee = fee
        self.slippage = slippage
        self.init_cash = init_cash
        self.symobl_type = symobl_type
        self.lookback_date = lookback_date

    def simulationdata(self):
        """

        Args:
            data_type (str, optional): _description_. Defaults to 'event_data'.

        Returns:
            _type_: _description_
        """
        if self.symobl_type == 'Futures':
            self.symobl_type = "F"

        if self.lookback_date:
            self.df = self.df[self.df.index > self.lookback_date]

        return self.df.to_dict("index"), self.df.to_numpy()


class Np_Order_Info(object):
    """ 用來處理訂單的相關資訊
    Args:
        object (_type_): _description_
    """

    def __init__(self, datetime_list,
                 orders: np.ndarray,
                 marketpostion: np.ndarray,
                 entryprice: np.ndarray,
                 buy_Fees: np.ndarray,
                 sell_Fees: np.ndarray,
                 OpenPostionprofit: np.ndarray,
                 ClosedPostionprofit: np.ndarray,
                 profit: np.ndarray,
                 Gross_profit: np.ndarray,
                 Gross_loss: np.ndarray,
                 all_Fees: np.ndarray,
                 netprofit: np.ndarray,
                 ) -> None:
        # 取得order儲存列
        self.order = pd.DataFrame(datetime_list, columns=['Datetime'])
        self.order['Order'] = orders
        self.order['Marketpostion'] = marketpostion
        self.order['Entryprice'] = entryprice
        self.order['Buy_Fees'] = buy_Fees
        self.order['Sell_Fees'] = sell_Fees
        self.order['OpenPostionprofit'] = OpenPostionprofit
        self.order['ClosedPostionprofit'] = ClosedPostionprofit
        self.order['Profit'] = profit
        self.order['Gross_profit'] = Gross_profit
        self.order['Gross_loss'] = Gross_loss
        self.order['all_Fees'] = all_Fees
        self.order['netprofit'] = netprofit

        # 壓縮資訊減少運算
        self.order = self.order[self.order['Order'] != 0]
        self.order.set_index("Datetime", inplace=True)

        # 取得需要二次運算的資料(計算勝率，賠率....繪圖)
        self.ClosedPostionprofit_array = self.order['ClosedPostionprofit'].to_numpy(
        )

    def register(self, strategy_info: Strategy_base):
        """將原始策略的資訊記錄起來

        Args:
            strategy_info (_type_): _description_
        """
        self.strategy_info = strategy_info

    @property
    def avgloss(self) -> float:
        """ 
            透過毛損來計算平均策略虧損

        Returns:
            _type_: _description_
        """
        if self.LossTrades == 0:
            return -100.0 # 由於都沒有交易輸的紀錄
        else:
            return self.order['Gross_loss'].iloc[-1] / self.LossTrades

    @property
    def TotalTrades(self) -> int:
        """ 透過訂單的長度即可判斷交易的次數

        Returns:
            _type_: _description_
        """
        return divmod(len(self.order), 2)[0]

    @property
    def WinTrades(self) -> int:
        """ 取得獲勝的次數
        Returns:
            _type_: _description_
        """
        return len(self.order['Profit'][self.order['Profit'] > 0])

    @property
    def LossTrades(self) -> int:
        """取得失敗的次數

        Returns:
            int: to get from profit
        """
        return len(self.order['Profit'][self.order['Profit'] < 0])

    @property
    def Percent_profitable(self) -> float:
        """取得盈利(勝率)(非百分比) 不全部輸出小數點位數

        Returns:
            float: _description_
        """
        return round(self.WinTrades / self.TotalTrades, 3)

    @property
    def drawdown(self):
        """
            取得回撤金額
        """
        return nb.get_drawdown(self.ClosedPostionprofit_array)

    @property
    def drawdown_per(self):
        """
            取得回撤百分比

        """

        if self.__class__.__name__ == "Portfolio_Order_Info":
            return nb.get_drawdown_per(self.ClosedPostionprofit_array, self.Portfolio_initcash)
        else:
            return nb.get_drawdown_per(self.ClosedPostionprofit_array, self.strategy_info.init_cash)

    @property
    def UI_indicators(self):
        """ 
            可根据价格下跌的深度和持续时间来衡量下行风险
        Returns:
            _type_: _description_
        """
        sumallDD = np.sum(self.drawdown_per**2)
        ROI = (
            self.ClosedPostionprofit_array[-1] / self.strategy_info.init_cash)-1
        ui_ = (ROI*100) / ((sumallDD / self.TotalTrades)**0.5)
        return ui_


class small_Np_Order_Info(Np_Order_Info):
    """ 用來處理最佳化訂單的相關資訊
    Args:
        object (_type_): _description_
    """

    def __init__(self,
                 datetime_list,
                 orders: np.ndarray,
                 ClosedPostionprofit: np.ndarray,
                 ) -> None:
        # 取得order儲存列
        self.order = pd.DataFrame(datetime_list, columns=['Datetime'])
        self.order['Order'] = orders
        self.order['ClosedPostionprofit'] = ClosedPostionprofit

        # 壓縮資訊減少運算
        self.order = self.order[self.order['Order'] != 0]
        self.order.set_index("Datetime", inplace=True)

        # 取得需要二次運算的資料(計算勝率，賠率....繪圖)
        self.ClosedPostionprofit_array = self.order['ClosedPostionprofit'].to_numpy(
        )


class ALL_order_INFO(Np_Order_Info):
    def __init__(self) -> None:
        pass

    def register_data(self,
                      datetime_list,
                      orders: np.ndarray,
                      ClosedPostionprofit: np.ndarray,):
        # 取得order儲存列
        self.order = pd.DataFrame(datetime_list, columns=['Datetime'])
        self.order['Order'] = orders
        self.order['ClosedPostionprofit'] = ClosedPostionprofit

        # 壓縮資訊減少運算
        self.order = self.order[self.order['Order'] != 0]
        self.order.set_index("Datetime", inplace=True)

        # 取得需要二次運算的資料(計算勝率，賠率....繪圖)
        self.ClosedPostionprofit_array = self.order['ClosedPostionprofit'].to_numpy(
        )


class Portfolio_Order_Info(Np_Order_Info):
    def __init__(self, datetime_list, orders, stragtegy_names, Portfolio_profit, Portfolio_ClosedPostionprofit, Portfolio_initcash, sizes):
        self.order = pd.DataFrame(datetime_list, columns=['Datetime'])
        self.order['Order'] = orders
        self.order['StragtegyNames'] = stragtegy_names
        self.order['Profit'] = Portfolio_profit
        self.order['ClosedPostionprofit'] = Portfolio_ClosedPostionprofit
        self.order['sizes'] = sizes
        self.order.set_index("Datetime", inplace=True)

        self.ClosedPostionprofit_array = self.order['ClosedPostionprofit'].to_numpy(
        )
        self.Portfolio_initcash = Portfolio_initcash
        self.norepeat_stragtegy_names = set(stragtegy_names)

    def get_last_status(self):
        last_status = {}
        for each_stragtegy_name in self.norepeat_stragtegy_names:
            each_df = self.order[self.order['StragtegyNames']
                                 == each_stragtegy_name]
            current_marketpostion = each_df['Order'].sum()
            current_size = each_df['sizes'].iloc[-1]
            last_status.update(
                {each_stragtegy_name: [current_marketpostion, current_size]})

        return last_status


class Np_Order_Strategy(object):
    """ order產生裝置
        來自向量式

    Args:
        object (_type_): _description_

        original_data columns name 
            'Open', 'High', 'Low', 'Close', 'Volume'
    """

    def __init__(self, strategy_info: Strategy_base) -> None:
        self.strategy_info = strategy_info
        self.original_data = strategy_info.array_data
        self.datetime_list = strategy_info.datetimes
        self.Length = self.original_data.shape[0]
        self.open_array = self.original_data[:, 0]
        self.high_array = self.original_data[:, 1]
        self.low_array = self.original_data[:, 2]
        self.close_array = self.original_data[:, 3]

    def set_parameter(self, parameter: dict):
        self.parameter = parameter
        self.highest_n1 = self.parameter['highest_n1']
        self.lowest_n2 = self.parameter['lowest_n2']
        self.ATR_short1 = self.parameter['ATR_short1']
        self.ATR_long2 = self.parameter['ATR_long2']

    def main_logic(self):
        """
            這邊就類似MC內編譯地方
        """
        ATR_short = nb.get_ATR(
            self.Length, self.high_array, self.low_array, self.close_array, self.ATR_short1)

        ATR_long = nb.get_ATR(
            self.Length, self.high_array, self.low_array, self.close_array, self.ATR_long2)

        self.highestarr = vecbot_count.max_rolling(
            self.high_array, self.highest_n1)

        self.lowestarr = vecbot_count.min_rolling(
            self.low_array, self.lowest_n2)

        self.marketpostion_array = nb.get_marketpostion_array(
            self.Length, self.high_array, self.low_array, self.close_array, ATR_short, ATR_long, self.highestarr, self.lowestarr)

    def more_fast_logic_order(self):
        """
            用來創造閹割版的快速回測
        """

        # 有些比較難使用向量化完成
        self.highestarr = vecbot_count.max_rolling(
            self.high_array, self.highest_n1)

        self.lowestarr = vecbot_count.min_rolling(
            self.low_array, self.lowest_n2)

        return nb.more_fast_logic_order(
            self.open_array,
            self.high_array,
            self.low_array,
            self.close_array,
            self.highestarr,
            self.lowestarr,
            self.Length,
            self.strategy_info.init_cash,
            self.strategy_info.slippage,
            self.strategy_info.size,
            self.strategy_info.fee,
            self.ATR_short1,
            self.ATR_long2
        )

    def logic_order(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.highestarr = vecbot_count.max_rolling(
            self.high_array, self.highest_n1)

        self.lowestarr = vecbot_count.min_rolling(
            self.low_array, self.lowest_n2)

        orders, marketpostion_array, entryprice_array, buy_Fees_array, sell_Fees_array, OpenPostionprofit_array, ClosedPostionprofit_array, profit_array, Gross_profit_array, Gross_loss_array, all_Fees_array, netprofit_array = nb.logic_order(
            self.open_array,
            self.high_array,
            self.low_array,
            self.close_array,
            self.highestarr,
            self.lowestarr,
            self.Length,
            self.strategy_info.init_cash,
            self.strategy_info.slippage,
            self.strategy_info.size,
            self.strategy_info.fee,
            self.ATR_short1,
            self.ATR_long2
        )

        Order_Info = Np_Order_Info(self.datetime_list,
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

        Order_Info.register(self.strategy_info)

        return Order_Info


class PortfolioTrader(object):
    def __init__(self, Portfolio_initcash: int) -> None:
        self.strategys = []
        self.strategys_maps = {}
        self.strategys_parameter = {}
        self.Portfolio_initcash = Portfolio_initcash  # 投資組合起始資金

    def register(self, strategy_info, parameter: dict):
        """
            將所有的商品資訊 合併做總回測

        Args:
            strategy_info (Strategy_base): 策略基本資料

        """
        self.strategys.append(strategy_info)
        self.strategys_maps.update(
            {strategy_info.strategy_name: strategy_info})

        self.strategys_parameter.update(
            {strategy_info.strategy_name: parameter})

    def time_min_scale(self):
        all_datetimes = []
        for strategy in self.strategys:
            all_datetimes.extend(strategy.datetimes)

        self.min_scale = list(set(all_datetimes))
        self.min_scale.sort()

    def add_data(self):
        """
            將訂單的買賣方向匯入
        """
        for strategy in self.strategys:
            ordermap = Np_Order_Strategy(strategy)
            ordermap.set_parameter(
                self.strategys_parameter[strategy.strategy_name])
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

    def get_data(self):
        """
            採用字典的方式加快處理速度

        """
        data = {}
        for strategy in self.strategys:
            dict_data = strategy.df.to_dict('index')  # 這邊的DF 已經含有order了

            for each_time in self.min_scale:
                if each_time in data:
                    data[each_time].update(
                        {strategy.strategy_name: dict_data.get(each_time, None)})
                else:
                    data[each_time] = {
                        strategy.strategy_name: dict_data.get(each_time, None)}

        return data

    def leverage_model(self, money, levelage, Openprice, strategys_count):
        """
            將即時資金乘上槓桿倍數所做的邏輯運算        
        """

        return money * levelage / Openprice / strategys_count

    def risk_model(self, money, rsikpercent, avgloss) -> float:
        """風險百分比管理模式

        Args:
            money (_type_): 資金量
            rsikpercent (_type_): 風險比率
            avgloss (_type_): 每單位損失金錢

        Returns:
            _type_: _description_
        """
        # print("資金量:", money, "風險比率:", rsikpercent,
        #       '每單位損失金錢:', abs(avgloss), "實際下單數量:", money * rsikpercent / abs(avgloss))
        return money * rsikpercent / abs(avgloss)

    def logic_order(self):
        """ 產生投資組合的order

            採用對抗模式
        Returns:
            _type_: _description_
        """
        strategys_count = len(self.strategys)  # 策略總數

        # 當資料流入並改變時
        self.time_min_scale()
        self.add_data()
        self.data = self.get_data()

        levelage = 2  # 槓桿倍數
        rsikpercent = 0.01  # 風險百分比
        ClosedPostionprofit = [self.Portfolio_initcash]

        strategy_order_info = {}  # 專門用來保存資料
        datetimelist = []  # 保存時間
        orders = []  # 保存訂單
        stragtegy_names = []  # 保存策略名稱
        Portfolio_ClosedPostionprofit = []  # 保存已平倉損益
        Portfolio_profit = []  # 保存單次已平倉損益
        sizes = []  # 用來買入部位
        # 單次已平倉損益init
        profit = 0
        for each_index, each_row in self.data.items():
            for each_strategy_index, each_strategy_value in each_row.items():
                # 如果那個時間有資料的話 且有訂單的話
                if each_strategy_value:
                    Order = each_strategy_value['Order']
                    Open = each_strategy_value['Open']
                    if Order:
                        # 這邊開始判斷單一資訊 # 用來編寫系統權重
                        if Order > 0:
                            # 當 ClosedPostionprofit[-1] 為負數時 給予最低委託單位
                            if ClosedPostionprofit[-1] < 0:
                                size = 1 * levelage / Open / strategys_count
                            else:
                                # size = self.leverage_model(
                                #     ClosedPostionprofit[-1], levelage, Open, strategys_count)

                                size = self.risk_model(
                                    ClosedPostionprofit[-1], rsikpercent, each_strategy_value['avgloss'])

                        else:
                            size = 0
                        # size = 1

                        # =========================================================================================
                        new_value = copy.deepcopy(each_strategy_value)

                        # 進場價格(已加滑價)
                        if Order > 0:
                            new_value['Entryprice'] = Open * \
                                (1 +
                                 self.strategys_maps[each_strategy_index].slippage)

                            new_value['buy_size'] = size
                            new_value['buy_fee'] = Open * new_value['buy_size'] * \
                                self.strategys_maps[each_strategy_index].fee

                        # 出場價格(已加滑價)
                        if Order < 0:
                            new_value['Exitsprice'] = Open * \
                                (1 -
                                 self.strategys_maps[each_strategy_index].slippage)
                            new_value['sell_size'] = strategy_order_info[each_strategy_index][-1]['buy_size']
                            new_value['sell_fee'] = Open * new_value['sell_size'] * \
                                self.strategys_maps[each_strategy_index].fee

                        # 將資料保存下來
                        if each_strategy_index in strategy_order_info:
                            last_order = strategy_order_info[each_strategy_index][-1]
                            # 如果最後一次是多單
                            if Order < 0 and last_order['Order'] > 0:
                                # 取得已平倉損益(單次)
                                profit = (
                                    new_value['Exitsprice'] - last_order['Entryprice']) * new_value['sell_size'] - last_order['buy_fee'] - new_value['sell_fee']

                                ClosedPostionprofit.append(
                                    ClosedPostionprofit[-1] + profit)
                            else:
                                profit = 0
                            strategy_order_info[each_strategy_index].append(
                                new_value)
                        else:
                            strategy_order_info[each_strategy_index] = [
                                new_value]

                        datetimelist.append(each_index)
                        orders.append(Order)
                        stragtegy_names.append(each_strategy_index)
                        Portfolio_ClosedPostionprofit.append(
                            ClosedPostionprofit[-1])
                        Portfolio_profit.append(profit)
                        sizes.append(size)

        # 系統資金校正 當差異值來到10% 發出賴通知
        self.last_trade_money = Portfolio_ClosedPostionprofit[-1]
        print(self.last_trade_money)
        Order_Info = Portfolio_Order_Info(
            datetimelist, orders, stragtegy_names, Portfolio_profit, Portfolio_ClosedPostionprofit, self.Portfolio_initcash, sizes)

        return Order_Info


class PortfolioOnline(PortfolioTrader):
    """
        即時交易系統
        將資料傳入並且運算出最後委託單是否與現在不想同
        進而判斷送出委託單

    Args:
        object (_type_): _description_
    """

    def register(self, strategy_info: Strategy_atom, parameter: dict):
        """
            將所有的商品資訊 合併做總回測

        Args:
            strategy_info (Strategy_atom): 策略基本資料

        """
        self.strategys.append(strategy_info)

        self.strategys_maps.update(
            {strategy_info.strategy_name: strategy_info})

        self.strategys_parameter.update(
            {strategy_info.strategy_name: parameter})
