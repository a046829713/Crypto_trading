import pandas as pd
from Count.Base import Event_count


class Strategy_base(object):
    """ 
    取得策略的基本資料及訊息
    Args:
        object (_type_): _description_
    """

    def __init__(self,
                 strategy_name: str,
                 symbol_name: str,
                 freq_time: int,
                 size: float,
                 fee: float,
                 slippage: float,
                 init_cash: float = 10000.0,
                 symobl_type: str = "Futures") -> None:
        """ to get strategy info msg

        Args:
            strategy_name (str): _description_
            symbol_name (int): _description_
                like : BTCUSDT
            freq_time (int): _description_
            fee (float): _description_
            slippage (float): _description_
        """
        self.strategy_name = strategy_name
        self.symbol_name = symbol_name
        self.freq_time = freq_time
        self.size = size
        self.fee = fee
        self.slippage = slippage
        self.init_cash = init_cash
        self.symobl_type = symobl_type
        self.data = self.simulationdata()
        self.datetimes = Event_count.get_index(self.data)
        self.array_data = self.simulationdata('array_data')

    def simulationdata(self, data_type: str = 'event_data'):
        """

        Args:
            data_type (str, optional): _description_. Defaults to 'event_data'.

        Returns:
            _type_: _description_
        """
        if self.symobl_type == 'Futures':
            self.symobl_type = "F"

        df = pd.read_csv(
            f"{self.symbol_name}-{self.symobl_type}-{self.freq_time}-Min.csv")
        df.set_index("Datetime", inplace=True)

        if data_type == 'event_data':
            return df.to_dict("index")
        elif data_type == 'array_data':
            return df.to_numpy()
