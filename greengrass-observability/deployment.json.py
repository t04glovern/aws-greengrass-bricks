import json
import os

AWS_REGION = os.getenv('AWS_REGION')
if not AWS_REGION:
    raise ValueError("AWS_REGION environment variable not set.")

AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
if not AWS_ACCOUNT_ID:
    raise ValueError("AWS_ACCOUNT_ID environment variable not set.")

LATEST_COMPONENT_VERSION = os.getenv('LATEST_COMPONENT_VERSION')
if not LATEST_COMPONENT_VERSION:
    raise ValueError("LATEST_COMPONENT_VERSION environment variable not set.")


mqttBridge_config = {
    "mqttTopicMapping": {
        "StatMapping": {
            "topic": "devopstar/robocat/pet",
            "source": "IotCore",
            "target": "Pubsub"
        }
    }
}

logManager_config = {
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
                "logFileRegex": "com\.devopstar\.Robocat(_\\d{4}_\\d{1,2}_\\d{1,2}_\\d{1,2}_\\d{1,2})?\.log",
                "minimumLogLevel": "INFO",
                "diskSpaceLimit": "20",
                "diskSpaceLimitUnit": "MB",
                "deleteLogFileAfterCloudUpload": "false"
            }
        }
    },
    "periodicUploadIntervalSec": 300
}

configuration = {
    "targetArn": f"arn:aws:iot:{AWS_REGION}:{AWS_ACCOUNT_ID}:thinggroup/robocat",
    "deploymentName": "Deployment for robocat group",
    "components": {
        "com.devopstar.Robocat": {
            "componentVersion": LATEST_COMPONENT_VERSION,
            "runWith": {},
            "configurationUpdate": {
                "reset": [""]
            }
        },
        "aws.greengrass.Nucleus": {
            "componentVersion": "2.10.1"
        },
        "aws.greengrass.clientdevices.mqtt.Bridge": {
            "componentVersion": "2.2.5",
            "configurationUpdate": {
                "merge": json.dumps(mqttBridge_config)
            },
            "runWith": {}
        },
        "aws.greengrass.LogManager": {
            "componentVersion": "2.3.3",
            "configurationUpdate": {
                "merge": json.dumps(logManager_config)
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
