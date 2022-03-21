import pandas as pd

from trade_view.database import DataBase
from trade_view.database.influxdb import InfluxDB

class DataManager:
    def __init__(self,
        database: DataBase
    ):
        self.database = database
        if database == DataBase.InfluxDB:
            self._cli = InfluxDB()
        else:
            raise Exception(f"Unimplemented database: {database}")
        
    def save_dataframe_quote(self, 
        source: str,
        table:str,
        df: pd.DataFrame,
    ):
        if self.database == DataBase.InfluxDB:
            if source == 'sino':
                self._cli.write_batch(
                    bucket='sino_quotes',
                    measurement_name=table,
                    df=df,
                    tag_columns=['code'],#, 'sec_type'
                )