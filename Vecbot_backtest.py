from Base.Strategy_base import Strategy_base
from Base.Strategy_base import Np_Order_Strategy
from Base.Strategy_base import PortfolioTrader
from Count.Base import vecbot_count, Event_count
from Count import nb
from tqdm import tqdm
from Hyper_optimiza import Hyper_optimization
from Plot_draw.Picture_Mode import Picture_maker

strategy1 = Strategy_base("BTCUSDT-15K-OB", "BTCUSDT", 15, 1.0, 0.002, 0.0025)
ordermap1 = Np_Order_Strategy(strategy1)


strategy2 = Strategy_base("ETHUSDT-15K-OB", "ETHUSDT", 15, 1.0, 0.002, 0.0025)
ordermap2 = Np_Order_Strategy(strategy2)

strategy3 = Strategy_base("BTCUSDT-2K-OB", "BTCUSDT", 2, 1.0, 0.002, 0.0025)
ordermap3 = Np_Order_Strategy(strategy3)

# 優化
def optimize():
    """
        用來計算最佳化的參數
    """

    inputs_parameter = {"highest_n1": list(
        range(10, 500, 10)), "lowest_n2": list(range(10, 500, 10))}
    out_list = []
    # for each_parameter in tqdm(Hyper_optimization.generator_parameter(inputs_parameter)):
    for each_parameter in [{'highest_n1': 470, 'lowest_n2': 370}]:
        ordermap.set_parameter(each_parameter)
        pf = ordermap.logic_order()
        out_list.append([each_parameter, pf.UI_indicators])

        Picture_maker(pf)

    UI_list = [i[1] for i in out_list]
    max_data = max(UI_list)

    for i in out_list:
        if i[1] == max_data:
            print(i)


# 普通

def Backtesting():
    ordermap.set_parameter({'highest_n1': 470, 'lowest_n2': 370})
    pf = ordermap.logic_order()
    print(pf)


# 總回測


app = PortfolioTrader()
app.register(strategy1)
app.register(strategy2)
app.register(strategy3)


app.logic_order()