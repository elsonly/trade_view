from trade_view.worker import QuoteWorker
from trade_view.setting import WORKER



if __name__ == '__main__':
    qw = QuoteWorker(**WORKER)
    qw.run()