import ciso8601
from loguru import logger

from trade_view.grafana.websocket_manager import WebsocketManager
from trade_view.config import GF_API_KEY


class GrafanaPusher(WebsocketManager):
    ENDPOINT = "ws://localhost:3000/api/live/push/gf_pusher"

    def __init__(self):
        self._header = {"Authorization": f"Bearer {GF_API_KEY}"}
        super().__init__()

    def _get_url(self):
        return self.ENDPOINT

    def _get_header(self):
        return self._header

    def _on_message(self, ws, message):
        logger.info(message)

    def _convert_to_influx_format(self, val):
        if isinstance(val, bool):
            if val:
                return "true"
            else:
                return "false"
        elif isinstance(val, str):
            return f'"{val}"'
        else:
            return val

    def _convert_to_influx_line(self, channel: str, d: dict):
        try:
            return (
                f"{channel} "
                + ",".join(
                    [
                        f"{key}={self._convert_to_influx_format(d[key])}"
                        for key in d
                        if key != "datetime"
                    ]
                )
                + f" {ciso8601.parse_datetime(d['datetime']).timestamp()*10**9:.0f}"
            )
        except Exception as exc:
            logger.exception(exc)
            logger.error(d["datetime"])

    def send_dict(self, channel: str, msg_d: dict):
        # <measurement>[,<tag_key>=<tag_value>[,<tag_key>=<tag_value>]] <field_key>=<field_value>[,<field_key>=<field_value>] [<timestamp>]
        msg = self._convert_to_influx_line(channel, msg_d)
        self.send(msg)
