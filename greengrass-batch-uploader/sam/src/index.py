import boto3
import json
import os

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()


def copy_s3_object(source_bucket, source_key, destination_bucket, destination_key):
    s3 = boto3.client('s3')

    try:
        s3.copy_object(Bucket=destination_bucket,
                       Key=destination_key,
                       CopySource={'Bucket': source_bucket, 'Key': source_key})

        logger.info(
            f"Copied object {source_bucket}/{source_key} to {destination_bucket}/{destination_key}")

    except Exception as e:
        logger.exception(f"Error copying S3 object: {e}")


@logger.inject_lambda_context
@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context: LambdaContext):
    logger.info(f"Event received: {event}")

    for record in event.records:
        try:
            message = json.loads(record.body)

            source_bucket = message['detail']['bucket']['name']
            source_key = message['detail']['object']['key']

            logger.info(
                f"Processing {source_key} from bucket {source_bucket}, Starting to copy object to temporary location")

            destination_bucket = os.environ.get('BATCH_BUCKET_NAME')
            destination_key = f"{context.aws_request_id}/{source_key.split('/')[-1]}"

            copy_s3_object(source_bucket, source_key,
                           destination_bucket, destination_key)

        except Exception as e:
            logger.exception(f"Error processing record: {e}")
