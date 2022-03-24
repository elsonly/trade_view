from trade_view.history import HistorySource
from trade_view.history.history_handler import HistoryHandler

source = HistorySource.Sino
hh = HistoryHandler(source)
code = '2330'
start_date = '2022-03-21'
end_date = '2022-03-22'


def test_get_markets():
    return hh.get_markets()

def test_get_kbars():
    return hh.get_kbars(code, start_date, end_date)

def test_get_ticks():
    return hh.get_ticks(code, start_date, end_date)