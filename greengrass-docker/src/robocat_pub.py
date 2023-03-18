import os
import logging
import time
import traceback

from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
from awsiot.greengrasscoreipc.model import (
    PublishMessage,
    BinaryMessage
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

thing_name = os.environ.get("AWS_IOT_THING_NAME")
if not thing_name:
    logger.error("AWS_IOT_THING_NAME is empty")
    raise ValueError("AWS_IOT_THING_NAME is empty")

hostname = os.environ.get("HOSTNAME")
if not hostname:
    logger.error("HOSTNAME is empty")
    raise ValueError("HOSTNAME is empty")


def publish_binary_message_to_topic(ipc_client, topic, message):
    binary_message = BinaryMessage(message=bytes(message, 'utf-8'))
    publish_message = PublishMessage(binary_message=binary_message)
    return ipc_client.publish_to_topic(topic=topic, publish_message=publish_message)


while True:
    time.sleep(30)
    topic = "devopstar/robocat/{}/meow".format(thing_name)
    message = "Meow! from {} running in {} container".format(
        thing_name, hostname)

    try:
        ipc_client = GreengrassCoreIPCClientV2()
        publish_binary_message_to_topic(ipc_client, topic, message)
        logger.info("Published message {} to topic {}".format(message, topic))
    except Exception as e:
        logger.error("Failed to publish message {}".format(e))
        traceback.print_exc()
