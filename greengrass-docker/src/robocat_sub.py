import os
import logging
import time
import traceback

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage
)

TIMEOUT = 10

# setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# setup ipc client
ipc_client = awsiot.greengrasscoreipc.connect()

# get environment variables
thing_name = os.environ.get("AWS_IOT_THING_NAME")
if not thing_name:
    logger.error("AWS_IOT_THING_NAME is empty")
    raise ValueError("AWS_IOT_THING_NAME is empty")

class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            message_string = str(event.binary_message.message, "utf-8")
            logger.info("Received message from topic {}: {}".format(event.topic, message_string))
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass


topic = "devopstar/robocat/{}/meow".format(thing_name)

request = SubscribeToTopicRequest()
request.topic = topic
handler = StreamHandler()
operation = ipc_client.new_subscribe_to_topic(handler) 
operation.activate(request)
future_response = operation.get_response()
future_response.result(TIMEOUT)

# Keep the main thread alive, or the process will exit.
while True:
    time.sleep(10)

# To stop subscribing, close the operation stream.
operation.close()
