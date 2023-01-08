from Database import SQL_operate
# import

SQL = SQL_operate.DB_operate()


df = SQL.read_Dateframe('SELECT * FROM `BTCUSDT-F` where Datetime > "2022-09-26"')
print(df)



