from typing import TypedDict, List


class Tick(TypedDict):
    code: str
    datetime: str #isoformat
    open: float
    high: float
    low: float
    close: float
    amount: float
    total_amount: float
    volume: int
    total_volume: int
    tick_type: int
    suspend: bool
    simtrade: bool


class OrderBook(TypedDict):
    code: str
    datetime: str #isoformat
    bids: List[float]
    bid_vols: List[int]
    asks: List[float]
    ask_vols: List[int]
    suspend: bool
    simtrade: bool


class OrderBookFlattened(TypedDict):
    code: str
    datetime: str #isoformat
    bid1: float
    bid2: float
    bid3: float
    bid4: float
    bid5: float
    bid1_vol: int
    bid2_vol: int
    bid3_vol: int
    bid4_vol: int
    bid5_vol: int
    
    ask1: float
    ask2: float
    ask3: float
    ask4: float
    ask5: float
    ask1_vol: int
    ask2_vol: int
    ask3_vol: int
    ask4_vol: int
    ask5_vol: int
    suspend: bool
    simtrade: bool


class Kbar(TypedDict):
    pass