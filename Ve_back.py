# from Base.Strategy_base import Strategy_base
# from Base.Strategy_base import Np_Order_Strategy
# import numpy as np
# from tqdm import tqdm
# from Hyper_optimiza import Hyper_optimization
    
# strategy1 = Strategy_base("BTCUSDT-15K-OB", "BTCUSDT", 15, 1.0, 0.002, 0.0025)


# def optimize():
#     """
#         用來計算最佳化的參數
#     """
#     ordermap = Np_Order_Strategy(strategy1)
#     inputs_parameter = {"highest_n1": np.arange(10, 500, 10, dtype=np.int16),
#                         "lowest_n2": np.arange(10, 500, 10, dtype=np.int16),
#                         'ATR_short1': np.arange(10, 200, 10, dtype=np.int16),
#                         'ATR_long2': np.arange(10, 200, 10, dtype=np.int16)}


#     for each_parameter in tqdm(Hyper_optimization.generator_parameter(inputs_parameter)):
#         ordermap.set_parameter(
#             {'highest_n1': 470, 'lowest_n2': 370, 'ATR_short1': 30, 'ATR_long2': 60})
#         ordermap.vb_logic_order()

# optimize()