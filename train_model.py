from AppSetting import AppSetting
import os
import gym
import numpy as np
import torch
import torch.optim as optim
import time
from DQN.lib import environ, models, common
from DQN import ptan
from DQN.lib.DataFeature import DataFeature
from tensorboardX import SummaryWriter
from datetime import datetime


# 問題紀錄:
# 1.為甚麼每次都要從5-6根K棒開始運行程序?
# 2.從甚麼地方將手續費匯入?



# 代辦事項:
# 驗證程序(run_model)
# 現貨資料爬取
# 多商品訓練的轉換,=> 1.訓練時候隨機轉換商品 2.EPSILON_STEPS 要隨著商品總數量做變化

TARGET_NET_SYNC = 1000
GAMMA = 0.99
REPLAY_SIZE = 100000
REPLAY_INITIAL = 10000
REWARD_STEPS = 2
STATES_TO_EVALUATE = 1000
EVAL_EVERY_STEP = 1000
EPSILON_START = 1.0
EPSILON_STOP = 0.1

CHECKPOINT_EVERY_STEP = 1000000
VALIDATION_EVERY_STEP = 100000

setting = AppSetting.get_DQN_setting()

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("目前使用的裝置是?", device)

    # 用來儲存的位置
    saves_path = os.path.join(setting['SAVES_PATH'], datetime.strftime(
        datetime.now(), "%Y%m%d-%H%M%S") + '-' + str(setting['BARS_COUNT']) + 'k-' + str(setting['REWARD_ON_CLOSE']))

    os.makedirs(saves_path, exist_ok=True)

    stock_data = DataFeature().get_net_work_data()
    
    EPSILON_STEPS = 1000000 * len(stock_data)
    
    print(EPSILON_STEPS)
    env = environ.StocksEnv(stock_data, bars_count=setting['BARS_COUNT'],
                            reset_on_close=True, state_1d=False, reward_on_close=setting['REWARD_ON_CLOSE'], volumes=setting['VOLUMES_TURNON'])

    env_tst = environ.StocksEnv(
        stock_data, bars_count=setting['BARS_COUNT'], reset_on_close=True, state_1d=False)

    env = gym.wrappers.TimeLimit(env, max_episode_steps=1000)

    writer = SummaryWriter(comment="-simple-")

    print("觀察空間:", env.observation_space.shape[0])
    net = models.SimpleFFDQN(
        env.observation_space.shape[0], env.action_space.n).to(device)

    tgt_net = ptan.agent.TargetNet(net)

    print("機率起始值:", EPSILON_START)
    selector = ptan.actions.EpsilonGreedyActionSelector(EPSILON_START)

    agent = ptan.agent.DQNAgent(net, selector, device=device)
    exp_source = ptan.experience.ExperienceSourceFirstLast(
        env, agent, GAMMA, steps_count=REWARD_STEPS)

    buffer = ptan.experience.ExperienceReplayBuffer(exp_source, REPLAY_SIZE)
    optimizer = optim.Adam(net.parameters(), lr=setting['LEARNING_RATE'])

    # main training loop
    step_idx = 0
    eval_states = None
    best_mean_val = None

    with common.RewardTracker(writer, np.inf, group_rewards=100) as reward_tracker:
        while True:
            step_idx += 1
            buffer.populate(1)

            # 探索率
            selector.epsilon = max(
                EPSILON_STOP, EPSILON_START - step_idx / EPSILON_STEPS)

            # [(-2.5305491551459296, 10)]
            # 跑了一輪之後,清空原本的數據,並且取得獎勵
            new_rewards = exp_source.pop_rewards_steps()

            if new_rewards:
                reward_tracker.reward(
                    new_rewards[0], step_idx, selector.epsilon)

            if len(buffer) < REPLAY_INITIAL:
                continue

            if eval_states is None:
                print("Initial buffer populated, start training")
                eval_states = buffer.sample(STATES_TO_EVALUATE)
                eval_states = [np.array(transition.state, copy=False)
                               for transition in eval_states]
                eval_states = np.array(eval_states, copy=False)

            if step_idx % EVAL_EVERY_STEP == 0:
                # eval_states 只產生了一次
                # 後面沒有重新產生
                mean_val = common.calc_values_of_states(
                    eval_states, net, device=device)
                writer.add_scalar("values_mean", mean_val, step_idx)
                if best_mean_val is None or best_mean_val < mean_val:
                    if best_mean_val is not None:
                        print("%d: Best mean value updated %.3f -> %.3f" %
                              (step_idx, best_mean_val, mean_val))
                    best_mean_val = mean_val
                    # 用來保存最厲害的模型
                    torch.save(net.state_dict(), os.path.join(
                        saves_path, "mean_val-%.3f.data" % mean_val))

            optimizer.zero_grad()
            batch = buffer.sample(setting['BATCH_SIZE'])

            loss_v = common.calc_loss(
                batch, net, tgt_net.target_model, GAMMA ** REWARD_STEPS, device=device)
            loss_v.backward()
            optimizer.step()

            if step_idx % TARGET_NET_SYNC == 0:
                tgt_net.sync()

            
            # 保存檢查點
            if step_idx % CHECKPOINT_EVERY_STEP == 0:
                idx = step_idx // CHECKPOINT_EVERY_STEP
                torch.save(net.state_dict(), os.path.join(
                    saves_path, "checkpoint-%3d.data" % idx))
