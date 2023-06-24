import json
import os
import boto3

"""
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity |  jq -r '.Account')
export AWS_REGION=ap-southeast-2

python deployment.json.py

aws greengrassv2 create-deployment \
    --output text \
    --no-paginate \
    --region ${AWS_REGION} \
    --cli-input-json file://deployment.json
"""

AWS_REGION = os.getenv('AWS_REGION')
if not AWS_REGION:
    raise ValueError("AWS_REGION environment variable not set.")

AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
if not AWS_ACCOUNT_ID:
    raise ValueError("AWS_ACCOUNT_ID environment variable not set.")

LATEST_COMPONENT_VERSION = os.getenv('LATEST_COMPONENT_VERSION')
if not LATEST_COMPONENT_VERSION:
    print("LATEST_COMPONENT_VERSION environment variable not set. Fetching latest component version from AWS if possible.")


def get_latest_component_version(component_name):
    greengrassv2 = boto3.client('greengrassv2', region_name=AWS_REGION)
    response = greengrassv2.list_component_versions(
        arn=f"arn:aws:greengrass:{AWS_REGION}:{AWS_ACCOUNT_ID}:components:{component_name}"
    )
    return response['componentVersions'][0]['componentVersion']


configuration = {
    "targetArn": f"arn:aws:iot:{AWS_REGION}:{AWS_ACCOUNT_ID}:thinggroup/robocat",
    "deploymentName": "Deployment for robocat group",
    "components": {
        "com.devopstar.Robocat": {
            "componentVersion": LATEST_COMPONENT_VERSION or get_latest_component_version("com.devopstar.Robocat"),
            "runWith": {},
            "configurationUpdate": {
                "reset": [""]
            }
        },
        "aws.greengrass.Nucleus": {
            "componentVersion": "2.10.3"
        },
        "aws.greengrass.Cli": {
            "componentVersion": "2.10.3"
        },
        "aws.greengrass.clientdevices.mqtt.Bridge": {
            "componentVersion": "2.2.6",
            "configurationUpdate": {
                "merge": json.dumps({
                    "mqttTopicMapping": {
                        "PetMapping": {
                            "topic": "devopstar/robocat/pet",
                            "source": "IotCore",
                            "target": "Pubsub"
                        },
                        "SpeakMapping": {
                            "topic": "devopstar/robocat/speak",
                            "source": "Pubsub",
                            "target": "IotCore"
                        },
                    }
                })
            },
            "runWith": {}
        },
        "aws.greengrass.LogManager": {
            "componentVersion": "2.3.4",
            "configurationUpdate": {
                "merge": json.dumps({
                    "logsUploaderConfiguration": {
                        "systemLogsConfiguration": {
                            "uploadToCloudWatch": "true",
                            "minimumLogLevel": "INFO",
                            "diskSpaceLimit": "10",
                            "diskSpaceLimitUnit": "MB",
                            "deleteLogFileAfterCloudUpload": "false"
                        },
                        "componentLogsConfigurationMap": {
                            "com.devopstar.Robocat": {
                                "minimumLogLevel": "INFO",
                                "diskSpaceLimit": "20",
                                "diskSpaceLimitUnit": "MB",
                                "deleteLogFileAfterCloudUpload": "false"
                            }
                        }
                    },
                    "periodicUploadIntervalSec": 300
                })
            },
            "runWith": {}
        },
        "aws.greengrass.LocalDebugConsole": {
            "componentVersion": "2.3.0",
            "configurationUpdate": {
                "merge": json.dumps({
                    "httpsEnabled": "false"
                })
            },
            "runWith": {}
        }
    },
    "deploymentPolicies": {
        "failureHandlingPolicy": "ROLLBACK",
        "componentUpdatePolicy": {
            "timeoutInSeconds": 60,
            "action": "NOTIFY_COMPONENTS"
        },
        "configurationValidationPolicy": {
            "timeoutInSeconds": 60
        }
    },
    "iotJobConfiguration": {}
}

with open('deployment.json', 'w') as json_file:
    json.dump(configuration, json_file, indent=4)
