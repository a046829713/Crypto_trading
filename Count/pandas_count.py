import pandas as pd


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


class Event_count():
    @staticmethod
    def get_OpenPostionprofit(OpenPostionprofit, marketpostion, last_marketpostion, buy_Fees, Close, buy_sizes, entryprice):
        if marketpostion == 1 and last_marketpostion == 0:
            OpenPostionprofit = - buy_Fees
        elif marketpostion == 1:
            OpenPostionprofit = Close * buy_sizes - entryprice * buy_sizes - buy_Fees
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

    def get_order(marketpostion: list) -> list:
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
