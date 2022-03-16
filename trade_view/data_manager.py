from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "btoMns5-o__S3C0xlB6RIMTpsjxpAefNMaWftWJrMh243m0PtnHIh1DLyGh_io82c2TcRGEjbYFAJs0qlyzHZw=="
org = "my-org"
bucket = "my-bucket"

client = InfluxDBClient(url="http://localhost:8086", token=token)


write_api = client.write_api(write_options=SYNCHRONOUS)

data = "mem,host=host1 used_percent=23.43234543"
write_api.write(bucket, org, data)


sequence = ["mem,host=host1 used_percent=23.43234543",
            "mem,host=host1 available_percent=15.856523"]
write_api.write(bucket, org, sequence)

p = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
write_api.write(bucket=bucket, org=org, record=p)



# query
query = f'from(bucket: "{bucket}") |> range(start:-1h)'
tables = client.query_api().query(query, org=org)

query = ' from(bucket:"my-bucket")\
|> range(start: -10m)\
|> filter(fn:(r) => r._host == "0") '

tables = client.query_api().query(query, org=org)

results = []
for table in tables:
  for record in table.records:
    results.append((record.get_field(), record.get_value()))
