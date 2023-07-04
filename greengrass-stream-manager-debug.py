#!/usr/bin/env python
#
# This script requires STREAM_MANAGER_AUTHENTICATE_CLIENT to be set to false
# in the aws.greengrass.StreamManager component
# https://docs.aws.amazon.com/greengrass/v2/developerguide/stream-manager-component.html#stream-manager-component-configuration
#
# pip install greengrasssdk==1.6.1
# ./greengrass-stream-manager-debug.py list
# ./greengrass-stream-manager-debug.py read --stream <stream_name>
# ./greengrass-stream-manager-debug.py write --stream <stream_name> --message <message>

import argparse
from pprint import pprint

from greengrasssdk.stream_manager import StreamManagerClient
from greengrasssdk.stream_manager.data import ReadMessagesOptions


def list_streams(client):
    try:
        streams = client.list_streams()
        print("Streams:")
        for stream in streams:
            print(stream)
    except Exception as e:
        print("Error occurred while listing streams:", e)


def describe_stream(client, stream_name):
    try:
        stream_info = client.describe_message_stream(stream_name)
        print(f"\nInformation for Stream: {stream_name}\n")

        # Parse and display the stream information
        stream_def = stream_info.definition
        storage_status = stream_info.storage_status
        export_statuses = stream_info.export_statuses

        print("Stream Definition:")
        pprint(stream_def.as_dict())
        
        print("\nStorage Status:")
        print(f"  Oldest Sequence: {storage_status.oldest_sequence_number}")
        print(f"  Newest Sequence: {storage_status.newest_sequence_number}")
        print(f"  Total Bytes: {storage_status.total_bytes}\n")

        if export_statuses:
            for i, export_status in enumerate(export_statuses):
                print(f"Export Status {i + 1}:")
                pprint(export_status.as_dict())
                print("\n")

    except Exception as e:
        print(f"Error occurred while describing {stream_name}:", e)


def get_newest_sequence(client, stream_name):
    try:
        stream_info = client.describe_message_stream(stream_name)
        storage_status = stream_info.storage_status
        return storage_status.newest_sequence_number
    except Exception as e:
        print(f"Error occurred while fetching newest sequence from {stream_name}:", e)
        return None

def read_stream(client, stream_name):
    try:
        newest_sequence = get_newest_sequence(client, stream_name)
        if newest_sequence is not None:
            options = ReadMessagesOptions(desired_start_sequence_number=newest_sequence)
            messages = client.read_messages(stream_name, options)
            print(f"Messages from {stream_name}:")
            for message in messages:
                print(message)
        else:
            print("Failed to fetch the newest sequence. Reading operation aborted.")
    except Exception as e:
        print(f"Error occurred while reading from {stream_name}:", e)


def append_message(client, stream_name, message):
    try:
        sequence_number = client.append_message(stream_name, message.encode())
        print(f"Message appended to {stream_name} at sequence {sequence_number}")
    except Exception as e:
        print(f"Error occurred while appending message to {stream_name}:", e)


def main():
    parser = argparse.ArgumentParser(description='Stream Manager Debug Tool')
    parser.add_argument('operation', choices=['list', 'describe', 'read', 'write'], help='The operation to perform.')
    parser.add_argument('--stream', help='The stream to interact with.')
    parser.add_argument('--message', help='The message to write to the stream.')
    args = parser.parse_args()

    try:
        client = StreamManagerClient()

        if args.operation == 'list':
            list_streams(client)
        elif args.operation == 'describe':
            if args.stream:
                describe_stream(client, args.stream)
            else:
                print("Please provide a stream name using --stream.")
        elif args.operation == 'read':
            if args.stream:
                read_stream(client, args.stream)
            else:
                print("Please provide a stream name using --stream.")
        elif args.operation == 'write':
            if args.stream and args.message:
                append_message(client, args.stream, args.message)
            else:
                print("Please provide a stream name and message using --stream and --message respectively.")
    except Exception as e:
        print("Error occurred:", e)
    finally:
        client.close()


if __name__ == '__main__':
    main()
