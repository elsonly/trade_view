from trade_view.data_manager import DataManager, DataBase


dm = DataManager(DataBase.InfluxDB)
source = 'sino'
table = 'orderbook'
