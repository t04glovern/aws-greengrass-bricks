import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_caller_identity():
    try:
        session = boto3.Session()
        client = session.client('sts')
        response = client.get_caller_identity()
        return response
    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your credentials.")
        return None
    except ClientError as e:
        print(f"Error: {e}")
        return None


while True:
    time.sleep(30)
    response = get_caller_identity()
    if response:
        logger.info(response)
