from DQN.lib import Backtest


if __name__ == "__main__":
    app = Backtest.Quantify_systeam_DQN(init_cash=20000,formal = False)
    
    # ['MATICUSDT','DOGEUSDT','XRPUSDT','LTCUSDT','AVAXUSDT']
    # ['SOLUSDT', 'BTCUSDT', 'BTCDOMUSDT', 'DEFIUSDT', 'XMRUSDT', 'AAVEUSDT', 'TRBUSDT', 'MKRUSDT']
    
    
    # 
    app.Portfolio_register( ['BCHUSDT', 'COMPUSDT'])
    app.Portfolio_start()