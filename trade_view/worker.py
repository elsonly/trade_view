import time
from typing import List

from trade_view.quote.sino import SinoQuote
from trade_view.data_manager import DataManager


class QuoteWorker:
    def __init__(self,
        source: str,
        enable_publish:bool,
        limit:int,
        quote_types: List[str],
        subscribe_codes: List[str],
        database:str,
        save_interval:float,
    ):
        self.source = source
        self.enable_publish = enable_publish
        self.limit = limit
        self.quote_types = quote_types
        self.subscribe_codes = subscribe_codes
        self.save_interval = save_interval
        
        if source == 'SINO':
            self.quote_cli = SinoQuote(
                enable_publish=enable_publish,
                pub_func=print
            )
        if len(subscribe_codes) > limit:
            raise Exception(f"number of codes to subscribe beyond limit: {limit}")

        self._active = False
        self._prev_save_ts = 0.0
        self.dm = DataManager(database)

    def run(self):
        self.quote_cli.connect()
        self.quote_cli.subscribe(self.quote_types, self.subscribe_codes)
        
        self._active = True
        while self._active:
            if time.time() - self._prev_save_ts > self.save_interval:
                self._prev_save_ts = time.time()
                for _quote_type in self.quote_types:
                    df = self.quote_cli.get_queue_data(_quote_type)
                    self.dm.save_dataframe_quote(
                        source=self.source,
                        table=_quote_type,
                        df=df
                    )
            time.sleep(0.000001) # save cpu loading