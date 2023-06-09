import pandas as pd
import numpy as np
from typing import Sequence


class Portfolio_count():
    pass


class Pandas_count():
    @staticmethod
    def highest(row_data: pd.Series, freq: int):
        """
            取得資料滾動的最高價
        """
        return row_data.rolling(freq).max()

    @staticmethod
    def lowest(row_data: pd.Series, freq: int):
        """
            取得資料滾動的最低價
        """
        return row_data.rolling(freq).min()

    @staticmethod
    def momentum(price: pd.Series, periond: int) -> pd.Series:
        """
            取得動量
        """
        lagPrice = price.shift(periond)
        momen = price / lagPrice - 1
        return momen


class Event_count():
    @staticmethod
    def get_highest(data: list, periods):
        return max(data[-(periods+1):-1])

    @staticmethod
    def get_lowest(data: list, periods):
        return min(data[-(periods+1):-1])

    @staticmethod
    def get_profit(profit, marketpostion, last_marketpostion, Close, sell_sizes, last_entryprice):
        if marketpostion == 0 and last_marketpostion == 1:
            profit = Close * sell_sizes - last_entryprice * sell_sizes
        else:
            profit = 0
        return profit

    @staticmethod
    def get_OpenPostionprofit(OpenPostionprofit, marketpostion, last_marketpostion, buy_Fees, Close, buy_sizes, entryprice):
        if marketpostion == 1:
            OpenPostionprofit = Close * buy_sizes - entryprice * buy_sizes
        else:
            OpenPostionprofit = 0
        return OpenPostionprofit

    @staticmethod
    def get_ClosedPostionprofit(ClosedPostionprofit, marketpostion, last_marketpostion, buy_Fees, sell_Fees, Close, sizes, last_entryprice):
        # 我的定義是當部位改變的時候再紀錄
        if marketpostion == 1 and last_marketpostion == 0:
            ClosedPostionprofit = ClosedPostionprofit - buy_Fees
        elif marketpostion == 0 and last_marketpostion == 1:
            ClosedPostionprofit = ClosedPostionprofit - sell_Fees
            # 當部位為平倉後 計算交易損益
            ClosedPostionprofit = ClosedPostionprofit + \
                (Close * sizes - last_entryprice * sizes)
        return ClosedPostionprofit

    @staticmethod
    def get_entryprice(entryprice, Close, marketpostion, last_marketpostion, slippage=None):
        if marketpostion == 1 and last_marketpostion == 0:
            if slippage:
                entryprice = Close * (1 + slippage)
            else:
                entryprice = Close
        elif marketpostion == 0:
            entryprice = 0
        return entryprice

    @staticmethod
    def get_buy_Fees(buy_Fee, fee, size, Close, marketpostion, last_marketpostion):
        if marketpostion == 1 and last_marketpostion == 0:
            buy_Fee = Close * fee * size
        elif marketpostion == 0:
            buy_Fee = 0
        return buy_Fee

    @staticmethod
    def get_sell_Fees(sell_Fee, fee: float, size, Close, marketpostion, last_marketpostion):
        """_summary_

        Args:
            sell_Fee (_type_): _description_
            fee (float): 原始策略裡的手續費費率
            Close (_type_): _description_
            marketpostion (_type_): _description_
            last_marketpostion (_type_): _description_

        Returns:
            _type_: _description_
        """
        if marketpostion == 0 and last_marketpostion == 1:
            sell_Fee = Close * fee * size
        elif marketpostion == 0:
            sell_Fee = 0
        return sell_Fee

    @staticmethod
    def get_info(data: dict, target_name: str) -> list:
        return [value[target_name] for index, value in data.items()]

    @staticmethod
    def get_index(data: dict) -> list:
        return list(data.keys())

    @staticmethod
    def get_order(marketpostion: Sequence) -> list:
        out_list = []
        order = 0
        for i in range(len(marketpostion)):
            if i > 0:
                # 用來比較轉換的時候
                # 狀態一樣不需要改變
                if marketpostion[i] == marketpostion[i-1]:
                    order = 0

                # 當狀態不一樣的時候
                if marketpostion[i] != marketpostion[i-1]:
                    if marketpostion[i] == 1:
                        order = 1
                    else:
                        order = -1
            else:
                order = marketpostion[i]

            # 求 order size
            out_list.append(order)

        return out_list


class vecbot_count():
    @staticmethod
    def max_rolling(a, window, axis=1):
        try:
            max_arr = np.empty(shape=a.shape[0])
            shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
            strides = a.strides + (a.strides[-1],)
            rolling = np.lib.stride_tricks.as_strided(
                a, shape=shape, strides=strides)
            max_arr[window-1:] = np.roll(np.maximum.reduce(rolling, axis=1), 1)
            max_arr[:window] = np.nan
            return max_arr
        except Exception as e:
            if "negative dimensions are not allowed" in str(e):
                return 0
            else:
                raise e

    @staticmethod
    def min_rolling(a, window, axis=1):
        try:
            min_arr = np.empty(shape=a.shape[0])
            shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
            strides = a.strides + (a.strides[-1],)
            rolling = np.lib.stride_tricks.as_strided(
                a, shape=shape, strides=strides)
            min_arr[window-1:] = np.roll(np.minimum.reduce(rolling, axis=1), 1)
            min_arr[:window] = np.nan
            return min_arr
        except Exception as e:
            if "negative dimensions are not allowed" in str(e):
                return 0
            else:
                raise e

    @staticmethod
    def std_rolling(a, window, axis=1):
        """用來計算標準差

        Args:
            a (_type_): _description_
            window (_type_): _description_
            axis (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        try:
            max_arr = np.empty(shape=a.shape[0])
            shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
            strides = a.strides + (a.strides[-1],)
            rolling = np.lib.stride_tricks.as_strided(
                a, shape=shape, strides=strides)
            max_arr[window-1:] = np.roll(np.std(rolling, axis=1, ddof=0), 1)
            max_arr[:window] = np.nan
            return max_arr
        except Exception as e:
            if "negative dimensions are not allowed" in str(e):
                return 0
            else:
                print(a, window)
                raise e

    @staticmethod
    def mean_rolling(a, window, axis=1):
        """用來計算平均值

        Args:
            a (_type_): _description_
            window (_type_): _description_
            axis (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        try:
            max_arr = np.empty(shape=a.shape[0])
            shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
            strides = a.strides + (a.strides[-1],)
            rolling = np.lib.stride_tricks.as_strided(
                a, shape=shape, strides=strides)
            max_arr[window-1:] = np.roll(np.mean(rolling, axis=1), 1)
            max_arr[:window] = np.nan
            return max_arr
        except Exception as e:
            if "negative dimensions are not allowed" in str(e):
                return 0
            else:
                raise e

    @staticmethod
    def get_active_max_rolling(prices, window_sizes):
        """
        取得動態最大值
        [nan, nan, 5.0, nan, 6.0, 6.0, 5.0, 8.0, 8.0]
        """
        out_list = np.empty(shape=prices.shape[0])
        last_num = np.nan
        for index, window_size in enumerate(window_sizes):
            if index - window_size < 0:
                target = np.nan
            else:
                target = np.max(prices[index - window_size: index])
            if not np.isnan(last_num):
                if np.isnan(target):
                    out_list[index] = last_num
                else:
                    out_list[index] = target
            else:
                # 如果最後的值還是空值就只好加入進去
                out_list[index] = target
                last_num = target
        return out_list

    @staticmethod
    def get_active_min_rolling(prices, window_sizes):
        """
        取得動態最大值
        [nan, nan, 5.0, nan, 6.0, 6.0, 5.0, 8.0, 8.0]
        """
        out_list = np.empty(shape=prices.shape[0])
        last_num = np.nan
        for index, window_size in enumerate(window_sizes):
            if index - window_size < 0:
                target = np.nan
            else:
                target = np.min(prices[index - window_size: index])
            if not np.isnan(last_num):
                if np.isnan(target):
                    out_list[index] = last_num
                else:
                    out_list[index] = target
            else:
                # 如果最後的值還是空值就只好加入進去
                out_list[index] = target
                last_num = target
        return out_list

    @staticmethod
    def batch_normalize_and_scale(data, batch_size=1000, scale_min=1, scale_max=1000):
        # 初始化一個與原始數據形狀相同的陣列來儲存結果
        result = np.empty_like(data)

        # 對每一個批次進行標準化和縮放
        for i in range(0, len(data), batch_size):
            batch = data[i: i + batch_size]
            batch = np.nan_to_num(batch)
            batch_original = np.max(batch) - np.min(batch)

            if batch_original == 0:
                result[i: i + batch_size] = (scale_min + scale_max) / 2
            else:
                batch_change = scale_max - scale_min
                rescaled = batch_change / batch_original
                new_batch = (batch - np.min(batch)) * rescaled
                new_batch = np.where(new_batch < 1, 1, new_batch)
                result[i: i + batch_size] = new_batch

        return result.astype(int)
