import os
import logging
import time

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest
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

# publish message
topic = "devopstar/robocat/{}/meow".format(thing_name)
message = "Meow! from {} running in {} container".format(
    thing_name, hostname)
qos = QOS.AT_LEAST_ONCE

request = PublishToIoTCoreRequest()
request.topic_name = topic
request.payload = bytes(message, "utf-8")
request.qos = qos

# Keep the main thread alive, or the process will exit.
while True:
    time.sleep(10)
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    future_response = operation.get_response()

    try:
        future_response.result(TIMEOUT)
    except Exception as e:
        logger.error("Failed to publish message {}".format(e))
