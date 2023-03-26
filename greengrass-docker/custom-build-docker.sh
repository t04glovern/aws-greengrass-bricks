#!/bin/bash

# Custom GDK build script for Docker container builds
# produces:
# - a zip file containing the docker image as a tar file
# - [optional] a Docker image pushed to ECR

# These commands must create a recipe and artifacts in the following folders
# within the component folder. The GDK CLI creates these folders for you when
# you run the component build command.
#
# - Recipe folder: greengrass-build/recipes
# - Artifacts folder: greengrass-build/artifacts/componentName/componentVersion

# Default environment variables
CONTAINER_ARCH="linux/amd64"
CONTAINER_PUSH="false"
BUILDX_CACHE_DIR="/tmp/.buildx-cache"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --component-name=*)
      COMPONENT_NAME="${1#*=}"
      shift
      ;;
    --component-version=*)
      COMPONENT_VERSION="${1#*=}"
      shift
      ;;
    --container-name=*)
      CONTAINER_NAME="${1#*=}"
      shift
      ;;
    --container-arch=*)
      CONTAINER_ARCH="${1#*=}"
      shift
      ;;
    --container-push)
      CONTAINER_PUSH="true"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 3
      ;;
  esac
done

if [[ -z "$COMPONENT_NAME" || -z "$COMPONENT_VERSION" || -z "$CONTAINER_NAME" ]]; then
  cat <<-EOF
Usage: $0 --component-name=<name>
          --component-version=<version>
          --container-name=<name>
          [--container-arch=<arch>]
          [--container-push]
EOF
  exit 3
fi

if [ "$CONTAINER_PUSH" == "false" ]; then
  echo "WARNING: Container will not be pushed to ECR. Use --container-push to push to ECR."
elif [ "$CONTAINER_PUSH" == "true" ]; then
  if [[ -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" || -z "$AWS_REGION" ]]; then
    echo "ERROR: AWS credentials not set. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_REGION."
    exit 3
  fi
  AWS_ACCOUNT_ID=$(aws sts get-caller-identity |  jq -r '.Account')
  AWS_REGION=$(aws configure get region --output text)
  echo "Using AWS account ID: $AWS_ACCOUNT_ID and region: $AWS_REGION to push container to ECR"
fi

# copy recipe to greengrass-build
cp recipe.yaml ./greengrass-build/recipes

# create custom build directory
rm -rf ./custom-build
mkdir ./custom-build

# Create builder instance
docker buildx create --name greengrass-docker-builder \
  --platform $CONTAINER_ARCH \
  --use

# build & save Docker image to tar file 
docker buildx build \
  --platform $CONTAINER_ARCH \
  --cache-to "type=local,dest=$BUILDX_CACHE_DIR" \
  --cache-from "type=local,src=$BUILDX_CACHE_DIR" \
  --output "type=docker,push=false,name=$CONTAINER_NAME,dest=./custom-build/container.tar" .

if [ "$CONTAINER_PUSH" == "true" ]; then
  # create ECR repository, ignore error if it already exists
  aws ecr create-repository --repository-name $CONTAINER_NAME --region $AWS_REGION || true
  # build & push Docker image to ECR
  aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
  docker buildx build \
    --platform $CONTAINER_ARCH \
    --cache-to "type=local,dest=$BUILDX_CACHE_DIR" \
    --cache-from "type=local,src=$BUILDX_CACHE_DIR" \
    --output "type=registry,name=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$CONTAINER_NAME:latest" .
fi

# Remove builder instance
docker buildx rm greengrass-docker-builder

# zip up archive
zip -r -j -X ./custom-build/container.zip ./custom-build

# copy archive to greengrass-build
cp ./custom-build/container.zip ./greengrass-build/artifacts/$COMPONENT_NAME/$COMPONENT_VERSION/
