

from Major.DataProvider import DataProvider



for symbol in['BCHUSDT', 'COMPUSDT']:
    DataProvider().get_symboldata(symbol_name=symbol)
# print("state_1d".upper())


# import pandas as pd
# import numpy as np


# df = pd.read_csv(f'DQN\ETHUSDT-F-15-Min.csv')
# df['Datetime'] = pd.to_datetime(df['Datetime'])

# df.set_index('Datetime',inplace=True)
# x1_data = df.index.to_numpy()


# if x1_data.dtype == 'datetime64[ns]':
#     x1_data = [str(date).split('T')[0] for date in x1_data]
    
#     print(x1_data)

# import torch
# import numpy as np

# obs = [1,2,3]
# print(obs)
# print(np.array(obs))
# print(torch.tensor(np.array(obs)))