import boto3
import os
import time

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import event_source, EventBridgeEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

event_logger = Logger()

ATHENA_DATABASE = os.environ.get('ATHENA_DATABASE', 'default')
ATHENA_TABLE = os.environ.get('ATHENA_TABLE')
ATHENA_WORKGROUP = os.environ.get('ATHENA_WORKGROUP', 'primary')

athena = boto3.client('athena')


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


@event_logger.inject_lambda_context
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context: LambdaContext):
    try:
        rule_arn = event["resources"][0]

        if rule_arn.endswith("-maintenance-vacuum"):
            run_athena_query(f"VACUUM {ATHENA_DATABASE}.{ATHENA_TABLE};")
        elif rule_arn.endswith("-maintenance-optimize"):
            run_athena_query(f"OPTIMIZE {ATHENA_DATABASE}.{ATHENA_TABLE} REWRITE DATA USING BIN_PACK;")
        else:
            event_logger.info("No matching rule suffix found. Make sure the rule ARN ends with '-maintenance-optimize' or '-maintenance-vacuum'.")
    except Exception as e:
        event_logger.exception(f"Error occurred during table maintenance: {e}")
        raise e
