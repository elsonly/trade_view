from trade_view.worker import QuoteWorker
from trade_view.setting import WORKER

qw = QuoteWorker(**WORKER)


def test_run():
    qw.run()