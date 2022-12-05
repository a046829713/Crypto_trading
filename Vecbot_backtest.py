from Base.Strategy_base import Strategy_base
from Count.Base import vecbot_count, Event_count
from Count import nb
from tqdm import tqdm
from Hyper_optimiza import Hyper_optimization
from Base.Order_Info import Np_Order_Info

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
        
        
        Order_Info.UI_indicators
        return Order_Info


inputs_parameter = {"highest_n1": list(
    range(10, 500, 10)), "lowest_n2": list(range(10, 500, 10))}

strategy1 = Strategy_base("BTCUSDT-15K-OB", "BTCUSDT", 15, 1.0, 0.002, 0.0025)
ordermap = Np_Order_Strategy(strategy1)

out_list = []
for each_parameter in tqdm(Hyper_optimization.generator_parameter(inputs_parameter)):
# for each_parameter in [{'highest_n1': 3, 'lowest_n2': 410}]:
    ordermap.set_parameter(each_parameter)
    pf = ordermap.logic_order()
    out_list.append([each_parameter,pf.UI_indicators])

    
print(out_list)
