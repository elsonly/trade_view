import pandas as pd
from typing import List

from trade_view.database import DataBaseSource
from trade_view.database.influxdb import InfluxDB

class DataManager:
    def __init__(self,
        database: DataBaseSource
    ):
        self.database = database
        if database == DataBaseSource.InfluxDB:
            self._cli = InfluxDB()
        else:
            raise Exception(f"Unimplemented database: {database}")
        
    def save_dataframe_quote(self, 
        source: str,
        table:str,
        df: pd.DataFrame,
        index_columns: List[str] = ['code'],
    ):
        if self.database == DataBaseSource.InfluxDB:
            self._cli.write_batch(
                bucket=f'{source}_quotes',
                measurement_name=table,
                df=df,
                tag_columns=index_columns,#, 'sec_type'
            )