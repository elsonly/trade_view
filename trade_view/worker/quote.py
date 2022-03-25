import time
from typing import List
from loguru import logger

from trade_view.quote import QuoteSource
from trade_view.quote.sino import SinoQuote
from trade_view.database.data_manager import DataManager
from trade_view.database import DataBaseSource
from trade_view.grafana.pusher import GrafanaPusher


class QuoteWorker:
    SUBSCRIBE_LIMIT = 100

    def __init__(self,
        source: QuoteSource,
        enable_publish:bool,
        quote_types: List[str],
        subscribe_codes: List[str],

        enable_save:bool,
        database:str,
        save_interval:float,
    ):
        self.source = source
        self.enable_publish = enable_publish
        self.quote_types = quote_types
        self.subscribe_codes = subscribe_codes
        self.enable_save = enable_save
        self.save_interval = save_interval
        
        if enable_publish:
            self._pusher = GrafanaPusher()
            self._pusher.connect()

        if source == QuoteSource.Sino.value:
            self.quote_cli = SinoQuote(
                enable_publish=enable_publish,
                pub_func=self._pusher.send_dict if enable_publish else print
            )
        if len(subscribe_codes) * len(quote_types) > self.SUBSCRIBE_LIMIT:
            raise Exception(f"number of subscription to subscribe beyond limit: {self.SUBSCRIBE_LIMIT}")

        self._active = False
        self._prev_save_ts = 0.0
        self.dm = DataManager(DataBaseSource(database))

    def run(self):
        self.quote_cli.connect()
        self.quote_cli.subscribe(self.quote_types, self.subscribe_codes)
        
        self._active = True
        while self._active:
            try:
                if time.time() - self._prev_save_ts > self.save_interval:
                    self._prev_save_ts = time.time()
                    for _quote_type in self.quote_types:
                        df = self.quote_cli.get_queue_data(_quote_type)
                        if df.empty:
                            continue
                        
                        if self.enable_save:
                            self.dm.save_dataframe_quote(
                                source=self.source,
                                table=_quote_type,
                                df=df
                            )
                time.sleep(0.000001) # save cpu loading
            except KeyboardInterrupt:
                pass
            except Exception as exc:
                logger.exception(exc)