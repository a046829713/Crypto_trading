#!/usr/bin/env python3
import numpy as np
from DQN.lib.DataFeature import DataFeature
import torch
from DQN.lib import environ, models, Backtest
import re
from AppSetting import AppSetting
from .common import Strategy_base_DQN
from utils.TimeCountMsg import TimeCountMsg
import time
# 尚未驗算實際下單部位


class Record_Orders():
    def __init__(self, strategy: Strategy_base_DQN, formal: bool = False) -> None:
        self.strategy = strategy
        self.model_count_path = strategy.model_count_path
        self.setting = AppSetting.get_DQN_setting()
        self.formal = formal

        self.BARS = re.search(
            '\d+', self.model_count_path.split('\\')[1].split('-')[2])
        self.BARS = int(self.BARS.group())
        self.EPSILON = 0.00

        self.main_count()

    @TimeCountMsg.record_timemsg
    def main_count(self):
        app = DataFeature(self.formal)
        prices = app.get_test_net_work_data(
            symbol=self.strategy.symbol_name, symbol_data=self.strategy.df)  # len(prices.open) 2562

        # 實際上在使用的時候 他並沒有reset_on_close
        env = environ.StocksEnv(prices, bars_count=self.BARS, reset_on_close=False, commission=self.setting['MODEL_DEFAULT_COMMISSION_PERC'],
                                state_1d=self.setting['STATE_1D'], random_ofs_on_reset=False, reward_on_close=self.setting['REWARD_ON_CLOSE'],  volumes=self.setting['VOLUMES_TURNON'])

        if self.setting['STATE_1D']:
            net = models.DQNConv1D(
                env.observation_space.shape, env.action_space.n)
        else:
            net = models.SimpleFFDQN(
                env.observation_space.shape[0], env.action_space.n)

        net.load_state_dict(torch.load(
            self.model_count_path, map_location=lambda storage, loc: storage))


        # 对模型进行脚本化，并用示例输入
        # example_input = torch.tensor(np.array([env.reset()]))  # 使用环境重置作为示例输入
        # scripted_net = net.script_model(example_input)

        obs = env.reset()  # 從1開始,並不是從0開始
        start_price = env._state._cur_close()        
        step_idx = 0        
        record_orders = []
        while True:
            step_idx += 1
            obs_v = torch.tensor(np.array([obs]))            
            out_v = net(obs_v)            
            action_idx = out_v.max(dim=1)[1].item()
            record_orders.append(self._parser_order(action_idx))            
            obs, reward, done, _ = env.step(action_idx)
            if done:
                break
                        
        self.pf = Backtest.Backtest(
            self.strategy.df, self.BARS, self.strategy).order_becktest(record_orders)
        

        
    def getpf(self):
        return self.pf

    def count_marketpostion(self, action, marketpostion):
        # Skip = 0
        # Buy = 1
        # Close = 2
        if action == 0:
            # 部位不需要改變
            return marketpostion

        if action == 1:
            marketpostion = 1
            return marketpostion

        if action == 2:
            marketpostion = 0
            return marketpostion
        
    def _parser_order(self, action_value: int):
        if action_value == 2:
            return -1
        return action_value
