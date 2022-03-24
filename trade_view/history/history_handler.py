import pandas as pd
from typing import Dict

from trade_view.history.sino import SinoHistoryHandler
from trade_view.history import HistorySource


class HistoryHandler:
    def __init__(self, 
        source:HistorySource
    ):
        if source == HistorySource.Sino:
            self._handler = SinoHistoryHandler()
        else:
            raise Exception(f"Invalid source {source}")

    def get_markets(self) -> Dict[str, dict]:
        return self._handler.get_markets()

    def get_kbars(self, code:str, start_date:str, end_date:str) -> pd.DataFrame:
        return self._handler.get_kbars(code, start_date, end_date)

    def get_ticks(self, code:str, start_date:str, end_date:str) -> pd.DataFrame:
        return self._handler.get_ticks(code, start_date, end_date)

