import pandas as pd
from Count.Base import Event_count
import numpy as np
import pandas as pd
from Count import nb
from collections import namedtuple
import copy

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
                 symobl_type: str = "Futures") -> None:
        """ 
        to get strategy info msg

        Args:
            strategy_name (str): distinguish symbol 
            symbol_name (int): _description_
                like : BTCUSDT
            freq_time (int): _description_
            fee (float): _description_
            slippage (float): _description_
        """
        self.strategy_name = strategy_name
        self.symbol_name = symbol_name
        self.freq_time = freq_time
        self.size = size
        self.fee = fee
        self.slippage = slippage
        self.init_cash = init_cash
        self.symobl_type = symobl_type
        self.data = self.simulationdata()
        self.datetimes = Event_count.get_index(self.data)
        self.array_data = self.simulationdata('array_data')

    def simulationdata(self, data_type: str = 'event_data'):
        """

        Args:
            data_type (str, optional): _description_. Defaults to 'event_data'.

        Returns:
            _type_: _description_
        """
        if self.symobl_type == 'Futures':
            self.symobl_type = "F"

        self.df = pd.read_csv(
            f"{self.symbol_name}-{self.symobl_type}-{self.freq_time}-Min.csv")
        self.df.set_index("Datetime", inplace=True)

        if data_type == 'event_data':
            return self.df.to_dict("index")
        elif data_type == 'array_data':
            return self.df.to_numpy()


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
        return nb.get_drawdown_per(self.ClosedPostionprofit_array)

    @property
    def UI_indicators(self):
        """ 還需要驗算

        Returns:
            _type_: _description_
        """
        sumallDD = np.sum(self.drawdown_per**2)
        ROI = (
            self.ClosedPostionprofit_array[-1] / self.strategy_info.init_cash)-1
        ui_ = (ROI*100) / ((sumallDD / self.TotalTrades)**0.5)
        return ui_


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

    def set_parameter(self, parameter: dict):
        self.parameter = parameter

    def logic_order(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        high_array = self.original_data[:, 1]
        low_array = self.original_data[:, 2]
        close_array = self.original_data[:, 3]

        orders, marketpostion_array, entryprice_array, buy_Fees_array, sell_Fees_array, OpenPostionprofit_array, ClosedPostionprofit_array, profit_array, Gross_profit_array, Gross_loss_array, all_Fees_array, netprofit_array = nb.logic_order(
            high_array,
            low_array,
            close_array,
            self.Length,
            self.strategy_info.init_cash,
            self.strategy_info.slippage,
            self.strategy_info.size,
            self.strategy_info.fee,
            self.parameter['highest_n1'],
            self.parameter['lowest_n2'])

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
    def __init__(self) -> None:
        self.strategys = []
        self.strategys_maps ={}

    def register(self, strategy_info: Strategy_base):
        """
            將所有的商品資訊 合併做總回測

        Args:
            strategy_info (Strategy_base): 策略基本資料

        """
        self.strategys.append(strategy_info)
        self.strategys_maps.update({strategy_info.strategy_name:strategy_info}) 
    
    def time_min_scale(self):
        all_datetimes = []
        for strategy in self.strategys:
            strategy: Strategy_base
            all_datetimes.extend(strategy.datetimes)

        self.min_scale = list(set(all_datetimes))
        self.min_scale.sort()

    def get_pd_data(self):
        """
            減少搜尋的量 以column 欄位值做塞選
            output:{
                "Open":
                        ......

                'Volume':                       
                                            BTCUSDT    ETHUSDT
                        Datetime
                        2019-09-09 01:45:00     0.002        NaN
                        2019-09-09 02:00:00     0.000        NaN
                        2019-09-09 02:15:00     0.000        NaN
                        2019-09-09 02:30:00     0.000        NaN
                        2019-09-09 02:45:00     0.000        NaN
                        ...                       ...        ...
                        2022-10-29 14:30:00  2906.644  57096.426
                        2022-10-29 14:45:00  1182.533  20274.797
                        2022-10-29 15:00:00  1799.500  20477.292
                        2022-10-29 15:15:00  3720.461  39870.559
                        2022-10-29 15:30:00  1005.658  39955.072
            }
        """
        all_df = pd.DataFrame()
        for strategy in self.strategys:
            strategy: Strategy_base
            strategy.df["strategy_name"] = strategy.strategy_name
            all_df = pd.concat([all_df, strategy.df])

        data_map = {}
        for col in all_df.columns:
            if col == 'strategy_name':
                continue
            for strategy in self.strategys:
                if col in data_map:
                    data_map[col][strategy.strategy_name] = all_df[all_df['strategy_name']
                                                                   == strategy.strategy_name][col]
                else:
                    row_df = pd.DataFrame(
                        all_df[all_df['strategy_name'] == strategy.strategy_name][col])
                    row_df.rename(
                        columns={col: strategy.strategy_name}, inplace=True)
                    data_map.update({col: row_df})

        self.col_data = data_map

    def add_data(self):
        """
            將訂單的買賣方向匯入
        """
        for strategy in self.strategys:
            strategy: Strategy_base
            ordermap = Np_Order_Strategy(strategy)
            ordermap.set_parameter({'highest_n1': 470, 'lowest_n2': 370})
            pf = ordermap.logic_order()

            out_list = []
            for datetime_ in strategy.df.index:
                if datetime_ in pf.order.index:
                    out_list.append(pf.order['Order'][datetime_])
                else:
                    out_list.append(0)

            strategy.df['Order'] = (out_list)

    def get_data(self):
        """
            採用字典的方式加快處理速度

        """
        data = {}
        strategy: Strategy_base
        for strategy in self.strategys:
            dict_data = strategy.df.to_dict('index')
            for each_time in self.min_scale:
                if each_time in data:
                    data[each_time].update(
                        {strategy.strategy_name: dict_data.get(each_time, None)})
                else:
                    data[each_time] = {
                        strategy.strategy_name: dict_data.get(each_time, None)}
        return data

    def logic_order(self):
        """ 產生投資組合的order

        Returns:
            _type_: _description_
        """

        self.time_min_scale()
        self.add_data()
        self.data = self.get_data()

        
        Portfolio_profit = 10000
        
        for each_index, each_row in self.data.items():
            for each_strategy_index, each_strategy_value in each_row.items():
                # 如果那個時間有資料的話 且有訂單的話
                if each_strategy_value:
                    if each_strategy_value['Order']:
                        # 這邊開始判斷單一資訊
                        entryprice = 0
                        
                        
                        new_value = copy.deepcopy(each_strategy_value)
                        if each_strategy_value['Order'] >0:
                            new_value['Entryprice'] = each_strategy_value['Close'] * (1 + self.strategys_maps[each_strategy_index].slippage)
                        
                        print(each_index, each_strategy_index,new_value)
                        
                        
