from trade_view.worker import QuoteWorker
from trade_view.setting import QUOTE_WORKER

qw = QuoteWorker(**QUOTE_WORKER)


def test_run():
    qw.run()