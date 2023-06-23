# greengrass-batch-uploader

## Deploy

```bash
pip3 install aws-sam-cli==1.87.0
sam build
sam deploy
```

## Relies on

1. An Athena table called `greengrass_data_iceberg` with the following schema:

    ```sql
    CREATE TABLE IF NOT EXISTS greengrass_data_iceberg (
        `id` string,
        `timestamp` timestamp,
        `speed` int,
        `temperature` float,
        `location` struct<lat:float, lng:float>
    )
    PARTITIONED BY (hour(`timestamp`))
    LOCATION 's3://greengrass-stream-manager-iceberg-ap-southeast-2-536829251200/'
    TBLPROPERTIES (
        'table_type'='ICEBERG',
        'format'='parquet',
        'write_compression'='gzip',
        'vacuum_min_snapshots_to_keep'='5',
        'vacuum_max_snapshot_age_seconds'='86400'
    );
    ``

2. An Athena Query output location of `s3://athena-ap-southeast-2-536829251200/` attached to the `primary` workgroup.
