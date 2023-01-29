import pandas as pd


df1 = pd.read_csv("db_df.csv")
df1.drop(columns=['Unnamed: 0'], inplace=True)
df1['Datetime'] = pd.to_datetime(df1['Datetime'])

df1.astype(float)
print(df1)

df2 = pd.read_csv("each_df.csv")
df2.drop(columns=['Unnamed: 0'], inplace=True)
df2['Datetime'] = pd.to_datetime(df2['Datetime'])






print(df2)


merge_df = pd.concat([df1, df2])
print(merge_df)