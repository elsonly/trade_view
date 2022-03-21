import time
from typing import List, Callable, Set, Union, Dict
import shioaji as sj
from collections import deque, defaultdict
import pandas as pd
from loguru import logger
from threading import Lock
import ciso8601

from trade_view.setting import SINO
from trade_view.model.sino.quote import Tick, OrderBook, OrderBookFlattened
from trade_view.utils import get_quote_channel
from shioaji.contracts import Contract, Future, Stock, Option, Index



def process_tick_ind_v0(quote: dict) -> Tick:
    """
        {
            'Amount': 0.0, 
            'AmountSum': 0.0, 
            'Close': 13368.9, 
            'Cnt': 0, 
            'Code': '099', 
            'Date': '', 
            'DiffPrice': 13368.9, 
            'DiffRate': 0.0, 
            'DiffType': 2, 
            'High': 13371.51, 
            'Low': 13005.16, 
            'Open': 13005.16, 
            'Time': '12:19:30.000000', 
            'VolSum': 0, 
            'Volume': 0
        }
    """
    if quote['Date'] == '':
        date = time.strftime('%Y-%m-%d')
    else:
        date = quote['Date'].replace('/', '-')
    
    dt_str = date + 'T' + quote['Time'] + "+08:00"

    return Tick(
        code = quote['Code'],
        dt=dt_str,
        open = quote['Open'],
        high = quote['High'],
        low = quote['Low'],
        price = quote['Close'],
        amt = quote['Amount'],
        tot_amt = quote['AmountSum'],
        vol = quote['Volume'],
        tot_vol = quote['VolSum'],
        tick_type = None,
        sim_trade = 0
    )

def process_tick(in_tick: Union[sj.TickSTKv1, sj.TickFOPv1]) -> Tick:
    """
        Tick(
            code = 'TXFG1', 
            datetime = datetime.datetime(2021, 7, 1, 10, 42, 29, 757000), 
            open = Decimal('17678'), 
            underlying_price = Decimal('17849.57'), 
            bid_side_total_vol= 32210, 
            ask_side_total_vol= 33218, 
            avg_price = Decimal('17704.663999'), 
            close = Decimal('17753'), 
            high = Decimal('17774'), 
            low = Decimal('17655'), 
            amount = Decimal('17753'), 
            total_amount = Decimal('913790823'), 
            volume = 1, 
            total_volume = 51613, 
            tick_type = 0, 
            chg_type = 2, 
            price_chg = Decimal('41'), 
            pct_chg = Decimal('0.231481'), 
            simtrade = 0
        )
    """
    if isinstance(in_tick, sj.TickSTKv1):
        suspend = bool(in_tick.suspend)
    else:
        suspend = None

    tick = Tick(
        code=in_tick.code,
        datetime=in_tick.datetime.isoformat() + "+08:00",
        open=float(in_tick.open),
        high=float(in_tick.high),
        low=float(in_tick.low),
        close=float(in_tick.close),
        amount=float(in_tick.amount),
        total_amount=float(in_tick.total_amount),
        volume=in_tick.volume,
        total_volume=in_tick.total_volume,
        tick_type=in_tick.tick_type,
        suspend=suspend,
        sim_trade=bool(in_tick.simtrade)
    )
    return tick

def process_orderbook(in_bidask: Union[sj.BidAskSTKv1, sj.BidAskFOPv1]) -> OrderBookFlattened:
    """
        BidAsk(
            code = '2330', 
            datetime = datetime.datetime(2021, 7, 1, 9, 9, 54, 36828), 
            bid_price = [Decimal('593'), Decimal('592'), Decimal('591'), Decimal('590'), Decimal('589')], 
            bid_volume = [248, 180, 258, 267, 163], 
            diff_bid_vol = [3, 0, 0, 0, 0], 
            ask_price = [Decimal('594'), Decimal('595'), Decimal('596'), Decimal('597'), Decimal('598')], 
            ask_volume = [1457, 531, 506, 90, 259], 
            diff_ask_vol = [0, 0, 0, 0, 0], 
            suspend = 0, 
            simtrade = 0,
            intraday_odd = 0
        )
    """
    
    if isinstance(in_bidask, sj.BidAskSTKv1):
        suspend = bool(in_bidask.suspend)
    else:
        suspend = False
    
    orderbook = OrderBookFlattened(
        code=in_bidask.code,
        datetime=in_bidask.datetime.isoformat() + "+08:00",
        bid1=float(in_bidask.bid_price[0]),
        bid2=float(in_bidask.bid_price[1]),
        bid3=float(in_bidask.bid_price[2]),
        bid4=float(in_bidask.bid_price[3]),
        bid5=float(in_bidask.bid_price[4]),
        bid1_vol=in_bidask.bid_volume[0],
        bid2_vol=in_bidask.bid_volume[1],
        bid3_vol=in_bidask.bid_volume[2],
        bid4_vol=in_bidask.bid_volume[3],
        bid5_vol=in_bidask.bid_volume[4],
        ask1=float(in_bidask.ask_price[0]),
        ask2=float(in_bidask.ask_price[1]),
        ask3=float(in_bidask.ask_price[2]),
        ask4=float(in_bidask.ask_price[3]),
        ask5=float(in_bidask.ask_price[4]),
        ask1_vol=in_bidask.ask_volume[0],
        ask2_vol=in_bidask.ask_volume[1],
        ask3_vol=in_bidask.ask_volume[2],
        ask4_vol=in_bidask.ask_volume[3],
        ask5_vol=in_bidask.ask_volume[4],
        suspend=suspend,
        sim_trade=bool(in_bidask.simtrade)
    )
    return orderbook


class SinoQuote:
    def __init__(self, 
        enable_publish:bool,
        pub_func:Callable[[bytes, dict], None],
    ):
        self.source = 'sino'
        self.enable_publish = enable_publish
        self._pub_func = pub_func
        self.markets: Dict[str, Union[Future, Stock, Option, Index]] = {}
        self._api: sj.Shioaji = None
        self._reset_data()
    
    def _reset_data(self) -> None:
        self._subscribed_codes: Dict[str, Set[str]] = defaultdict(set)
        self._q_ticks = deque()
        self._q_orderbooks = deque()
        self._lock_ticks = Lock()
        self._lock_orderbooks = Lock()
        
    def _get_contracts(self) -> Dict[str, Union[Future, Stock, Option, Index]]:
        contracts = {
            code: contract
            for name, iter_contract in self._api.Contracts
            for code, contract in iter_contract._code2contract.items()
        }
        return contracts
    
    def connect(self):
        logger.info('logging...')
        api = sj.Shioaji(simulation=SINO['simulation'])
        accounts = api.login(
            person_id=SINO['id'], 
            passwd=SINO['password'], 
            contracts_timeout=10000
        )
        logger.info("waiting for contract download...")
        if accounts:
            logger.info("login successfully")
        
        self._api = api

        # contracts
        self.markets = self._get_contracts()

        # callback 
        api.quote.set_event_callback(self._event_callback)
        api.set_order_callback(lambda stat, msg: None)
        api.quote.set_quote_callback(self._quote_callback_v0)
        api.quote.set_on_tick_stk_v1_callback(self._on_tick)
        api.quote.set_on_bidask_stk_v1_callback(self._on_bidask)
        api.quote.set_on_tick_fop_v1_callback(self._on_tick)
        api.quote.set_on_bidask_fop_v1_callback(self._on_bidask)

    def reconnect(self):
        try:
            self._api.logout()
            del self._api
            del self.markets
        except:
            pass
        self.connect()
        self.subscribe(self._subscribed_codes)

    def _event_callback(self,
        resp_code:int, 
        event_code:int, 
        info:str, 
        event:str
    ):
        logger.info(f'Info:{info}| Event: {event}')

    def _on_tick(self,
        exchange: sj.Exchange, 
        quote: Union[sj.TickSTKv1, sj.TickFOPv1]
    ):
        tick = process_tick(quote)
        if self.enable_publish:
            channel = get_quote_channel(
                self.source,
                'tick', 
                tick['code']
            )
            self._pub_func(channel, tick)
        with self._lock_ticks:
            self._q_ticks.append(tick)
    
    def _on_bidask(self, 
        exchange: sj.Exchange, 
        quote: Union[sj.BidAskSTKv1, sj.BidAskFOPv1]
    ):
        orderbook = process_orderbook(quote)
        if self.enable_publish:
            channel = get_quote_channel(
                self.source,
                'orderbook', 
                orderbook['code']
            )
            self._pub_func(channel, orderbook)
        with self._lock_orderbooks:
            self._q_orderbooks.append(orderbook)
    
    def _quote_callback_v0(self, topic: str, quote: dict):
        """only support ind tick"""
        split_topic = topic.split('/')
        if split_topic[-1] != 'ODD':
            code = split_topic[-1]
            odd = 0
        else:
            code = split_topic[-2]
            odd = 1

        # if split_topic[0] == 'QUT':
        #     sec_type = 'stk'
        #     quote_type = 'orderbook'
        # elif split_topic[0] == 'MKT':
        #     sec_type = 'stk'
        #     quote_type = 'tick'
        # elif split_topic[0] == 'L': 
        #     sec_type = 'fut'
        #     quote_type = 'tick'
        # elif split_topic[0] == 'Q':
        #     sec_type = 'fut'
        #     quote_type = 'orderbook'
        if split_topic[0] == 'I':
            sec_type = 'ind'
            quote_type = 'tick'
        elif split_topic[0] == 'O':
            sec_type = 'ind'
            quote_type = 'orderbook'
        else:
            raise Exception(f"invalid quote_type {split_topic[0]}")        
        
        if sec_type == 'ind' and quote_type == 'orderbook':
            quote['code'] = code
            channel = get_quote_channel(
                self.exchange, 
                quote_type, 
                code
            )
            tick = process_tick_ind_v0(quote)
            self._pub_func(channel, tick)
            with self._lock_ticks:
                self._q_ticks.append(tick)

    def _get_quote_version(self, code:str):
        # Index
        if len(code) == 3 and code.startswith('0'):
            return 'v0'
        else:
            return 'v1'
    
    def _quote_type_convert(self, quote_type: str) -> str:
        if quote_type == 'orderbook':
            return 'bidask'
        else:
            return quote_type


    def subscribe(self, quote_types: List[str], codes: List[str]) -> None:
        for _quote_type in quote_types:
            for _code in codes:
                if _code not in self.markets:
                    logger.warning(f"Invalid code: {_code}")
                    continue
                if _code in self._subscribed_codes[_quote_type]:
                    continue
                self._subscribed_codes[_quote_type].add(_code)

                self._api.quote.subscribe(
                    self.markets[_code], 
                    quote_type=self._quote_type_convert(_quote_type),
                    version=self._get_quote_version(_code)
                )
            
    def unsubscribe(self, quote_types: List[str], codes:List[str]) -> None:
        for _quote_type in quote_types:
            for _code in codes:
                if _code not in self.markets:
                    logger.warning(f"Invalid code: {_code}")
                    continue
                if _code not in self._subscribed_codes[_quote_type]:
                    continue
                self._subscribed_codes[_quote_type].remove(_code)

                self._api.quote.unsubscribe(
                    self.markets[_code], 
                    quote_type=self._quote_type_convert(_quote_type),
                    version=self._get_quote_version(_code)
                )
            
    def check_connection(self):
        try:
            data = self._api.snapshots([self.markets['TXFR1']])
            if data:
                return True
            else:
                return False
        except:
            return False

    def get_queue_data(self, quote_type: str) -> pd.DataFrame:
        df = pd.DataFrame()
        if quote_type == 'tick':
            if self._q_ticks:
                with self._lock_ticks:
                    df = pd.DataFrame(self._q_ticks)
                    self._q_ticks.clear()
                df.set_index('datetime', inplace=True)
                df.index = pd.to_datetime(df.index)

        else:
            if self._q_orderbooks:
                with self._lock_orderbooks:
                    df = pd.DataFrame(self._q_orderbooks)
                    self._q_orderbooks.clear()
                df.set_index('datetime', inplace=True)
                df.index = pd.to_datetime(df.index)
        return df