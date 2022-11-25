import pandas as pd
import vectorbt as vbt
from itertools import product
from collections.abc import Iterable
import time
import gc
from tqdm import tqdm
from decimal import *
from typing import Optional


class Strategy(object):
    """
    change from finlab_crypto package
        TODO : mk func 

    """

    def __init__(self, **default_parameters):
        """inits strategy."""
        self.filters = {}
        self._default_parameters = default_parameters
        self.set_parameters(default_parameters)

    def __call__(self, func):
        """decorator function

        Args
          func: A function of customized strategy.
        """
        self.func = func
        return self

    def set_parameters(self, variables):
        """set your customized strategy parameters.

        let strategy class use variables dict to set method.

        Args:
          variables: a dict of your customized strategy attributes.

        """

        # remove stop vars
        stop_vars = ['sl_stop', 'tp_stop', 'ts_stop']
        for svar in stop_vars:
            if hasattr(self, svar):
                delattr(self, svar)

        # set defualt variables
        if self._default_parameters:
            for key, val in self._default_parameters.items():
                setattr(self, key, val)

        # set custom variables
        if variables:
            for key, val in variables.items():
                setattr(self, key, val)

    def show_parameters(self):
        parameters = {}
        for key, val in self._default_parameters.items():
            parameters[key] = getattr(self, key)
        print(parameters)

    @staticmethod
    def _enumerate_filters(ohlcv, filters):
        """enumerate filters data.

        process filter dictionary data to prepare for adding filter signals.

        Args:
          ohlcv: a dataframe of your trading target.
          filters: a dict of your customized filter attributes.

        Returns:
          a dict that generate tuple with filter signal dataframe and figures data.
          for example:

        {'mmi': (timeperiod                    20
          timestamp
          2020-11-25 02:00:00+00:00   true
          2020-11-25 03:00:00+00:00   true
          2020-11-25 04:00:00+00:00   true

          [3 rows x 1 columns], {'figures': {'mmi_index': timestamp
            2020-11-25 02:00:00+00:00    0.7
            2020-11-25 03:00:00+00:00    0.7
            2020-11-25 04:00:00+00:00    0.7
            name: close, length: 28597, dtype: float64}})}

        """
        ret = {}
        for fname, f in filters.items():
            # get filter signals and figures
            filter_df, filter_figures = f(ohlcv)
            ret[fname] = (filter_df, filter_figures)
        return ret

    @staticmethod
    def _add_filters(entries, exits, fig_data, filters):
        """add filters in strategy.

        generate entries, exits, fig_data after add filters.

        Args:
          entries: A dataframe of entries point time series.
          exits: A dataframe of exits point time series.
          fig_data: A dict of your customized figure Attributes.
          filters: A dict of _enumerate_filters function return.

        Returns:
          entries: A dataframe of entries point time series after add filter function.
          exits: A dataframe of exits point time series after add filter function.
          fig_data: A dict of tuple with filter signal dataframe and figures data.

        """
        for fname, (filter_df, filter_figures) in filters.items():
            filter_df.columns = filter_df.columns.set_names(
                [fname + '_' + n for n in filter_df.columns.names])
            entries = filter_df.vbt.tile(
                entries.shape[1]).vbt & entries.vbt.repeat(filter_df.shape[1]).vbt
            exits = exits.vbt.repeat(filter_df.shape[1])
            exits.columns = entries.columns

            # merge figures
            if filter_figures is not None:
                if 'figures' in filter_figures:
                    if 'figures' not in fig_data:
                        fig_data['figures'] = {}
                    for name, fig in filter_figures['figures'].items():
                        fig_data['figures'][fname + '_' + name] = fig
                if 'overlaps' in filter_figures:
                    if 'overlaps' not in fig_data:
                        fig_data['overlaps'] = {}
                    for name, fig in filter_figures['overlaps'].items():
                        fig_data['overlaps'][fname + '_' + name] = fig

        return entries, exits, fig_data

    @staticmethod
    def _add_stops(ohlcv, entries, exits, variables):
        """Add early trading stop condition in strategy.

        Args:
          ohlcv: A dataframe of your trading target.
          entries: A dataframe of entry point time series.
          exits: A dataframe of exits point time series.
          variables: A dict of your customized strategy Attributes.

        Returns:
          entries: A dataframe of entries point time series after add stop_early function.
          exits: A dataframe of exits point time series after add stop_early function.

        """
        entries, exits = stop_early(ohlcv, entries, exits, variables)
        entries = entries.squeeze()
        exits = exits.squeeze()
        return entries, exits

    def change_str(self, enumeration_vars: list) -> list:
        out_list = []

        for each_ in enumeration_vars:
            each_ = list(map(str, each_))
            out_list.append(list(map(Decimal, each_)))

        return out_list

    def enumerate_variables(self, variables: dict) -> list:
        """ 將資料改變（配對成每一對）

        Args:
            variables (dict): 
            {'sma1': array([ 20,  30,  40,  50,  60,  70,  80,  90, 100, 110, 120, 130, 140,
        150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270,
        280, 290, 300]), 'sma2': array([ 20,  30,  40,  50,  60,  70,  80,  90, 100, 110, 120, 130, 140,
        150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270,
        280, 290, 300])}

        Returns:
            list: [...{'sma1': 300, 'sma2': 130}, {'sma1': 300, 'sma2': 140}, {'sma1': 300, 'sma2': 150}, {'sma1': 300, 'sma2': 160}, {'sma1': 300, 'sma2': 170}, {'sma1': 300, 'sma2': 180}, {'sma1': 300, 'sma2': 190}, {'sma1': 300, 'sma2': 200}, {'sma1': 300, 'sma2': 210}, {'sma1': 300, 'sma2': 220}, {'sma1': 300, 'sma2': 230}, {'sma1': 300, 'sma2': 240}, {'sma1': 300, 'sma2': 250}, {'sma1': 300, 'sma2': 260}, {'sma1': 300, 'sma2': 270}, {'sma1': 300, 'sma2': 280}, {'sma1': 300, 'sma2': 290}, {'sma1': 300, 'sma2': 300}]
        """
        if not variables:
            return []

        enumeration_name = []
        enumeration_vars = []
        constant_d = {}

        for name, v in variables.items():
            if (isinstance(v, Iterable) and not isinstance(v, str)
                and not isinstance(v, pd.Series)
                    and not isinstance(v, pd.DataFrame)):

                enumeration_name.append(name)
                enumeration_vars.append(v)
            else:
                constant_d[name] = v

        enumeration_vars = self.change_str(enumeration_vars)

        variable_enumerations = []
        for ps in list(product(*enumeration_vars)):
            ps = (tuple(map(float, ps)))
            variable_enumerations.append(
                dict(**dict(zip(enumeration_name, ps)), **constant_d))
        print(variable_enumerations)
        exit()
        return variable_enumerations

    def is_evalable(self, obj):
        try:
            eval(str(obj))
            return True
        except:
            return False

    def remove_pd_object(self, d):
        ret = {}
        for n, v in d.items():
            if ((not isinstance(v, pd.Series) and not isinstance(v, pd.DataFrame) and not callable(v) and self.is_evalable(v))
                    or isinstance(v, str)):
                ret[n] = v
        return ret

    def enumerate_signal(self, ohlcv: pd.DataFrame, variables: list):
        """ 產生訊號的方式

        Args:
            ohlcv (pd.DataFrame): _description_
            strategy (_type_): _description_
            variables (list): _description_

        Returns:
            _type_: _description_
        """
        entries = {}
        exits = {}
        fig = {}

        for each_row in variables:
            # 如果不設定參數 會無法傳遞進去函數
            self.set_parameters(each_row)

            # 從原本策略取的結果
            results = self.func(ohlcv)
            entries[str(each_row)], exits[str(
                each_row)] = results[0], results[1]

            if len(results) >= 3:
                fig = results[2]

        # 將整個字典丟入
        entries = pd.DataFrame(entries)
        exits = pd.DataFrame(exits)

        # setup columns
        param_names = list(eval(entries.columns[0]).keys())

        # eval 將字串還原
        arrays = ([entries.columns.map(lambda s: eval(s)[p])
                  for p in param_names])

        # 將兩者合併在一起
        tuples = list(zip(*arrays))

        if tuples:
            columns = pd.MultiIndex.from_tuples(tuples, names=param_names)
            exits.columns = columns
            entries.columns = columns

        return entries, exits, fig

    def backtest_Hyperparameter_optimization(self, df: pd.DataFrame, variables: dict, batchoperation: int = 500):
        """
            use backtest
                # if 'entries' to large to rasie memory
                    then slicing data

                修正字典記憶體不足 
        """
        variables = variables or dict()
        # 取得所有參數之配對
        variable_enumerates = self.enumerate_variables(variables)

        # 總運算次數
        all_num = divmod(len(variable_enumerates), batchoperation)
        all_num = all_num[0] if all_num[1] == 0 else all_num[0] + 1

        i = 0
        total_returns = []
        for _i in tqdm(range(all_num)):
            variable_batch = variable_enumerates[i:i+batchoperation]
            # args['size'] = vbt.settings.portfolio['init_cash'] / ohlcv_lookback.close[0]
            entries, exits, fig_data = self.enumerate_signal(
                df, variable_batch)

            # entries = pd.DataFrame
            portfolio = vbt.Portfolio.from_signals(
                df['Close'], entries, exits)

            total_returns.append(portfolio.total_return())

            del portfolio
            gc.collect()

            i += batchoperation

        total_return = pd.concat(total_returns)
        print(total_return.max())
        return total_return

    def backtest(self, df: pd.DataFrame, **kwargs):
        """
            一般參數情況 使用內建參數並且於此中此

        Args:
            df (pd): _description_

        """
        print('backtest 回測準備參數', kwargs)
        variable_enumerates = [self._default_parameters]

        entries, exits, fig_data = self.enumerate_signal(
            df, variable_enumerates)

        return vbt.Portfolio.from_signals(
            df['Close'], entries, exits, **kwargs)
