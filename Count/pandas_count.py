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