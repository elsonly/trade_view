from trade_view.grafana.pusher import GrafanaPusher


if __name__ == '__main__':
    gfp = GrafanaPusher()
    gfp.connect()
    gfp.send_dict('sino/tick/TXO', {})