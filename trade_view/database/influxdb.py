from loguru import logger 
import pandas as pd
from typing import List, Any
from influxdb_client import (
    InfluxDBClient, WriteOptions, BucketRetentionRules
)
from influxdb_client.client.write_api import (
    WriteType, PointSettings, ASYNCHRONOUS
)


from trade_view import config



class InfluxDB:
    def __init__(self):
        self.client = InfluxDBClient(
            url=config.INFLUXDB_URL,
            token=config.INFLUXDB_TOKEN,
            org=config.INFLUXDB_ORG
        )
        self.org = config.INFLUXDB_ORG
        
    def __del__(self):
        self.client.close()
        
    def create_bucket(self, bucket_name: str):
        buckets_api = self.client.buckets_api()
        # retention_rules = BucketRetentionRules(
        #     type="expire", 
        #     every_seconds=3600
        # )
        created_bucket = buckets_api.create_bucket(
            org=self.org,
            bucket_name=bucket_name,
            #retention_rules=retention_rules,
        )
        logger.info(created_bucket)

    def delete_bucket(self, bucket_name: str):
        buckets_api = self.client.buckets_api()
        buckets = buckets_api.find_buckets().buckets
        for bucket in buckets:
            if bucket.name == bucket_name:
                buckets_api.delete_bucket(bucket)
                logger.info(bucket)
                break

    def write_batch(self, 
        bucket: str, 
        df: pd.DataFrame,
        measurement_name: str,
        tag_columns: List[str] = [],
        point_settings : dict = {},
        batch_size: int = 50000,
        flush_interval: int = 100,
    ):  
        with self.client.write_api(
            write_options=WriteOptions(
                write_type=WriteType.batching,
                batch_size=batch_size, 
                flush_interval=flush_interval
            ),
            point_settings=PointSettings(**point_settings),
        ) as write_api:
            write_api.write(
                bucket=bucket, 
                record=df, 
                data_frame_measurement_name=measurement_name,
                data_frame_tag_columns=tag_columns,
            )

    def write_structured_data(self,
        bucket: str, 
        record: Any,
        measurement_key: str,
        time_key: str,
        tag_keys: List[str],
        field_keys: List[str] = [],
    ):
        with self.client.write_api(
            write_options=ASYNCHRONOUS
        ) as write_api:
            write_api.write(
                bucket=bucket,
                record=record,
                record_measurement_key=measurement_key,
                record_time_key=time_key,
                record_tag_keys=tag_keys,
                record_field_keys=field_keys
            )


if __name__ == '__main__':
    cli = InfluxDB()
    bucket = 'sino_quotes'

    cli.create_bucket(bucket)
    cli.delete_bucket(bucket)

    """
    from(bucket:"sino_quotes")
    |> range(start: 0, stop: now())
    |> filter(fn: (r) => r._measurement == "kbars")
    |> filter(fn: (r) => r.sec_type == "F")
    |> filter(fn: (r) => r.category == "TXF")
    |> filter(fn: (r) => r.symbol == "TXFD2")

    |> filter(fn: (r) => r._field == "Close" or r._field == "Open"  or r._field == "High" or r._field == "Low")
    
    |> keep(columns: ["_field", "_value","_time", "symbol"])
    |> drop(columns: ["_start", "_stop","_measurement"])



    from(bucket:"sino_quotes")
    |> range(start: 0, stop: now())
    |> filter(fn: (r) => r._measurement == "ticks")
    |> filter(fn: (r) => r.sec_type == "F")
    |> filter(fn: (r) => r.category == "TXF")
    |> filter(fn: (r) => r.symbol == "TXFD2")    
    |> keep(columns: ["_field", "_value","_time", "symbol"])
    """