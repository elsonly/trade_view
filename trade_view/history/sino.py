import pytz
from datetime import datetime
from typing import Union, Dict
import shioaji as sj
import pandas as pd
from urllib3 import Retry

from trade_view.setting import SINO
from trade_view.model.sino.quote import Tick, Kbar
from shioaji.contracts import Future, Stock, Option, Index

KBAR_MAPPER = {
    'Amount': 'amount',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume',
    'Open': 'open',
    'High': 'high'
}

TICK_MAPPER = {
    'bid_price': 'bid',
    'ask_volume': 'ask_vol',
    'close': 'close',
    'tick_type': 'tick_type',
    'volume': 'vol',
    'bid_volume': 'bid_vol',
    'ask_price': 'ask',
}

class SinoHistoryHandler:
    RATE_LIMIT = 0.1
    
    def __init__(self, 
    ):
        self.source = 'sino'
        self.markets: Dict[str, Union[Future, Stock, Option, Index]] = {}
        self._api: sj.Shioaji = None
        self._local_tz = pytz.timezone("Asia/Taipei")
        self._connect()
    
    def _get_contracts(self) -> Dict[str, Union[Future, Stock, Option, Index]]:
        contracts = {
            code: contract
            for name, iter_contract in self._api.Contracts
            for code, contract in iter_contract._code2contract.items()
        }
        return contracts
    
    def _connect(self):
        api = sj.Shioaji(simulation=SINO['simulation'])
        accounts = api.login(
            person_id=SINO['id'], 
            passwd=SINO['password'], 
            contracts_timeout=10000,
            subscribe_trade=False
        )
        self._api = api
        # contracts
        self.markets = self._get_contracts()

    def get_contracts(self) -> Dict[str, Union[Future, Stock, Option, Index]]:
        return self.markets

    def get_kbars(self, code:str, start_date:str, end_date:str) -> pd.DataFrame:
        assert code in self.market
        start_date = pd.to_datetime(start_date).strftime("%Y-%m-%d")
        end_date = pd.to_datetime(end_date).strftime("%Y-%m-%d")

        kbars = self._api.kbars(
            contract=self.markets[code],
            start=start_date,
            end=end_date
        )
        df = pd.DataFrame({**kbars})
        df.loc[:, 'ts'] = [
            datetime.fromtimestamp(x/10**9, tz=pytz.UTC).replace(tzinfo=self._local_tz) 
            for x in df.loc[:, 'ts']
        ]
        df.set_index("ts", inplace=True)
        df.rename(KBAR_MAPPER, axis=1, inplace=True)

        return df

    def get_ticks(self, code:str, start_date:str, end_date:str) -> pd.DataFrame:
        assert code in self.market
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        code = '2330'
        start_date = '2022-03-22'
        end_date = '2022-03-23'

        df_list = []

        while start_date < end_date:        
            ticks = self._api.ticks(
                contract=self.markets[code],
                date=start_date.strftime("%Y-%m-%d"),
            )
            df = pd.DataFrame({**ticks})
            df.loc[:, 'ts'] = [
                datetime.fromtimestamp(x/10**9, tz=pytz.UTC).replace(tzinfo=self._local_tz) 
                for x in df.loc[:, 'ts']
            ]
            df.columns
            df.set_index("ts", inplace=True)
            df.rename(TICK_MAPPER, axis=1, inplace=True)
            df_list.append(df)
            
            start_date += pd.offsets.BDay()

        return pd.concat(df_list, axis=0)
        