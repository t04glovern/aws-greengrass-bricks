# greengrass-batch-uploader

## Deploy

```bash
pip3 install aws-sam-cli==1.89.0
sam build
sam deploy
```

## Relies on

1. Create the Iceberg & Athena Query bucket

    ```bash
    aws s3 mb s3://greengrass-stream-manager-iceberg-ap-southeast-2-000000000000
    aws s3 mb s3://athena-ap-southeast-2-000000000000
    ```

2. An Athena table called `greengrass_data_iceberg` with the following schema:

    ```sql
    CREATE TABLE IF NOT EXISTS greengrass_data_iceberg (
        `id` string,
        `timestamp` timestamp,
        `speed` int,
        `temperature` float,
        `location` struct<lat:float, lng:float>
    )
    PARTITIONED BY (hour(`timestamp`))
    LOCATION 's3://greengrass-stream-manager-iceberg-ap-southeast-2-000000000000/'
    TBLPROPERTIES (
        'table_type'='ICEBERG',
        'format'='parquet',
        'write_compression'='gzip',
        'vacuum_min_snapshots_to_keep'='5',
        'vacuum_max_snapshot_age_seconds'='86400'
    );
    ``

3. An Athena Query output location of `s3://athena-ap-southeast-2-000000000000/` attached to the `primary` workgroup.

    ```bash
    aws athena update-work-group --region ap-southeast-2 --work-group primary --configuration-updates ResultConfigurationUpdates="{OutputLocation=s3://athena-ap-southeast-2-000000000000/}"
    ```
