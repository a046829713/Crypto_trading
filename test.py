from Major.DataProvider import DataProvider


DataProvider().reload_all_data(time_type='1m',symbol_type ='FUTURES')


from utils.BackUp import DatabaseBackupRestore


DatabaseBackupRestore().export_all_tables()