import schedule
from typing import List
import time

from trade_view.history import HistorySource
from trade_view.history.sino import SinoHistoryHandler
from trade_view.database import DataBaseSource
from trade_view.database.data_manager import DataManager
from trade_view.setting import SCHEDULES


def dispatch_jobs(
    source: str,
    database: str,
    types: List[str],
    start_date: str,
    end_date: str,
    codes: List[str],
):  
    if source == HistorySource.Sino.value:
        history_handler = SinoHistoryHandler()
    else:
        raise
    dm = DataManager(DataBaseSource(database))

    
    for _type in types:
        if _type == 'kbar':
            for _code in codes:
                df = history_handler.get_kbars(
                    _code, start_date, end_date
                )
                dm.save_dataframe_quote(
                    source,
                    'kbars',
                    df
                )

        elif _type == 'tick':
            for _code in codes:
                df = history_handler.get_ticks(
                    _code, start_date, end_date
                )
                dm.save_dataframe_quote(
                    source,
                    'ticks',
                    df
                )


        elif _type == 'market':
            df = history_handler.get_markets()
            dm.save_dataframe_quote(
                source,
                'markets',
                df,
                index_columns=['exchange', 'security_type', 'code']
            )


def register_and_run():
    for _job in SCHEDULES:
        print(_job)

        if not _job['schedule']:
            dispatch_jobs(
                source=_job['source'],
                database=_job['database'],
                types=_job['types'],
                start_date=_job['start_date'],
                end_date=_job['end_date'],
                codes=_job['codes'],
            )
        else:
            schedule.every().day.at(_job['schedule']).do(
                dispatch_jobs,
                source=_job['source'],
                database=_job['database'],
                types=_job['types'],
                start_date=_job['start_date'],
                end_date=_job['end_date'],
                codes=_job['codes'],
            )
        

    while True:
        schedule.run_pending()
        time.sleep(1)