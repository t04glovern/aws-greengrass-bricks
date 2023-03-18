import logging
import time
import traceback

from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
from awsiot.greengrasscoreipc.model import (
    SubscriptionResponseMessage,
    UnauthorizedError
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def on_stream_event(event: SubscriptionResponseMessage) -> None:
    try:
        message = event.json_message.message
        topic = event.json_message.context.topic
        logger.info('Received new message on topic %s: %s' % (topic, message))
    except:
        traceback.print_exc()


def on_stream_error(error: Exception) -> bool:
    logger.error('Subscribe to topic stream error: %s', error)
    traceback.print_exc()
    return False  # Return True to close stream, False to keep stream open.


def on_stream_closed() -> None:
    logger.info('Subscribe to topic stream closed.')


# Keep the main thread alive, or the process will exit.
while True:
    topic = "devopstar/robocat/+/meow"

    try:
        ipc_client = GreengrassCoreIPCClientV2()
        # Subscription operations return a tuple with the response and the operation.
        _, operation = ipc_client.subscribe_to_topic(topic=topic, on_stream_event=on_stream_event,
                                                     on_stream_error=on_stream_error, on_stream_closed=on_stream_closed)
        logger.info("Subscribed to topic %s", topic)

        # Keep the main thread alive, or the process will exit.
        try:
            while True:
                time.sleep(10)
        except InterruptedError:
            logger.info("Interrupted, closing stream.")

        # To stop subscribing, close the stream.
        operation.close()
    except UnauthorizedError as e:
        logger.error("Failed to subscribe to topic %s: %s", topic, e)
        traceback.print_exc()
        exit(1)
    except Exception as e:
        logger.error("Failed to subscribe to topic %s: %s", topic, e)
        traceback.print_exc()
        exit(1)
