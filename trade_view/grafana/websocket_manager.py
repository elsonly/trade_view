import json
import time
from threading import Thread
from websocket import WebSocketApp

from loguru import logger

class WebsocketManager:
    _CONNECT_TIMEOUT_S = 5
    _PING_TIMEOUT_S = 5
    _PING_INTERVAL_S = 15

    def __init__(self):
        self.ws:WebSocketApp = None

    def _get_url(self):
        raise NotImplementedError()

    def _get_header(self):
        raise NotImplementedError()

    def send(self, message):
        self.ws.send(message)

    def send_json(self, message):
        self.send(json.dumps(message))

    def _wrap_callback(self, f):
        def wrapped_f(ws, *args, **kwargs):
            if ws is self.ws:
                try:
                    f(ws, *args, **kwargs)
                except Exception as e:
                    raise Exception(f'Error running websocket callback: {e}')
        return wrapped_f

    def _run_websocket(self, ws:WebSocketApp):
        logger.info("Run WebsocketApp")
        try:
            ws.run_forever()
            logger.info("WebsocketApp Terminated")
        except Exception as e:
            raise Exception(f'Unexpected error while running websocket: {e}')
        finally:
            self._reconnect()

    def _connect(self):
        assert not self.ws, "ws should be closed before attempting to connect"
        logger.info("connecting...")
        self.ws = WebSocketApp(
            self._get_url(),
            header=self._get_header(),
            on_message=self._wrap_callback(self._on_message),
            on_close=self._wrap_callback(self._on_close),
            on_error=self._wrap_callback(self._on_error),
        )
        wst = Thread(target=self._run_websocket, args=(self.ws,))
        wst.daemon = True
        wst.start()

        # Wait for socket to connect
        ts = time.time()
        while self.ws and (not self.ws.sock or not self.ws.sock.connected):
            if time.time() - ts > self._CONNECT_TIMEOUT_S:
                self.ws = None
                logger.warning('connect failed')
                return
            time.sleep(0.1)
        logger.info("connected")
    
    def _reconnect(self) -> None:
        if self.ws:
            self.ws.close()
            self.ws = None
        self.connect()

    def connect(self):
        if self.ws:
            return
        while not self.ws:
            self._connect()
            if self.ws:
                return
        
    def _on_close(self, ws, *args):
        logger.warning('connection lost')
        self.ws.keep_running = False

    def _on_error(self, ws, error):
        logger.exception(error)

    def _on_message(self, ws, message):
        raise NotImplementedError()