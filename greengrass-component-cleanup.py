#!/usr/bin/env python

import boto3
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--thing-group', dest='thing_group', default=None,
                    help='Thing group name')
parser.add_argument('--account-id', dest='account_id', default=None,
                    help='AWS account ID')
parser.add_argument('--bucket-name', dest='bucket_name', required=True,
                    help='S3 bucket name')
parser.add_argument('--region', dest='region', default=None,
                    help='AWS region')
parser.add_argument('--thing-name', dest='thing_name', default=None,
                    help='Thing name')
args = parser.parse_args()

if args.thing_group is None and args.thing_name is None:
    parser.error('Please specify either --thing-group or --thing-name')

# Define the S3 bucket name and the AWS Region it is located in
s3_bucket_name = args.bucket_name
if args.region is None:
    session = boto3.Session()
    aws_region = session.region_name
else:
    aws_region = args.region

# Define the GreengrassV2 client
session = boto3.Session(region_name=aws_region)
greengrass_client = session.client('greengrassv2')

# Define the S3 resource
s3_resource = session.resource('s3')

if args.account_id is None:
    sts_client = session.client('sts')
    account_id = sts_client.get_caller_identity()['Account']
else:
    account_id = args.account_id

# Get a list of all components in GreengrassV2
components_response = greengrass_client.list_components()
components = components_response['components']

# Loop through each component
for component in components:
    component_name = component['componentName']

    # Get the latest component version in use
    if args.thing_name is not None:
        target_arn = f'arn:aws:iot:{aws_region}:{account_id}:thing/{args.thing_name}'
    else:
        target_arn = f'arn:aws:iot:{aws_region}:{account_id}:thinggroup/{args.thing_group}'
    deployments_response = greengrass_client.list_deployments(
        targetArn=target_arn,
        historyFilter='LATEST_ONLY'
    )
    latest_deployment_id = deployments_response['deployments'][0]['deploymentId']
    deployment_response = greengrass_client.get_deployment(
        deploymentId=latest_deployment_id
    )
    component_versions_in_use = deployment_response['components']
    if component_name not in component_versions_in_use:
        latest_component_version = 'NONE'
    else:
        latest_component_version = component_versions_in_use[component_name]['componentVersion']

    # Get a list of all component versions in the S3 bucket for this component
    prefix = component_name + '/'
    component_versions_response = s3_resource.Bucket(s3_bucket_name).objects.filter(Prefix=prefix)

    # Loop through each component version
    for component_version in component_versions_response:
        component_version_key = component_version.key
        version_regex = r'(?<=/)\d+\.\d+\.\d+' # Regex to match the version number
        component_version_number = re.search(version_regex, component_version_key).group(0)

        # Check if this component version is not the latest version in use
        if component_version_number != latest_component_version:

            # Delete the component version in the S3 bucket
            s3_bucket = s3_resource.Bucket(s3_bucket_name)
            s3_bucket.objects.filter(Prefix=component_version_key).delete()
            print(f'Deleted S3 objects under: {component_version_key}')

            # Delete the component version in GreengrassV2
            greengrass_client.delete_component(
                arn='{}:versions:{}'.format(component['arn'], component_version_number)
            )
            print(f'Deleted GreengrassV2 component version: {component_version_number}')
