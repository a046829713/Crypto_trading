from Base.Strategy_base import Strategy_base
from Base.Strategy_base import Np_Order_Strategy
from Base.Strategy_base import PortfolioTrader
from Count.Base import vecbot_count, Event_count
from Count import nb
from tqdm import tqdm
from Hyper_optimiza import Hyper_optimization
from Plot_draw.Picture_Mode import Picture_maker


class Trading_systeam():
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
        inputs_parameter = {"highest_n1": list(range(10, 500, 20)), "lowest_n2": list(range(
            10, 500, 20)), 'ATR_short1': list(range(30, 200, 20)), 'ATR_long2': list(range(60, 200, 20))}

        out_list = []
        for each_parameter in tqdm(Hyper_optimization.generator_parameter(inputs_parameter)):
            ordermap.set_parameter(each_parameter)
            pf = ordermap.more_fast_logic_order()
            # 這邊有0再思考一下
            if len(pf.order) ==0:continue
            out_list.append([each_parameter, pf.UI_indicators])
            
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
        ordermap.set_parameter(
            {'highest_n1': 470, 'lowest_n2': 370, 'ATR_short1': 30, 'ATR_long2': 60})
        pf = ordermap.more_fast_logic_order()
        Picture_maker(pf)

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
    systeam = Trading_systeam()
    systeam.optimize()
