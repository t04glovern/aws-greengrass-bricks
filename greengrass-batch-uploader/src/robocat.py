import asyncio
import time
import logging
import random
import json
import sys

from datetime import datetime, timezone

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
    # Ensure speed does not go below 0
    speed += random.randint(0, 5)
    speed = max(0, speed)

    # Ensure temperature stays between -10 and 60 degrees
    temperature = round(temperature + random.uniform(-0.5, 0.5), 2)
    temperature = max(-10, min(60, temperature))

    location['lat'] += random.uniform(-0.001, 0.001)
    location['lng'] += random.uniform(-0.001, 0.001)

    return json.dumps({
        "id": id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed": speed,
        "temperature": temperature,
        "location": location
    }).encode(), speed, temperature, location


if __name__ == "__main__":
    # args : enabled, frequency
    if len(sys.argv) == 3:
        if sys.argv[1] == "true":
            enabled = True
        else:
            enabled = False
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
