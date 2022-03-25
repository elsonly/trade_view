import pytz
from datetime import datetime
from typing import Union, Dict
import shioaji as sj
import pandas as pd
import time

from trade_view.setting import SINO
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
    RATE_LIMIT = 0.01 # 100 req/1s
    
    def __init__(self, 
    ):
        self.source = 'sino'
        self.contracts: Dict[str, Union[Future, Stock, Option, Index]] = {}
        self._api: sj.Shioaji = None
        self._local_tz = pytz.timezone("Asia/Taipei")
        self._prev_req_ts = 0.0
        self._connect()
    
    def _check_req_limit(self):
        if time.time() - self._prev_req_ts > self.RATE_LIMIT > 0:
            time.sleep(self.RATE_LIMIT)

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
        self.contracts = self._get_contracts()

    def get_markets(self) -> pd.DataFrame:
        df = pd.DataFrame([val.dict() for val in self.contracts.values()])
        df['update_date'] = pd.to_datetime(max(df['update_date'])).replace(
            tzinfo=self._local_tz
        )
        df.set_index('update_date', inplace=True)
        for col, dtype in df.dtypes.iteritems():
            if dtype == 'object':
                cond = pd.isnull(df.loc[:, col])
                df.loc[cond, col] = ""
            elif dtype == 'int64':
                cond = pd.isnull(df.loc[:, col])
                df.loc[cond, col] = 0
            elif dtype == 'float64':
                cond = pd.isnull(df.loc[:, col])
                df.loc[cond, col] = 0.0

        return df

    def get_kbars(self, code:str, start_date:str, end_date:str) -> pd.DataFrame:
        assert code in self.contracts
        start_date = pd.to_datetime(start_date).strftime("%Y-%m-%d")
        end_date = pd.to_datetime(end_date).strftime("%Y-%m-%d")
        
        self._check_req_limit()
        kbars = self._api.kbars(
            contract=self.contracts[code],
            start=start_date,
            end=end_date
        )
        df = pd.DataFrame({**kbars})
        df['code'] = code
        df.loc[:, 'ts'] = [
            datetime.fromtimestamp(
                x/10**9, 
                tz=pytz.UTC
            ).replace(tzinfo=self._local_tz) 
            for x in df.loc[:, 'ts']
        ]
        df.set_index("ts", inplace=True)
        df.rename(KBAR_MAPPER, axis=1, inplace=True)

        return df

    def get_ticks(self, code:str, start_date:str, end_date:str) -> pd.DataFrame:
        assert code in self.contracts
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        df_list = []
        while start_date <= end_date:
            self._check_req_limit()
            ticks = self._api.ticks(
                contract=self.contracts[code],
                date=start_date.strftime("%Y-%m-%d"),
            )
            df = pd.DataFrame({**ticks})
            df['code'] = code
            df.loc[:, 'ts'] = [
                datetime.fromtimestamp(
                    x/10**9, 
                    tz=pytz.UTC
                ).replace(tzinfo=self._local_tz) 
                for x in df.loc[:, 'ts']
            ]
            df.columns
            df.set_index("ts", inplace=True)
            df.rename(TICK_MAPPER, axis=1, inplace=True)
            df_list.append(df)
            
            start_date += pd.offsets.BDay()
        
        if df_list:
            return pd.concat(df_list, axis=0)
        else:
            return pd.DataFrame()
        