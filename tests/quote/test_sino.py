from trade_view.quote.sino import SinoQuote


sq = SinoQuote(enable_publish=False, pub_func=True)
quote_types = ['bidask']
codes = ['TXFD2', 'MXFD2']

def test_connect():
    sq.connect()

def test_reconnect():
    sq.reconnect()

def test_subscribe():
    sq.subscribe(
        quote_types,
        codes
    )

def test_unsubscribe():
    sq.unsubscribe(
        quote_types,
        codes
    )

def test_check_connection():
    return sq.check_connection()

def test_get_queue_data():
    return sq.get_queue_data(quote_type=quote_types[0])

