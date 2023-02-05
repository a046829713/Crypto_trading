class AppSetting():
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_setting():
        data = {"Quantify_systeam": {

            "online": {
                "Attributes": {"AVAXUSDT-15K-OB": {'symbol': 'AVAXUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "ETHUSDT-15K-OB": {'symbol': 'ETHUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "SOLUSDT-15K-OB": {'symbol': 'SOLUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               },

                "parameter": {
                    "AVAXUSDT-15K-OB": {'highest_n1': 570, 'lowest_n2': 370, 'ATR_short1': 100.0, 'ATR_long2': 190.0},
                    "ETHUSDT-15K-OB": {'highest_n1': 570, 'lowest_n2': 470, 'ATR_short1': 50.0, 'ATR_long2': 160.0},
                    "SOLUSDT-15K-OB": {'highest_n1': 490, 'lowest_n2': 290, 'ATR_short1': 100.0, 'ATR_long2': 60.0}
                }
            },
            "history": {
                "Attributes": {"AVAXUSDT-15K-OB": {'symbol': 'AVAXUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "ETHUSDT-15K-OB": {'symbol': 'ETHUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "SOLUSDT-15K-OB": {'symbol': 'SOLUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               },

                "parameter": {
                    "AVAXUSDT-15K-OB": {'highest_n1': 570, 'lowest_n2': 370, 'ATR_short1': 100.0, 'ATR_long2': 190.0},
                    "ETHUSDT-15K-OB": {'highest_n1': 570, 'lowest_n2': 470, 'ATR_short1': 50.0, 'ATR_long2': 160.0},
                    "SOLUSDT-15K-OB": {'highest_n1': 490, 'lowest_n2': 290, 'ATR_short1': 100.0, 'ATR_long2': 60.0}
                }
            }

        },
        }

        return data
