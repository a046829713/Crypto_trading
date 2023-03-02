class AppSetting():
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_setting():
        data = {"Quantify_systeam": {

            "online": {
                "Attributes": {"AVAXUSDT-15K-OB": {'symbol': 'AVAXUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "COMPUSDT-15K-OB": {'symbol': 'COMPUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "SOLUSDT-15K-OB": {'symbol': 'SOLUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "AAVEUSDT-15K-OB": {'symbol': 'AAVEUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "DEFIUSDT-15K-OB": {'symbol': 'DEFIUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               },

                "parameter":  {
                    "AVAXUSDT-15K-OB": {'highest_n1': 570, 'lowest_n2': 370, 'ATR_short1': 100.0, 'ATR_long2': 190.0},
                    "COMPUSDT-15K-OB": {'highest_n1': 670, 'lowest_n2': 130, 'ATR_short1': 160.0, 'ATR_long2': 60.0},
                    "SOLUSDT-15K-OB": {'highest_n1': 490, 'lowest_n2': 290, 'ATR_short1': 100.0, 'ATR_long2': 60.0},
                    "AAVEUSDT-15K-OB": {'highest_n1': 730, 'lowest_n2': 490, 'ATR_short1': 170.0, 'ATR_long2': 150.0},
                    "DEFIUSDT-15K-OB": {'highest_n1': 90, 'lowest_n2': 490, 'ATR_short1': 70.0, 'ATR_long2': 180.0},
                }
            },
            "history": {
                "Attributes": {"AVAXUSDT-15K-OB": {'symbol': 'AVAXUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "COMPUSDT-15K-OB": {'symbol': 'COMPUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "SOLUSDT-15K-OB": {'symbol': 'SOLUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "AAVEUSDT-15K-OB": {'symbol': 'AAVEUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               "DEFIUSDT-15K-OB": {'symbol': 'DEFIUSDT', 'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025, "lookback_date": '2020-01-01'},
                               },

                "parameter": {
                    "AVAXUSDT-15K-OB": {'highest_n1': 570, 'lowest_n2': 370, 'ATR_short1': 100.0, 'ATR_long2': 190.0},
                    "COMPUSDT-15K-OB": {'highest_n1': 670, 'lowest_n2': 130, 'ATR_short1': 160.0, 'ATR_long2': 60.0},
                    "SOLUSDT-15K-OB": {'highest_n1': 490, 'lowest_n2': 290, 'ATR_short1': 100.0, 'ATR_long2': 60.0},
                    "AAVEUSDT-15K-OB": {'highest_n1': 730, 'lowest_n2': 490, 'ATR_short1': 170.0, 'ATR_long2': 150.0},
                    "DEFIUSDT-15K-OB": {'highest_n1': 90, 'lowest_n2': 490, 'ATR_short1': 70.0, 'ATR_long2': 180.0},
                }

            },
            "sharemode": {
                "Attributes": {"SHARE-15K-OB": {'freq_time': 15, "size": 1.0, "fee": 0.002, "slippage": 0.0025},

                               },

            }

        },
        }

        return data
