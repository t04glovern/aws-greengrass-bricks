#!/usr/bin/env python
#
# pip install boto3
# ./redrive-processing.py enable|disable
# ./redrive-processing.py redrive

import argparse
import boto3
from botocore.exceptions import ClientError


def get_lambda_arn(function_name):
    client = boto3.client('lambda', region_name='ap-southeast-2')
    try:
        response = client.get_function(FunctionName=function_name)
        return response['Configuration']['FunctionArn']
    except ClientError as e:
        print(f"Error getting ARN for Lambda function {function_name}: {e}")
        return None


def get_sqs_arn(queue_name):
    client = boto3.client('sqs', region_name='ap-southeast-2')
    try:
        response = client.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        response = client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])
        return response['Attributes']['QueueArn']
    except ClientError as e:
        print(f"Error getting ARN for SQS queue {queue_name}: {e}")
        return None


def toggle_event_source(trigger_state, lambda_arn, event_source_arn):
    client = boto3.client('lambda', region_name='ap-southeast-2')

    # Get the current event source mappings
    response = client.list_event_source_mappings(
        FunctionName=lambda_arn,
        EventSourceArn=event_source_arn
    )

    # Check if there are any event source mappings
    if len(response['EventSourceMappings']) == 0:
        raise Exception('No event source mappings found for the specified Lambda function and SQS queue.')

    # Loop over all the event source mappings and enable/disable them
    for mapping in response['EventSourceMappings']:
        if trigger_state == 'enable':
            if mapping['State'] != 'Enabled':
                client.update_event_source_mapping(UUID=mapping['UUID'], Enabled=True)
        elif trigger_state == 'disable':
            if mapping['State'] != 'Disabled':
                client.update_event_source_mapping(UUID=mapping['UUID'], Enabled=False)


def start_message_move_task(source_arn, dest_arn):
    sqs = boto3.client('sqs', region_name='ap-southeast-2')
    try:
        response = sqs.start_message_move_task(SourceArn=source_arn, DestinationArn=dest_arn)
        print(f"Started moving messages from {source_arn} to {dest_arn}. TaskHandle: {response['TaskHandle']}")
    except ClientError as e:
        print(f"Error starting message move task: {e}")


def main():
    parser = argparse.ArgumentParser(description='Enable or disable an SQS event source trigger for a Lambda function or redrive messages from DLQ.')
    parser.add_argument('action', choices=['enable', 'disable', 'redrive'], help='The action to perform.')
    args = parser.parse_args()

    # Names of the Lambda function and SQS queue
    lambda_name = 'batch-uploader-robocat-greengrass'
    sqs_name = 'batch-uploader-robocat-greengrass-landing'

    # Get the ARNs for the Lambda function and SQS queue
    lambda_arn = get_lambda_arn(lambda_name)
    event_source_arn = get_sqs_arn(sqs_name)
    dlq_arn = get_sqs_arn(sqs_name + "-dlq")

    if lambda_arn is None or event_source_arn is None or dlq_arn is None:
        print("Exiting due to error getting ARNs.")
        return

    if args.action in ['enable', 'disable']:
        toggle_event_source(args.action, lambda_arn, event_source_arn)
    elif args.action == 'redrive':
        start_message_move_task(dlq_arn, event_source_arn)

if __name__ == '__main__':
    main()
