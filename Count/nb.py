from numba import njit
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from utils.TimeCountMsg import TimeCountMsg
from utils.Debug_tool import debug


@njit
def get_marketpostion_array(Length, high_array, low_array, close_array, ATR_short, ATR_long, highest_price, lowest_price):
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
def get_order_array(high_array, low_array, close_array, ATR_short, ATR_long, highest_price, lowest_price):
    # [True, True, True, False, False]
    # [False, False, True, True, True]
    # 0    1.0
    # 1    0.0
    # 2    0.0
    # 3   -1.0
    # 4    0.0
    Entries = np.where((high_array - highest_price > 0) &
                       (ATR_short - ATR_long > 0), 1, 0)
    Exits = np.where((low_array - lowest_price) < 0, 1, 0)

    Entries_cum = np.cumsum(Entries)
    for i in range(high_array.shape[0]):
        print(Entries[i], Exits[i], Entries_cum[i])
    return Entries


@njit
def get_ATR(Length, high_array: np.array, low_array: np.array, close_array: np.array, parameter_timeperiod):
    last_close_array = np.roll(close_array, 1)
    last_close_array[0] = 0

    def moving_average(a, n=3):
        """
            決定平均類別不向後移動
        """
        ret = np.cumsum(a)
        ret[n:] = ret[n:] - ret[:-n]
        ret[:n] = np.nan
        return ret/n

    # maximum 這個要兩兩比較 不然會有問題
    each_num = np.maximum(close_array - low_array,
                          np.abs(high_array - last_close_array))
    TR = np.maximum(each_num, np.abs(low_array - last_close_array))
    ATR = moving_average(TR, parameter_timeperiod)

    return ATR


@njit
def get_drawdown_per(ClosedPostionprofit: np.ndarray, init_cash: float):
    DD_per_array = np.empty(shape=ClosedPostionprofit.shape[0])
    max_profit = init_cash
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
def get_entryprice(entryprice, target_price: float, marketpostion, last_marketpostion, slippage=None, direction=None):
    """
    用來取得入場價格

    Args:
        entryprice (_type_): _description_
        target_price (float): "Close" or "Open" >> any price to link entryprice
        marketpostion (_type_): _description_
        last_marketpostion (_type_): _description_
        slippage (_type_, optional): _description_. Defaults to None.
        direction (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if marketpostion == 1 and last_marketpostion == 0:
        if slippage:
            entryprice = target_price * (1 + slippage)
        else:
            entryprice = target_price
    elif marketpostion == 0:
        entryprice = 0
    return entryprice


@njit
def get_exitsprice(exitsprice, target_price: float, marketpostion, last_marketpostion, slippage=None, direction=None):
    """
    exitsprice (有2種連貫性的設定)
    決定採用2

    1.給予每一個array 出場價 (方便未來可以運用和計算)
    2.只判斷在沒有部位時候的出價格 並且加入滑價

    attetion : 滑價設定要往不利的方向 以免錯估
    Args:
        exitsprice (_type_): _description_
        target_price (float): _description_
        marketpostion (_type_): _description_
        last_marketpostion (_type_): _description_
        slippage (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if direction == 'buyonly':
        if marketpostion == 0 and last_marketpostion == 1:
            if slippage:
                exitsprice = target_price * (1 - slippage)
            else:
                exitsprice = target_price
        elif marketpostion == 1:
            exitsprice = 0
    return exitsprice


@njit
def get_buy_Fees(buy_Fee, fee, size, target_price: float, marketpostion, last_marketpostion):
    """_summary_

    Args:
        buy_Fee (_type_): _description_
        fee (_type_): _description_
        size (_type_): _description_
        target_price (float): "Close" or "Open" >> any price to link entryprice
        marketpostion (_type_): _description_
        last_marketpostion (_type_): _description_

    Returns:
        _type_: _description_
    """
    if marketpostion == 1 and last_marketpostion == 0:
        buy_Fee = target_price * fee * size
    elif marketpostion == 0:
        buy_Fee = 0
    return buy_Fee


@njit
def get_sell_Fees(sell_Fee, fee: float, size, target_price: float, marketpostion, last_marketpostion):
    """_summary_

    Args:
        sell_Fee (_type_): _description_
        fee (float): 原始策略裡的手續費費率
        target_price (float): "Close" or "Open" >> any price to link entryprice
        marketpostion (_type_): _description_
        last_marketpostion (_type_): _description_

    Returns:
        _type_: _description_
    """
    if marketpostion == 0 and last_marketpostion == 1:
        sell_Fee = target_price * fee * size
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
def get_ClosedPostionprofit(ClosedPostionprofit, marketpostion, last_marketpostion, buy_Fees, sell_Fees, sizes, last_entryprice, exitsprice):
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
def get_profit(profit, marketpostion, last_marketpostion, target_price: float, sell_sizes, last_entryprice):
    """_summary_

    Args:
        profit (_type_): _description_
        marketpostion (_type_): _description_
        last_marketpostion (_type_): _description_
        target_price (float): "Close" or "Open" >> any price to link entryprice
        sell_sizes (_type_): _description_
        last_entryprice (_type_): _description_

    Returns:
        _type_: _description_
    """
    if marketpostion == 0 and last_marketpostion == 1:
        profit = target_price * sell_sizes - last_entryprice * sell_sizes
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
    shiftorder: np.ndarray,
    open_array: np.ndarray,
    Length: int,
    init_cash: float,
    slippage: float,
    size: float,
    fee: float,
):

    marketpostion_array = np.full(Length, 0, dtype=np.int_)

    # 此變數區列可以在迭代當中改變
    marketpostion = 0  # 部位方向
    entryprice = 0  # 入場價格
    exitsprice = 0  # 出場價格
    buy_Fees = 0  # 買方手續費
    sell_Fees = 0  # 賣方手續費

    buy_sizes = size  # 買進部位大小
    sell_sizes = size  # 賣出進部位大小

    # 商品固定屬性
    slippage = slippage  # 滑價計算
    fee = fee  # 手續費率
    direction = "buyonly"


    # 主循環區域
    for i in range(Length):
        current_order = shiftorder[i]  # 實際送出訂單位置
        # 主邏輯區段
        if current_order == 1:
            marketpostion = 1
        if current_order == -1:
            marketpostion = 0

        marketpostion_array[i] = marketpostion

    # 計算當前入場價(並且記錄滑價)
    last_marketpostion_arr = np.roll(marketpostion_array, 1)
    last_marketpostion_arr[0] = 0

    entryprice_arr = np.where(
        (marketpostion_array - last_marketpostion_arr > 0), open_array * (1+slippage), 0)

    entryprice_arr = entryprice_arr[np.where(entryprice_arr > 0)]
    # 跳過沒成交的交易
    if entryprice_arr.shape[0] == 0:
        return 0

    exitsprice_arr = np.where(
        (marketpostion_array - last_marketpostion_arr < 0), open_array * (1-slippage), 0)
    exitsprice_arr = exitsprice_arr[np.where(exitsprice_arr > 0)]
    if exitsprice_arr.shape[0] == 0:
        return 0

    # 判斷長度
    entryprice_arr = entryprice_arr[:exitsprice_arr.shape[0]]
    # 取得點數差
    diff_arr = exitsprice_arr - entryprice_arr

    buy_Fees_arr = np.where(
        (marketpostion_array - last_marketpostion_arr > 0), open_array * fee * size, 0)
    buy_Fees_arr = buy_Fees_arr[np.where(buy_Fees_arr > 0)]
    buy_Fees_arr = buy_Fees_arr[:exitsprice_arr.shape[0]]

    sell_Fees_arr = np.where(
        (marketpostion_array - last_marketpostion_arr < 0), open_array * fee * size, 0)
    sell_Fees_arr = sell_Fees_arr[np.where(sell_Fees_arr > 0)]

    ClosedPostionprofit_arr = diff_arr - buy_Fees_arr - sell_Fees_arr

    ClosedPostionprofit_arr = np.cumsum(
        ClosedPostionprofit_arr) + init_cash  # 已平倉損益

    # 指標優化區
    DD_per_array = get_drawdown_per(ClosedPostionprofit_arr, init_cash)
    sumallDD = np.sum(DD_per_array**2)
    ROI = (ClosedPostionprofit_arr[-1] / init_cash)-1

    if ((sumallDD / exitsprice_arr.shape[0])**0.5) == 0:
        ui_ = 0
    else:
        ui_ = (ROI*100) / ((sumallDD / exitsprice_arr.shape[0])**0.5)

    return ui_


@njit
def logic_order(
    shiftorder: np.ndarray,
    open_array: np.ndarray,
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
        傳入參數不可以為None 需要為數值型態 np.nan


        2023.05.20 認為這裡單純的計算 回測報告就好
        因為策略的延伸所造成的不便性太大
    """

    marketpostion_array = np.empty(shape=Length)
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

    # 此變數區列可以在迭代當中改變
    marketpostion = 0  # 部位方向
    entryprice = 0  # 入場價格
    exitsprice = 0  # 出場價格
    buy_Fees = 0  # 買方手續費
    sell_Fees = 0  # 賣方手續費
    OpenPostionprofit = 0  # 未平倉損益(非累積式純計算有多單時)
    ClosedPostionprofit = init_cash   # 已平倉損益
    profit = 0  # 計算已平倉損益(非累積式純計算無單時)
    buy_sizes = size  # 買進部位大小
    sell_sizes = size  # 賣出進部位大小
    Gross_profit = 0  # 毛利
    Gross_loss = 0  # 毛損
    all_Fees = 0  # 累積手續費
    netprofit = 0  # 淨利

    # 商品固定屬性
    slippage = slippage  # 滑價計算
    fee = fee  # 手續費率
    direction = "buyonly"

    # 主循環區域
    for i in range(Length):
        Open = open_array[i]
        current_order = shiftorder[i]  # 實際送出訂單位置(訊號產生)
        last_marketpostion = marketpostion
        last_entryprice = entryprice
        # ==============================================================
        # 部位方向區段
        if current_order == 1:
            marketpostion = 1
        if current_order == -1:
            marketpostion = 0

        marketpostion_array[i] = marketpostion

        # 計算當前入場價(並且記錄滑價)
        entryprice = get_entryprice(
            entryprice, Open, marketpostion, last_marketpostion, slippage, direction)

        # 計算當前出場價(並且記錄滑價)
        exitsprice = get_exitsprice(
            exitsprice, Open, marketpostion, last_marketpostion, slippage, direction)

        # 計算入場手續費
        buy_Fees = get_buy_Fees(
            buy_Fees, fee, buy_sizes, Open, marketpostion, last_marketpostion)

        # 計算出場手續費
        sell_Fees = get_sell_Fees(
            sell_Fees, fee, sell_sizes, Open, marketpostion, last_marketpostion)

        # 未平倉損益(不包含手續費用)
        OpenPostionprofit = get_OpenPostionprofit(
            OpenPostionprofit, marketpostion, last_marketpostion, buy_Fees, Open, buy_sizes, entryprice)

        # 計算已平倉損益(累積式) # v:20221213
        ClosedPostionprofit = get_ClosedPostionprofit(
            ClosedPostionprofit, marketpostion, last_marketpostion, buy_Fees, sell_Fees, sell_sizes, last_entryprice, exitsprice)

        # 計算已平倉損益(非累積式純計算無單時)
        profit = get_profit(
            profit, marketpostion, last_marketpostion, Open, sell_sizes, last_entryprice)

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

    # for i in range(Length):
    #     print("部位:", marketpostion_array[i], "進場價格:", entryprice_array[i],
    #           "買入手續費", buy_Fees_array[i], "賣出手續費:", sell_Fees_array[i])

    neworders = get_order(marketpostion_array)
    return neworders, marketpostion_array, entryprice_array, buy_Fees_array, sell_Fees_array, OpenPostionprofit_array, ClosedPostionprofit_array, profit_array, Gross_profit_array, Gross_loss_array, all_Fees_array, netprofit_array


@njit
def TurtleStrategy(high_array, highestarr, ATR_short, ATR_long, low_array, lowestarr):
    """
        海龜交易法
    """
    trends = np.where((high_array - highestarr > 0) &
                      (ATR_short-ATR_long > 0), 1, 0)
    orders = np.where((low_array - lowestarr) < 0, -1, trends)
    shiftorder = np.roll(orders, 1)
    shiftorder[0] = 0
    return shiftorder


@njit
def TurtleStrategy01(high_array, highestarr, ATR_short, ATR_long, low_array, lowestarr):
    """
        海龜交易法優化01
    """
    trends = np.where((high_array - highestarr > 0) &
                      (ATR_short-ATR_long > 0), 1, 0)
    orders = np.where((low_array - lowestarr) < 0, -1, trends)
    shiftorder = np.roll(orders, 1)
    shiftorder[0] = 0
    return shiftorder


@njit
def VCPStrategy(std_arr: np.array, Volume: np.array, Volume_avgarr: np.array, High: np.array, highestarr: np.array, Low: np.array, lowestarr: np.array, threshold=1.5):
    """
        通道壓縮交易法
    """

    # 判斷波動度是否縮小
    shifted_arr_1 = np.roll(std_arr, 1)
    shifted_arr_1[:1] = np.nan
    shifted_arr_2 = np.roll(std_arr, 2)
    shifted_arr_2[:2] = np.nan
    shifted_arr_3 = np.roll(std_arr, 3)
    shifted_arr_3[:3] = np.nan
    shifted_arr_4 = np.roll(std_arr, 4)
    shifted_arr_4[:4] = np.nan

    vc_pattern = std_arr < shifted_arr_1
    vc_pattern = vc_pattern & (std_arr < shifted_arr_2)
    vc_pattern = vc_pattern & (std_arr < shifted_arr_3)
    vc_pattern = vc_pattern & (std_arr < shifted_arr_4)

    # 判斷成交量是否大於平均值
    vc_pattern = np.where(Volume > Volume_avgarr*threshold, vc_pattern, False)

    trends = np.where((High - highestarr > 0) & vc_pattern, 1, 0)
    orders = np.where((Low - lowestarr) < 0, -1, trends)

    shiftorder = np.roll(orders, 1)
    shiftorder[0] = 0
    return shiftorder



@njit
def DynamicStrategy(high_array: np.array, low_array: np.array, ATR_shortArr: np.array, ATR_longArr: np.array, highestarr: np.array, lowestarr1: np.array, lowestarr2: np.array):
    trends = np.where((high_array - highestarr > 0) & (ATR_shortArr-ATR_longArr > 0), 1, 0)    
    orders = np.where((ATR_shortArr > ATR_longArr) & (low_array < lowestarr1), -1, trends)
    orders = np.where((ATR_shortArr <= ATR_longArr) & (low_array < lowestarr2), -1, orders)    
    shiftorder = np.roll(orders, 1)
    shiftorder[0] = 0
    return shiftorder
