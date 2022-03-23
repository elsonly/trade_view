import argparse

from trade_view.worker import QuoteWorker
from trade_view.setting import QUOTE_WORKER


if __name__ == '__main__':    
    parser = argparse.ArgumentParser()    
    parser.add_argument(
        "-m", "--mode", 
        type=str,
        help="stream or history"
    )

    args = parser.parse_args()

    if args.mode == 'stream':
        qw = QuoteWorker(**QUOTE_WORKER)
        qw.run()
    
    elif args.mode == 'history':
        pass