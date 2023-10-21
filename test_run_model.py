from DQN.lib import Backtest


if __name__ == "__main__":
    app = Backtest.Quantify_systeam_DQN(init_cash=20000,formal = False)
    
    # ['BCHUSDT', 'COMPUSDT']
    # ['SOLUSDT', 'BTCUSDT', 'BTCDOMUSDT', 'DEFIUSDT', 'XMRUSDT', 'AAVEUSDT', 'TRBUSDT', 'MKRUSDT']
    # ['MATICUSDT','DOGEUSDT','XRPUSDT','LTCUSDT','AVAXUSDT']
    
    # 'LQTYUSDT', 'BANDUSDT', 'TOMOUSDT', 'RNDRUSDT', 'INJUSDT', 'LINKUSDT', 'ANTUSDT', 'XVSUSDT'
    app.Portfolio_register( ['BTCUSDT'])
    app.Portfolio_start()