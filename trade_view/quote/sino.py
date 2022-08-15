import time
from typing import List, Callable, Set, Union, Dict
import shioaji as sj
from collections import deque, defaultdict
import pandas as pd
from loguru import logger
from threading import Lock
import ciso8601
from datetime import datetime, timedelta

from trade_view.setting import SINO
from trade_view.model.sino.quote import (
    MarketIndexInfo,
    MarketIndexTick,
    Tick,
    OrderBook,
    OrderBookFlattened,
)
from trade_view.utils import get_quote_channel
from shioaji.contracts import Contract, Future, Stock, Option, Index


def process_market_bidask(in_bidask: dict, date: str) -> MarketIndexInfo:
    """
    O/TSE/001
    {
        "Market": 1,
        "Time": 100315,
        "af_buy_cnt": 0,
        "af_buy_vol": 0,
        "af_down_buy_cnt": 0,
        "af_down_buy_vol": 0,
        "af_down_sell_cnt": 0,
        "af_down_sell_vol": 0,
        "af_sell_cnt": 0,
        "af_sell_vol": 0,
        "af_up_buy_cnt": 0,
        "af_up_buy_vol": 0,
        "af_up_sell_cnt": 0,
        "af_up_sell_vol": 0,
        "bf_buy_cnt": 4908501,
        "bf_buy_vol": 34001172,
        "bf_sell_cnt": 4935374,
        "bf_sell_vol": 24612921,
        "bwt_buy_cnt": 2927340,
        "bwt_buy_vol": 27164160,
        "bwt_down_buy_cnt": 19658,
        "bwt_down_buy_vol": 1336723,
        "bwt_down_sell_cnt": 345,
        "bwt_down_sell_vol": 34375,
        "bwt_sell_cnt": 3095154,
        "bwt_sell_vol": 18583987,
        "bwt_up_buy_cnt": 9,
        "bwt_up_buy_vol": 206,
        "bwt_up_sell_cnt": 371,
        "bwt_up_sell_vol": 13136,
        "es_buy_cnt": 14403,
        "es_buy_vol": 20236652,
        "es_sell_cnt": 12522,
        "es_sell_vol": 27378367,
        "etf_buy_cnt": 482926,
        "etf_buy_vol": 700556,
        "etf_down_buy_cnt": 2042,
        "etf_down_buy_vol": 50416,
        "etf_down_sell_cnt": 25,
        "etf_down_sell_vol": 140,
        "etf_sell_cnt": 401542,
        "etf_sell_vol": 583279,
        "etf_up_buy_cnt": 61,
        "etf_up_buy_vol": 118,
        "etf_up_sell_cnt": 214,
        "etf_up_sell_vol": 1266,
        "stk_buy_cnt": 1140792,
        "stk_buy_vol": 2656830,
        "stk_down_buy_cnt": 19400,
        "stk_down_buy_vol": 39127,
        "stk_down_sell_cnt": 14754,
        "stk_down_sell_vol": 70790,
        "stk_sell_cnt": 1077601,
        "stk_sell_vol": 3273639,
        "stk_up_buy_cnt": 13913,
        "stk_up_buy_vol": 43164,
        "stk_up_sell_cnt": 55377,
        "stk_up_sell_vol": 215423,
        "swt_buy_cnt": 345913,
        "swt_buy_vol": 3441870,
        "swt_down_buy_cnt": 2190,
        "swt_down_buy_vol": 163649,
        "swt_down_sell_cnt": 19,
        "swt_down_sell_vol": 962,
        "swt_sell_cnt": 349780,
        "swt_sell_vol": 2133440,
        "swt_up_buy_cnt": 0,
        "swt_up_buy_vol": 0,
        "swt_up_sell_cnt": 26,
        "swt_up_sell_vol": 496,
        "tib_buy_cnt": 0,
        "tib_buy_vol": 0,
        "tib_down_buy_cnt": 0,
        "tib_down_buy_vol": 0,
        "tib_down_sell_cnt": 0,
        "tib_down_sell_vol": 0,
        "tib_sell_cnt": 0,
        "tib_sell_vol": 0,
        "tib_up_buy_cnt": 0,
        "tib_up_buy_vol": 0,
        "tib_up_sell_cnt": 0,
        "tib_up_sell_vol": 0,
        "tot_down_buy_cnt": 43371,
        "tot_down_buy_vol": 1590195,
        "tot_down_sell_cnt": 15156,
        "tot_down_sell_vol": 106279,
        "tot_up_buy_cnt": 13989,
        "tot_up_buy_vol": 43492,
        "tot_up_sell_cnt": 56183,
        "tot_up_sell_vol": 232707
    }
    """

    time_str = str(in_bidask["Time"]).rjust(6, "0")
    in_bidask[
        "datetime"
    ] = f"{date}T{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}+08:00"
    for col in ["Time", "Market"]:
        in_bidask.pop(col)
    return in_bidask


def process_market_tick(in_tick: dict) -> MarketIndexTick:
    """
    I/TSE/001
    {
        "AfAmountSum": 0.0,
        "AfCnt": 0,
        "AfVolSum": 0,
        "Amount": 50304320.0,
        "AmountSum": 123728143040.0,
        "AmountSum_00": 0.0,
        "AmountSum_30": 0.0,
        "Close": 17703.19,
        "Cnt": 786013,
        "Code": "001",
        "Date": "2022/03/25",
        "DiffPrice": 4.13,
        "DiffRate": 0.02,
        "DiffType": 2,
        "High": 17747.13,
        "Low": 17633.86,
        "Open": 17695.8,
        "PrevDate": "",
        "Time": "10:00:30.000000",
        "VolSum": 2882042,
        "Volume": 1719,
        "bwt_gamt": 1187138290.0,
        "bwt_gcnt": 36712,
        "bwt_gvol": 952289,
        "es_camt": 24.28842350364265,
        "es_gamt": 5133.658796593614,
        "etf_gamt": 4353565210.0,
        "etf_gcnt": 44852,
        "etf_gvol": 253041,
        "oes_gamt": 1035701602.0,
        "oes_gcnt": 8330,
        "oes_gvol": 12182552,
        "pAmountSum": 0.0,
        "stk_gamt": 118045900750.0,
        "stk_gcnt": 700230,
        "stk_gvol": 1592714,
        "swt_gamt": 95885510.0,
        "swt_gcnt": 3395,
        "swt_gvol": 80509,
        "tib_gamt": 0.0,
        "tib_gcnt": 0,
        "tib_gvol": 0
    }
    """
    in_tick["code"] = in_tick["Code"]
    in_tick["datetime"] = f"{in_tick['Date'].replace('/', '-')}T{in_tick['Time']}+08:00"
    for col in ["Date", "Time", "PrevDate"]:
        in_tick.pop(col)
    return in_tick


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
    if quote["Date"] == "":
        date = time.strftime("%Y-%m-%d")
    else:
        date = quote["Date"].replace("/", "-")

    dt_str = date + "T" + quote["Time"] + "+08:00"

    return Tick(
        code=quote["Code"],
        dt=dt_str,
        open=quote["Open"],
        high=quote["High"],
        low=quote["Low"],
        price=quote["Close"],
        amt=quote["Amount"],
        tot_amt=quote["AmountSum"],
        vol=quote["Volume"],
        tot_vol=quote["VolSum"],
        tick_type=False,
        sim_trade=0,
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
        suspend = False

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
        sim_trade=bool(in_tick.simtrade),
    )
    return tick


def process_orderbook(
    in_bidask: Union[sj.BidAskSTKv1, sj.BidAskFOPv1]
) -> OrderBookFlattened:
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
        sim_trade=bool(in_bidask.simtrade),
    )
    return orderbook


class SinoQuote:
    def __init__(
        self,
        enable_publish: bool,
        enable_save: bool,
        pub_func: Callable[[str, dict], None],
    ):
        self.source = "sino"
        self.enable_publish = enable_publish
        self.enable_save = enable_save
        self._pub_func = pub_func
        self.markets: Dict[str, Union[Future, Stock, Option, Index]] = {}
        self._api: sj.Shioaji = None
        self._reset_data()
        self.trade_date = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d")

    def _reset_data(self) -> None:
        self._subscribed_codes: Dict[str, Set[str]] = defaultdict(set)
        self._q_tick = deque()
        self._q_orderbook = deque()
        self._lock_tick = Lock()
        self._lock_orderbook = Lock()

        self._q_market_tick = deque()
        self._q_market_info = deque()
        self._lock_market_tick = Lock()
        self._lock_market_info = Lock()

    def _get_contracts(self) -> Dict[str, Union[Future, Stock, Option, Index]]:
        contracts = {
            code: contract
            for name, iter_contract in self._api.Contracts
            for code, contract in iter_contract._code2contract.items()
        }
        return contracts

    def connect(self):
        logger.info("logging...")
        api = sj.Shioaji(simulation=SINO["simulation"])
        accounts = api.login(
            person_id=SINO["id"], passwd=SINO["password"], contracts_timeout=10000
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

    def _event_callback(self, resp_code: int, event_code: int, info: str, event: str):
        logger.info(f"Info:{info}| Event: {event}")

    def _on_tick(self, exchange: sj.Exchange, quote: Union[sj.TickSTKv1, sj.TickFOPv1]):
        tick = process_tick(quote)
        if self.enable_publish:
            channel = get_quote_channel(self.source, "tick", tick["code"])
            self._pub_func(channel, tick)
        if self.enable_save:
            with self._lock_tick:
                self._q_tick.append(tick)

    def _on_bidask(
        self, exchange: sj.Exchange, quote: Union[sj.BidAskSTKv1, sj.BidAskFOPv1]
    ):
        orderbook = process_orderbook(quote)
        if self.enable_publish:
            channel = get_quote_channel(self.source, "orderbook", orderbook["code"])
            self._pub_func(channel, orderbook)
        if self.enable_save:
            with self._lock_orderbook:
                self._q_orderbook.append(orderbook)

    def _quote_callback_v0(self, topic: str, quote: dict):
        """only support ind tick"""
        split_topic = topic.split("/")
        if split_topic[-1] != "ODD":
            code = split_topic[-1]
            odd = 0
        else:
            code = split_topic[-2]
            odd = 1
        quote["code"] = code

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
        if split_topic[0] == "I":
            sec_type = "ind"
            quote_type = "tick"
            quote = process_market_tick(quote)
            if self.enable_publish:
                channel = get_quote_channel(self.source, quote_type, code)
                self._pub_func(channel, quote)
            if self.enable_save:
                with self._lock_market_tick:
                    self._q_market_tick.append(quote)

        elif split_topic[0] == "O":
            sec_type = "ind"
            quote_type = "orderbook"
            quote = process_market_bidask(quote, self.trade_date)
            if self.enable_publish:
                channel = get_quote_channel(self.source, quote_type, code)
                self._pub_func(channel, quote)
            if self.enable_save:
                with self._lock_market_info:
                    self._q_market_info.append(quote)
        else:
            raise Exception(f"invalid quote_type {split_topic[0]}")

    def _get_quote_version(self, code: str):
        # Index
        if len(code) == 3 and code.startswith("0"):
            return "v0"
        else:
            return "v1"

    def _quote_type_convert(self, quote_type: str) -> str:
        if quote_type == "orderbook":
            return "bidask"
        elif quote_type == "market_tick":
            return "tick"
        elif quote_type == "tick_info":
            return "bidask"
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
                    version=self._get_quote_version(_code),
                )

    def unsubscribe(self, quote_types: List[str], codes: List[str]) -> None:
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
                    version=self._get_quote_version(_code),
                )

    def check_connection(self):
        try:
            data = self._api.snapshots([self.markets["TXFR1"]])
            if data:
                return True
            else:
                return False
        except:
            return False

    def get_queue_data(self, quote_type: str) -> pd.DataFrame:
        df = pd.DataFrame()
        if quote_type == "tick":
            if self._q_tick:
                with self._lock_tick:
                    df = pd.DataFrame(self._q_tick)
                    self._q_tick.clear()
                df.set_index("datetime", inplace=True)
                df.index = pd.to_datetime(df.index)

        elif quote_type == "orderbook":
            if self._q_orderbook:
                with self._lock_orderbook:
                    df = pd.DataFrame(self._q_orderbook)
                    self._q_orderbook.clear()
                df.set_index("datetime", inplace=True)
                df.index = pd.to_datetime(df.index)

        elif quote_type == "market_tick":
            if self._q_market_tick:
                with self._lock_market_tick:
                    df = pd.DataFrame(self._q_market_tick)
                    self._q_market_tick.clear()
                df.set_index("datetime", inplace=True)
                df.index = pd.to_datetime(df.index)

        elif quote_type == "market_info":
            if self._q_market_info:
                with self._lock_market_info:
                    df = pd.DataFrame(self._q_market_info)
                    self._q_market_info.clear()
                df.set_index("datetime", inplace=True)
                df.index = pd.to_datetime(df.index)
        return df
