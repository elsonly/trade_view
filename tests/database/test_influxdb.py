from trade_view.database.influxdb import InfluxDB

cli = InfluxDB()
bucket = "sino_quotes"

def test_create_bucket():
    cli.create_bucket(bucket)

def test_delete_bucket():
    cli.delete_bucket(bucket)