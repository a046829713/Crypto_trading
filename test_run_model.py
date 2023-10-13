from DQN.lib import Backtest


if __name__ == "__main__":
    app = Backtest.Quantify_systeam_DQN(init_cash=20000,formal = False)
    app.Portfolio_register(['BTCUSDT'])
    app.Portfolio_start()