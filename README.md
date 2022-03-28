# TradeView

TradeView is a stock analysis & monitoring solution.


## Set up Grafana and InfluxDB

```bash
cd docker && docker-compose -p trade_view up -d
```

## Installation

```bash
pip install -r requirements.txt
```


## Examples

```bash
python app.py -m stream
```

```bash
python app.py -m schedule
```

```bash
http://localhost:3000
```

<p align="center">
    <img  src="./readme_assets/influxdb2-market.JPG" width="100%">
</p>


<p align="center">
    <img  src="./readme_assets/influxdb2-stocks.JPG" width="100%">
</p>
