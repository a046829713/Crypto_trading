import vectorbt as vbt
from datetime import datetime
import matplotlib.pyplot as plt
start = '2019-03-01 UTC'  # crypto is in UTC
end = '2019-09-01 UTC'
cols = ['Open', 'High', 'Low', 'Close', 'Volume']
ohlcv = vbt.YFData.download("BTC-USD", start=start, end=end).get(cols)
ohlcv.vbt.ohlcv.plot()

plt.show()