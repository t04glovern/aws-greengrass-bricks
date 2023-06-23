import boto3
import json
import os
import time

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

event_logger = Logger()

ATHENA_DATABASE = os.environ.get('ATHENA_DATABASE', 'default')
ATHENA_TABLE = os.environ.get('ATHENA_TABLE')
ATHENA_WORKGROUP = os.environ.get('ATHENA_WORKGROUP', 'primary')
BATCH_BUCKET_NAME = os.environ.get('BATCH_BUCKET_NAME')


def run_athena_query(query):
    athena_client = boto3.client('athena')

    try:
        event_logger.info(f"Executing query: {query}")

        query_start_response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": ATHENA_DATABASE},
            WorkGroup=ATHENA_WORKGROUP,
        )

        query_execution_id = query_start_response["QueryExecutionId"]

        while True:
            query_status_response = athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )

            query_execution_status = query_status_response["QueryExecution"]["Status"]["State"]

            if query_execution_status in ["SUCCEEDED"]:
                event_logger.info(f"Query executed successfully.")
                return
            elif query_execution_status in ["FAILED", "CANCELLED"]:
                event_logger.error(
                    f"Query execution failed. Status: {query_execution_status}")
                raise Exception(
                    f"Query execution failed. Status: {query_execution_status}")
            else:
                event_logger.info(
                    f"Query execution in progress. Current status: {query_execution_status}")

            time.sleep(5)

    except Exception as err:
        event_logger.exception(f"Error during query execution: {err}")
        raise err


def transfer_s3_file(src_bucket, src_key, dest_bucket, dest_key):
    s3_client = boto3.client('s3')

    try:
        s3_client.copy_object(Bucket=dest_bucket,
                              Key=dest_key,
                              CopySource={'Bucket': src_bucket, 'Key': src_key})

        event_logger.info(
            f"Transferred file {src_bucket}/{src_key} to {dest_bucket}/{dest_key}")

    except Exception as err:
        event_logger.exception(f"Error transferring S3 file: {err}")


@event_logger.inject_lambda_context
@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context: LambdaContext):
    for record in event.records:
        try:
            msg = json.loads(record.body)

            src_bucket = msg['detail']['bucket']['name']
            src_key = msg['detail']['object']['key']

            event_logger.info(
                f"Processing {src_key} from bucket {src_bucket}, Starting to transfer file to temporary location")

            dest_bucket = BATCH_BUCKET_NAME
            dest_key = f"{context.aws_request_id}/{src_key.split('/')[-1]}"

            transfer_s3_file(src_bucket, src_key, dest_bucket, dest_key)

            table_prefix = '/'.join(dest_key.split('/')[:-1])
            tmp_table_id = table_prefix.split('-')[-1].lower()

            ATHENA_TMP_TABLE = "{}_{}".format(ATHENA_TABLE, tmp_table_id)
            ATHENA_TMP_S3_BUCKET = dest_bucket
            ATHENA_TMP_TABLE_PREFIX = table_prefix

            # Create Temporary Table
            run_athena_query(f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS {ATHENA_DATABASE}.{ATHENA_TMP_TABLE} (
                `id` string,
                `timestamp` timestamp,
                `speed` int,
                `temperature` float,
                `location` struct<lat:float, lng:float>
            )
            ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
            WITH SERDEPROPERTIES ( "timestamp.formats"="yyyy-MM-dd'T'HH:mm:ss.SSSSSS" )
            LOCATION 's3://{ATHENA_TMP_S3_BUCKET}/{ATHENA_TMP_TABLE_PREFIX}'
            TBLPROPERTIES ('has_encrypted_data'='false')
            """)

            # Insert into Main Table
            run_athena_query(
                f"INSERT INTO {ATHENA_DATABASE}.{ATHENA_TABLE} SELECT * FROM {ATHENA_DATABASE}.{ATHENA_TMP_TABLE};")

            # Drop Temporary Table
            run_athena_query(
                f"DROP TABLE {ATHENA_DATABASE}.{ATHENA_TMP_TABLE};")

        except Exception as err:
            event_logger.exception(f"Error processing record: {err}")
            try:
                run_athena_query(
                    f"DROP TABLE {ATHENA_DATABASE}.{ATHENA_TMP_TABLE};")
            except Exception as e:
                event_logger.exception(f"Error dropping temporary table: {e}")
                raise e
            raise err
