from numba import njit
import numpy as np
from typing import Sequence
from datetime import datetime
from Count.Base import vecbot_count
from numpy.lib.stride_tricks import sliding_window_view


@njit
def get_new_marketpostion_array(Length, high_array, low_array, close_array, ATR_short, ATR_long, parameter_1, parameter_2):
    # 資料產生區
    highest_price = Highest(
        high_array, step=parameter_1)

    lowest_price = Lowest(
        low_array, step=parameter_2)

    print(np.where((high_array - highest_price > 0)
          & (ATR_short - ATR_long > 0), 1, 0))
    # # ==============================================================
    # # 主邏輯區段
    # if High > highest_price[i] and ATR_short[i] > ATR_long[i]:
    #     marketpostion = 1
    # if Low < lowest_price[i]:
    #     marketpostion = 0
    # # ==============================================================
    # marketpostion_array[i] = marketpostion


@njit
def get_marketpostion_array(Length, high_array, low_array, close_array, ATR_short, ATR_long, parameter_1, parameter_2):
    # 資料產生區
    highest_price = Highest(
        high_array, step=parameter_1)

    lowest_price = Lowest(
        low_array, step=parameter_2)

    marketpostion_array = np.empty(shape=Length)
    marketpostion = 0
    for i in range(Length):
        High = high_array[i]
        Low = low_array[i]
        Close = close_array[i]
        # ==============================================================
        # 主邏輯區段
        if High > highest_price[i] and ATR_short[i] > ATR_long[i]:
            marketpostion = 1
        if Low < lowest_price[i]:
            marketpostion = 0
        # ==============================================================
        marketpostion_array[i] = marketpostion

    return marketpostion_array


@njit
def get_ATR(Length, high_array: np.array, low_array: np.array, close_array: np.array, parameter_timeperiod):
    """直接手寫ATR 希望可以加快速度(有判斷過不可視未來)

    Args:
        high_array (np.array): _description_
        low_array (np.array): _description_
        close_array (np.array): _description_
        parameter (_type_): _description_

    Returns:
        _type_: _description_
    """
    ATR_array = np.empty(shape=Length)
    TR_array = np.empty(shape=Length)

    for i in range(Length):
        High = high_array[i]
        Low = low_array[i]
        Close = close_array[i]

        if i > 0:
            last_close = close_array[i - 1]
        else:
            last_close = 0

        TR = max(Close - Low, abs(High - last_close),
                 abs(Low - last_close))

        TR_array[i] = TR

        if i < parameter_timeperiod:
            ATR_array[i] = np.nan
        else:
            ATR_array[i] = np.sum(
                TR_array[i - parameter_timeperiod:i]) / parameter_timeperiod

    return ATR_array


@njit
def get_drawdown_per(ClosedPostionprofit: np.ndarray):
    DD_per_array = np.empty(shape=ClosedPostionprofit.shape[0])
    max_profit = 0
    for i in range(ClosedPostionprofit.shape[0]):
        if ClosedPostionprofit[i] > max_profit:
            max_profit = ClosedPostionprofit[i]
            DD_per_array[i] = 0
        else:
            DD_per_array[i] = 100 * (ClosedPostionprofit[i] -
                                     max_profit) / max_profit
    return DD_per_array


@njit
def get_drawdown(ClosedPostionprofit: np.ndarray):
    DD_array = np.empty(shape=ClosedPostionprofit.shape[0])
    max_profit = 0
    for i in range(ClosedPostionprofit.shape[0]):
        if ClosedPostionprofit[i] > max_profit:
            max_profit = ClosedPostionprofit[i]
            DD_array[i] = 0
        else:
            DD_array[i] = (ClosedPostionprofit[i] - max_profit)
    return DD_array


@njit
def get_entryprice(entryprice, Close, marketpostion, last_marketpostion, slippage=None, direction=None):
    if marketpostion == 1 and last_marketpostion == 0:
        if slippage:
            entryprice = Close * (1 + slippage)
        else:
            entryprice = Close
    elif marketpostion == 0:
        entryprice = 0
    return entryprice


@njit
def get_exitsprice(exitsprice, Close, marketpostion, last_marketpostion, slippage=None, direction=None):
    """
    exitsprice (有2種連貫性的設定)
    決定採用2

    1.給予每一個array 出場價 (方便未來可以運用和計算)
    2.只判斷在沒有部位時候的出價格 並且加入滑價

    attetion : 滑價設定要往不利的方向 以免錯估
    Args:
        exitsprice (_type_): _description_
        Close (_type_): _description_
        marketpostion (_type_): _description_
        last_marketpostion (_type_): _description_
        slippage (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if direction == 'buyonly':
        if marketpostion == 0 and last_marketpostion == 1:
            if slippage:
                exitsprice = Close * (1 - slippage)
            else:
                exitsprice = Close
        elif marketpostion == 1:
            exitsprice = 0
    return exitsprice


@njit
def get_buy_Fees(buy_Fee, fee, size, Close, marketpostion, last_marketpostion):
    if marketpostion == 1 and last_marketpostion == 0:
        buy_Fee = Close * fee * size
    elif marketpostion == 0:
        buy_Fee = 0
    return buy_Fee


@njit
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


@njit
def get_OpenPostionprofit(OpenPostionprofit, marketpostion, last_marketpostion, buy_Fees, Close, buy_sizes, entryprice):
    if marketpostion == 1:
        OpenPostionprofit = Close * buy_sizes - entryprice * buy_sizes
    else:
        OpenPostionprofit = 0
    return OpenPostionprofit


@njit
def get_ClosedPostionprofit(ClosedPostionprofit, marketpostion, last_marketpostion, buy_Fees, sell_Fees, Close, sizes, last_entryprice, exitsprice):
    # 我的定義是當部位改變的時候再紀錄
    if marketpostion == 1 and last_marketpostion == 0:
        ClosedPostionprofit = ClosedPostionprofit - buy_Fees
    elif marketpostion == 0 and last_marketpostion == 1:
        ClosedPostionprofit = ClosedPostionprofit - sell_Fees
        # 當部位為平倉後 計算交易損益
        # =====================================================================
        # 注意這邊應該是會以開盤價做平倉?
        # 思考方向是 因為當收盤價結束時才會判斷 是否需要賣出 當需要賣出的時候 以收盤價 當作出場價
        # 是否需要考量賣出時的滑價
        ClosedPostionprofit = ClosedPostionprofit + \
            (exitsprice * sizes - last_entryprice * sizes)
        # =====================================================================
    return ClosedPostionprofit


@njit
def get_profit(profit, marketpostion, last_marketpostion, Close, sell_sizes, last_entryprice):
    if marketpostion == 0 and last_marketpostion == 1:
        profit = Close * sell_sizes - last_entryprice * sell_sizes
    else:
        profit = 0
    return profit


@njit
def Highest(data_array: np.ndarray, step: int) -> np.ndarray:
    """取得rolling的滾動值 和官方的不一樣,並且完成不可視的未來

    Args:
        data_array (np.ndarray): original data like "Open" "High"
        step (int): to window

    Returns:
        np.ndarray: _description_
    """
    high_array = np.empty(shape=data_array.shape[0])
    # 由前向後滾動
    for i in range(0, data_array.shape[0]):
        if i < step:
            high_array[i] = np.nan
            continue
        else:
            high_array[i] = np.max(data_array[i-step:i])
    return high_array

@njit
def Lowest(data_array: np.ndarray, step: int) -> np.ndarray:
    """取得rolling的滾動值 和官方的不一樣,並且完成不可視的未來

    Args:
        data_array (np.ndarray): original data like "Open" "High"
        step (int): to window

    Returns:
        np.ndarray: _description_
    """
    low_array = np.empty(shape=data_array.shape[0])
    # 由前向後滾動
    for i in range(0, data_array.shape[0]):
        if i < step:
            low_array[i] = np.nan
            continue
        else:
            low_array[i] = np.min(data_array[i-step:i])
    return low_array


@njit
def get_order(marketpostion: np.array) -> np.array:
    order_array = np.empty(shape=marketpostion.shape[0])
    for i in range(len(marketpostion)):
        if i > 0:
            # 用來比較轉換的時候
            # 狀態一樣不需要改變
            if marketpostion[i] == marketpostion[i-1]:
                order_array[i] = 0

            # 當狀態不一樣的時候
            if marketpostion[i] != marketpostion[i-1]:
                if marketpostion[i] == 1:
                    order_array[i] = 1
                else:
                    order_array[i] = -1
        else:
            order_array[i] = marketpostion[i]
    return order_array


@njit
def more_fast_logic_order(
        marketpostion_array: np.ndarray,
        close_array: np.ndarray,
        Length: int,
        init_cash: float,
        slippage: float,
        size: float,
        fee: float,
):

    # 初始化資料
    ClosedPostionprofit_array = np.empty(shape=Length)

    # 此變數區列可以在迭代當中改變
    marketpostion = 0  # 部位方向
    entryprice = 0  # 入場價格
    exitsprice = 0  # 出場價格
    buy_Fees = 0  # 買方手續費
    sell_Fees = 0  # 賣方手續費
    ClosedPostionprofit = init_cash   # 已平倉損益
    buy_sizes = size  # 買進部位大小
    sell_sizes = size  # 賣出進部位大小

    # 商品固定屬性
    slippage = slippage  # 滑價計算
    fee = fee  # 手續費率
    direction = "buyonly"

    # 取得訂單
    orders = get_order(marketpostion_array)
    # 主循環區域
    for i in range(Length):
        Close = close_array[i]

        # 策略所產生之資訊
        last_marketpostion = marketpostion
        last_entryprice = entryprice
        # ==============================================================
        # 主邏輯區段
        marketpostion = marketpostion_array[i]

        # 加速寫法
        if orders[i] == 0:
            ClosedPostionprofit_array[i] = ClosedPostionprofit
            continue
        # ==============================================================
        # 計算當前入場價(並且記錄滑價)
        entryprice = get_entryprice(
            entryprice, Close, marketpostion, last_marketpostion, slippage, direction)

        # 計算當前出場價(並且記錄滑價)
        exitsprice = get_exitsprice(
            exitsprice, Close, marketpostion, last_marketpostion, slippage, direction)

        # 計算入場手續費
        buy_Fees = get_buy_Fees(
            buy_Fees, fee, buy_sizes, Close, marketpostion, last_marketpostion)

        # 計算出場手續費
        sell_Fees = get_sell_Fees(
            sell_Fees, fee, sell_sizes, Close, marketpostion, last_marketpostion)

        # 計算已平倉損益(累積式) # v:20221213
        ClosedPostionprofit = get_ClosedPostionprofit(
            ClosedPostionprofit, marketpostion, last_marketpostion, buy_Fees, sell_Fees, Close, sell_sizes, last_entryprice, exitsprice)

        # 記錄保存位置
        ClosedPostionprofit_array[i] = ClosedPostionprofit

    return orders, ClosedPostionprofit_array


@njit
def logic_order(
        marketpostion_array: np.ndarray,
        high_array: np.ndarray,
        low_array: np.ndarray,
        close_array: np.ndarray,
        Length: int,
        init_cash: float,
        slippage: float,
        size: float,
        fee: float,
):
    """
        撰寫邏輯的演算法
        init_cash = init_cash  # 起始資金
        exitsprice (設計時認為應該要添加滑價)

    """
    # 初始化資料
    entryprice_array = np.empty(shape=Length)
    buy_Fees_array = np.empty(shape=Length)
    sell_Fees_array = np.empty(shape=Length)
    OpenPostionprofit_array = np.empty(shape=Length)
    ClosedPostionprofit_array = np.empty(shape=Length)
    profit_array = np.empty(shape=Length)
    Gross_profit_array = np.empty(shape=Length)
    Gross_loss_array = np.empty(shape=Length)
    all_Fees_array = np.empty(shape=Length)
    netprofit_array = np.empty(shape=Length)
    # exitsprice_array = np.empty(shape=Length)

    # 此變數區列可以在迭代當中改變
    marketpostion = 0  # 部位方向
    entryprice = 0  # 入場價格
    exitsprice = 0  # 出場價格
    buy_Fees = 0  # 買方手續費
    sell_Fees = 0  # 賣方手續費
    all_Fees = 0  # 累積手續費
    Gross_profit = 0  # 毛利
    Gross_loss = 0  # 毛損
    OpenPostionprofit = 0  # 未平倉損益(非累積式純計算有多單時)
    ClosedPostionprofit = init_cash   # 已平倉損益
    profit = 0  # 計算已平倉損益(非累積式純計算無單時)
    netprofit = 0  # 淨利
    buy_sizes = size  # 買進部位大小
    sell_sizes = size  # 賣出進部位大小

    # 商品固定屬性
    slippage = slippage  # 滑價計算
    fee = fee  # 手續費率
    direction = "buyonly"
    # 主循環區域
    for i in range(Length):
        Close = close_array[i]

        # 策略所產生之資訊
        last_marketpostion = marketpostion
        last_entryprice = entryprice
        # ==============================================================
        # 主邏輯區段
        marketpostion = marketpostion_array[i]
        # ==============================================================
        # 計算當前賣出進部位大小 (由於賣出部位是買入給的 要先判斷賣出)
        if marketpostion == 0 and last_marketpostion == 1:
            sell_sizes = buy_sizes
        elif marketpostion == 1:
            sell_sizes = 0

        # 計算當前買進部位大小
        if marketpostion == 1 and last_marketpostion == 0:
            # buy_sizes = init_cash / Close
            buy_sizes = 1
        elif marketpostion == 0:
            buy_sizes = 0

        # 計算當前入場價(並且記錄滑價)
        entryprice = get_entryprice(
            entryprice, Close, marketpostion, last_marketpostion, slippage, direction)

        # 計算當前出場價(並且記錄滑價)
        exitsprice = get_exitsprice(
            exitsprice, Close, marketpostion, last_marketpostion, slippage, direction)

        # 計算入場手續費
        buy_Fees = get_buy_Fees(
            buy_Fees, fee, buy_sizes, Close, marketpostion, last_marketpostion)

        # 計算出場手續費
        sell_Fees = get_sell_Fees(
            sell_Fees, fee, sell_sizes, Close, marketpostion, last_marketpostion)

        # 未平倉損益(不包含手續費用)
        OpenPostionprofit = get_OpenPostionprofit(
            OpenPostionprofit, marketpostion, last_marketpostion, buy_Fees, Close, buy_sizes, entryprice)

        # 計算已平倉損益(累積式) # v:20221213
        ClosedPostionprofit = get_ClosedPostionprofit(
            ClosedPostionprofit, marketpostion, last_marketpostion, buy_Fees, sell_Fees, Close, sell_sizes, last_entryprice, exitsprice)

        # 計算已平倉損益(非累積式純計算無單時)
        profit = get_profit(
            profit, marketpostion, last_marketpostion, Close, sell_sizes, last_entryprice)

        # Gross_profit (毛利)
        if profit > 0:
            Gross_profit = Gross_profit + profit

        # Gross_loss(毛損)
        if profit < 0:
            Gross_loss = Gross_loss + profit

        # 累積手續費
        if marketpostion == 1 and last_marketpostion == 0:
            all_Fees = all_Fees + buy_Fees
        elif marketpostion == 0 and last_marketpostion == 1:
            all_Fees = all_Fees + sell_Fees

        # 計算當下淨利(類似權益數) 起始資金 - 買入手續費 - 賣出手續費 + 毛利 + 毛損 + 未平倉損益
        netprofit = init_cash - all_Fees + Gross_profit + Gross_loss + OpenPostionprofit

        # 記錄保存位置
        entryprice_array[i] = entryprice
        buy_Fees_array[i] = buy_Fees
        sell_Fees_array[i] = sell_Fees
        OpenPostionprofit_array[i] = OpenPostionprofit
        ClosedPostionprofit_array[i] = ClosedPostionprofit
        profit_array[i] = profit
        Gross_profit_array[i] = Gross_profit
        Gross_loss_array[i] = Gross_loss
        all_Fees_array[i] = all_Fees
        netprofit_array[i] = netprofit

    orders = np.array(get_order(marketpostion_array))

    return orders, entryprice_array, buy_Fees_array, sell_Fees_array, OpenPostionprofit_array, ClosedPostionprofit_array, profit_array, Gross_profit_array, Gross_loss_array, all_Fees_array, netprofit_array
