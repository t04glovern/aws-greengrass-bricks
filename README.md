# AWS IoT Greengrass Bricks (v2)

This repository contains a set of good pratices and examples when working with AWS IoT Greengrass (v2). It is built ontop of some work i've done previously in this space for [Greengrass (v1) called aws-greener-grass](https://github.com/t04glovern/aws-greener-grass)

## Contents

* [01 - Setting up an AWS IoT Greengrass v2 Learning environment](#basic-setup) - **This step is mandatory** for ALL other tutorials in this repository
* [02 - Using Github Actions for AWS IoT Greengrass v2 Continuous Deployment](./greengrass-cicd)

## Basic Setup

Run the following from your Greengrass device (make sure you have AWS Credentials setup in on the device before running)

```bash
curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip > greengrass-nucleus-latest.zip && unzip greengrass-nucleus-latest.zip -d GreengrassCore

export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
export AWS_REGION="ap-southeast-2"
export GREENGRASS_THING_GROUP="robocat"
export GREENGRASS_THING_NAME="robocat-01"

# For more: https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html#install-greengrass-v2
sudo -E java \
  -Droot="/greengrass/v2" \
  -Dlog.store=FILE -jar ./GreengrassCore/lib/Greengrass.jar \
  --aws-region ${AWS_REGION} \
  --thing-name ${GREENGRASS_THING_NAME} \
  --thing-group-name ${GREENGRASS_THING_GROUP} \
  --thing-policy-name GreengrassV2IoTThingPolicy \
  --tes-role-name GreengrassV2TokenExchangeRole \
  --tes-role-alias-name GreengrassCoreTokenExchangeRoleAlias \
  --component-default-user ggc_user:ggc_group \
  --provision true \
  --setup-system-service true \
  --deploy-dev-tools true
```

The following commands don't have to be run on the device, however you should run them from the root directory of this repository

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity |  jq -r '.Account')
export AWS_REGION="ap-southeast-2"

# Creates IAM policy that can be attached to roles
envsubst < "device-policy.json.template" > "device-policy.json"
aws iam create-policy \
    --policy-name GreengrassV2ComponentArtifactPolicy \
    --policy-document file://device-policy.json \
    --region ${AWS_REGION}

# [SKIP] Only run if you need to update the policy
aws iam create-policy-version \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/GreengrassV2ComponentArtifactPolicy \
    --policy-document file://device-policy.json \
    --set-as-default

aws iam attach-role-policy \
    --role-name GreengrassV2TokenExchangeRole \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/GreengrassV2ComponentArtifactPolicy \
    --region ${AWS_REGION}
```
