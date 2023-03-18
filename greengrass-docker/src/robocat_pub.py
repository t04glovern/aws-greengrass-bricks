import os
import logging
import time
import traceback

from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
from awsiot.greengrasscoreipc.model import (
    PublishMessage,
    JsonMessage
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

thing_name = os.environ.get("AWS_IOT_THING_NAME")
if not thing_name:
    logger.error("AWS_IOT_THING_NAME is empty")
    raise ValueError("AWS_IOT_THING_NAME is empty")


def publish_json_message_to_topic(ipc_client, topic, message):
    json_message = JsonMessage(message=message)
    publish_message = PublishMessage(json_message=json_message)
    return ipc_client.publish_to_topic(topic=topic, publish_message=publish_message)


while True:
    time.sleep(30)
    topic = "devopstar/robocat/{}/meow".format(thing_name)
    message = {
        "thing": thing_name,
        "message": "Meow!"
    }

    try:
        ipc_client = GreengrassCoreIPCClientV2()
        publish_json_message_to_topic(ipc_client, topic, message)
        logger.info("Published message {} to topic {}".format(message, topic))
    except Exception as e:
        logger.error("Failed to publish message {}".format(e))
        traceback.print_exc()
