from Base.Strategy_base import Strategy_base
from Base.Strategy_base import Np_Order_Strategy
from Base.Strategy_base import PortfolioTrader
from Base.Strategy_base import ALL_order_INFO
from tqdm import tqdm
from Hyper_optimiza import Hyper_optimization
from Plot_draw.Picture_Mode import Picture_maker
import numpy as np

        # sl_init_i = np.full(target_shape[1], -1, dtype=np.int_)
        # sl_init_price = np.full(target_shape[1], np.nan, dtype=np.float_)
        # sl_curr_i = np.full(target_shape[1], -1, dtype=np.int_)
        # sl_curr_price = np.full(target_shape[1], np.nan, dtype=np.float_)
        # sl_curr_stop = np.full(target_shape[1], np.nan, dtype=np.float_)
        # sl_curr_trail = np.full(target_shape[1], False, dtype=np.bool_)
        # tp_init_i = np.full(target_shape[1], -1, dtype=np.int_)
        # tp_init_price = np.full(target_shape[1], np.nan, dtype=np.float_)
        # tp_curr_stop = np.full(target_shape[1], np.nan, dtype=np.float_)
class Quantify_systeam():
    def __init__(self) -> None:
        self.strategy1 = Strategy_base(
            "BTCUSDT-15K-OB", "BTCUSDT", 15, 1.0, 0.002, 0.0025)

        self.strategy2 = Strategy_base(
            "ETHUSDT-15K-OB", "ETHUSDT", 15, 1.0, 0.002, 0.0025)

        self.strategy3 = Strategy_base(
            "BTCUSDT-2K-OB", "BTCUSDT", 2, 1.0, 0.002, 0.0025)

        # ordermap3 = Np_Order_Strategy(strategy3)

    def optimize(self):
        """
            用來計算最佳化的參數
        """
        ordermap = Np_Order_Strategy(self.strategy2)
        inputs_parameter = {"highest_n1": np.arange(10, 500, 10, dtype=np.int16),
                            "lowest_n2": np.arange(10, 500, 10, dtype=np.int16),
                            'ATR_short1': np.arange(10, 200, 10, dtype=np.float_),
                            'ATR_long2': np.arange(10, 200, 10, dtype=np.float_)}

        all_orderinfo = ALL_order_INFO()
        out_list=[]
        for each_parameter in tqdm(Hyper_optimization.generator_parameter(inputs_parameter)):
            ordermap.set_parameter(each_parameter)
            ordermap.more_fast_logic_order()
            # self.datetime_list, orders, ClosedPostionprofit_array = ordermap.more_fast_logic_order()
            # all_orderinfo.register(ordermap.strategy_info)
            # all_orderinfo.register_data(
            #     self.datetime_list, orders, ClosedPostionprofit_array)
            
            
            
            # if len(all_orderinfo.order) == 0:
            #     continue
            # out_list.append([each_parameter, all_orderinfo.UI_indicators])


        # print(out_list)
        # UI_list = [i[1] for i in out_list]
        # max_data = max(UI_list)

        # for i in out_list:
        #     if i[1] == max_data:
        #         print(i)

    def Backtesting(self):
        """
            普通回測模式
        """
        ordermap = Np_Order_Strategy(self.strategy1)
        ordermap.set_parameter(
            {'highest_n1': 470, 'lowest_n2': 370, 'ATR_short1': 30, 'ATR_long2': 60})
        pf = ordermap.more_fast_logic_order()
        # Picture_maker(pf)

    def PortfolioBacktesting(self):
        # 總回測
        app = PortfolioTrader()
        app.register(
            self.strategy1, {'highest_n1': 470, 'lowest_n2': 370})
        app.register(
            self.strategy2, {'highest_n1': 230, 'lowest_n2': 420})

        pf = app.logic_order()
        Picture_maker(pf)


if __name__ == "__main__":
    systeam = Quantify_systeam()
    systeam.Backtesting()
