import os
import logging
import time

import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    PublishToTopicRequest,
    PublishMessage,
    BinaryMessage
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

hostname = os.environ.get("HOSTNAME")
if not hostname:
    logger.error("HOSTNAME is empty")
    raise ValueError("HOSTNAME is empty")

while True:
    time.sleep(30)

    topic = "devopstar/robocat/{}/meow".format(thing_name)
    message = "Meow! from {} running in {} container".format(thing_name, hostname)

    request = PublishToTopicRequest()
    request.topic = topic
    publish_message = PublishMessage()
    publish_message.binary_message = BinaryMessage()
    publish_message.binary_message.message = bytes(message, "utf-8")

    try:
        request.publish_message = publish_message
        operation = ipc_client.new_publish_to_topic()
        logger.info("Publishing message to topic {}: {}".format(topic, message))
        operation.activate(request)
        future_response = operation.get_response()
        future_response.result(TIMEOUT)
    except Exception as e:
        logger.error("Failed to publish message {}".format(e))
