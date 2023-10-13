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

    @staticmethod
    def get_UserDeadline():
        data = {
            "48d326d82ea14efc6710e4043722c204ee230b001f0524d1f7b3f37091542136": "2023-12-31",
            "094cb2eaec7a7eb0eb8f7dce3a5e1d082af20e9424ac70413ff79fc47d9dcecb": "2023-10-10"  # UTTER
        }

        return data

    @staticmethod
    def get_version() -> str:
        return '2023-07-02'

    @staticmethod
    def get_emergency_times() -> str:
        return 20

    @staticmethod
    def get_DQN_setting() -> str:
        setting_data = {
            "SAVES_PATH": "saves", # 儲存的路徑
            "LEARNING_RATE": 0.0001,  # optim 的學習率,
            "BARS_COUNT": 20, # 用來準備要取樣的特徵長度,例如:開高低收成交量各取10根K棒
            "VOLUMES_TURNON": True, # 特徵是否要採用成交量
            'BATCH_SIZE' : 32, #  每次要從buffer提取的資料筆數,用來給神經網絡更新權重
            'DEFAULT_COMMISSION_PERC':0.002,  # 手續費用(傭金)(乘上100 類神經網絡會更有反應)(影響reward)
            "DEFAULT_SLIPPAGE": 0.0025, #滑價
            "REWARD_ON_CLOSE" : True, # 結束之後才給獎勵
        }
        return setting_data
