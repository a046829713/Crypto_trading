#!/usr/bin/env python3
import numpy as np
from DQN.lib.DataFeature import DataFeature
import torch
from DQN.lib import environ, models,Backtest
import re
from AppSetting import AppSetting



# 尚未驗算實際下單部位

model_count_path = r'saves\20231011-105307-20k-True\mean_val-0.981.data'

BARS = re.search('\d+',model_count_path.split('\\')[1].split('-')[2])
BARS = int(BARS.group())
EPSILON = 0.00

setting = AppSetting.get_DQN_setting()

if __name__ == "__main__":
    app = DataFeature()    
    prices =  app.get_test_net_work_data(symbol='BNBUSDT') # len(prices.open) 2562    
    
    # 實際上在使用的時候 他並沒有reset_on_close
    env = environ.StocksEnv(prices, bars_count=BARS, reset_on_close=False, commission=setting['DEFAULT_COMMISSION_PERC'],
                            state_1d=False, random_ofs_on_reset=False, reward_on_close=setting['REWARD_ON_CLOSE'],  volumes=setting['VOLUMES_TURNON'])
    
    if False:
        net = models.DQNConv1D(env.observation_space.shape, env.action_space.n)
    else:
        net = models.SimpleFFDQN(env.observation_space.shape[0], env.action_space.n)

    net.load_state_dict(torch.load(model_count_path, map_location=lambda storage, loc: storage))

    obs = env.reset()# 從1開始,並不是從0開始
    
    start_price = env._state._cur_close()    
    
    total_reward = 0.0
    step_idx = 0
    rewards = []
    record_rewards =[]
    marketpostion = 0
    marketpostions = []
    record_oreders =[]
    def count_marketpostion(action, marketpostion):
        
        # Skip = 0
        # Buy = 1
        # Close = 2
        if action == 0:
            # 部位不需要改變
            return marketpostion
        
        if action == 1:
            marketpostion =1
            return marketpostion
        
        if action == 2:
            marketpostion = 0
            return marketpostion 
    
    while True:
        step_idx += 1
        obs_v = torch.tensor([obs])
        out_v = net(obs_v)   

        action_idx = out_v.max(dim=1)[1].item()
        
        if np.random.random() < EPSILON:
            action_idx = env.action_space.sample()
            
        action = environ.Actions(action_idx)
        
        def _parser_order(action_value:int):            
            if action_value == 2:
                return -1
            
            return action_value
        
        record_oreders.append(_parser_order(action_idx))
        
        marketpostion = count_marketpostion(action_idx,marketpostion)
        marketpostions.append(marketpostion)
        obs, reward, done, _ = env.step(action_idx)
        
        
        total_reward += reward
        rewards.append(total_reward)
        record_rewards.append(reward)
        if step_idx % 1000 == 0:
            print("%d: reward=%.3f" % (step_idx, total_reward))
        if done:
            break
    
    print(marketpostions)
    Backtest.Backtest(app.df,BARS).order_becktest(record_oreders)