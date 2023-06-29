import sys
import time
import logging
import json

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest
)

TIMEOUT = 10

ipc_client = awsiot.greengrasscoreipc.connect()

logging.basicConfig(level=logging.INFO)

class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            message = str(event.message.payload, "utf-8")
            logging.info(message)
        except:
            logging.error("Exception occurred", exc_info=True)

    def on_stream_error(self, error: Exception) -> bool:
        logging.error(f"Stream error: {error}")
        return True

    def on_stream_closed(self) -> None:
        logging.info("Stream closed")


def publish_message(topic: str, message: str):
    logging.info(f"Publishing message to topic {topic}: {message}")
    request = PublishToIoTCoreRequest()
    request.topic_name = topic
    request.qos = QOS.AT_MOST_ONCE
    request.payload = bytes(message, "utf-8")

    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    operation.get_response().result(TIMEOUT)


if __name__ == "__main__":
    # args : enabled, frequency, sub_topic, pub_topic
    if len(sys.argv) == 5:
        if sys.argv[1].lower() == "true":
            enabled = True
        else:
            enabled = False
        frequency = float(sys.argv[2])
        sub_topic = sys.argv[3]
        pub_topic = sys.argv[4]

        logging.info(f"enabled: {enabled}, frequency: {frequency}, sub_topic: {sub_topic}, pub_topic: {pub_topic}")

        handler = StreamHandler()
        request = SubscribeToIoTCoreRequest()
        request.topic_name = sub_topic
        request.qos = QOS.AT_MOST_ONCE
        operation = ipc_client.new_subscribe_to_iot_core(handler)
        operation.activate(request)
        future_response = operation.get_response()
        future_response.result(TIMEOUT)

        message_count = 1

        try:
            while True:
                time.sleep(frequency)
                if enabled:
                    message = json.dumps({
                        "id": message_count,
                        "timestamp": time.time()
                    })
                    publish_message(pub_topic, message)
                    message_count += 1
        except:
            logging.error("Exception occurred", exc_info=True)
            operation.close()
    else:
        logging.error(f'4 arguments required, only {len(sys.argv) - 1} provided.')
