import asyncio
import time
import logging
import random
import json
import sys

from datetime import datetime

from greengrasssdk.stream_manager import (
    StreamManagerClient,
    StreamManagerException
)

steam_name = "BatchMessageStream"
stream_manager_client = StreamManagerClient()

logging.basicConfig(level=logging.INFO)

speed = 50
temperature = 25
location = {'lat': -31.976056, 'lng': 115.9113084}


def generate_random_json(id, speed, temperature, location):
    speed += random.randint(-5, 5)
    temperature = round(temperature + random.uniform(-0.5, 0.5), 2)
    location['lat'] += random.uniform(-0.0001, 0.0001)
    location['lng'] += random.uniform(-0.0001, 0.0001)
    return json.dumps({
        "id": id,
        "timestamp": datetime.now().isoformat(),
        "speed": speed,
        "temperature": temperature,
        "location": location
    }).encode(), speed, temperature, location


if __name__ == "__main__":
    # args : enabled, frequency
    if len(sys.argv) == 3:
        enabled = bool(sys.argv[1])
        frequency = float(sys.argv[2])

        logging.info(f"enabled: {enabled}, frequency: {frequency}")

        try:
            while True:
                if enabled:
                    message, speed, temperature, location = generate_random_json("1", speed, temperature, location)
                    try:
                        sequence_number = stream_manager_client.append_message(
                            stream_name=steam_name, data=message)
                        logging.info(
                            f"Message published to Stream Manager: {steam_name} - sequence number: {sequence_number}")
                    except StreamManagerException:
                        logging.error("StreamManagerException occurred", exc_info=True)
                    except (ConnectionError, asyncio.TimeoutError):
                        logging.error(
                            "Connection or Timeout error occurred", exc_info=True)
                time.sleep(frequency)
        except:
            logging.error("Exception occurred", exc_info=True)
    else:
        logging.error(f'2 argument required, only {len(sys.argv)-1} provided.')