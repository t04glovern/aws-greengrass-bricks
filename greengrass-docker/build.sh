# Custom GDK build script
# Documentation: https://docs.aws.amazon.com/greengrass/v2/developerguide/gdk-cli-configuration-file.html
# Script based on: https://github.com/awslabs/aws-greengrass-labs-local-web-server/blob/main/build-custom.sh

# These commands must create a recipe and artifacts in the following folders
# within the component folder. The GDK CLI creates these folders for you when
# you run the component build command.
#
# - Recipe folder: greengrass-build/recipes
# - Artifacts folder: greengrass-build/artifacts/componentName/componentVersion
#
# Replace componentName with the component name, and replace componentVersion with
# the component version or NEXT_PATCH.

if [ $# -ne 2 ]; then
  echo 1>&2 "Usage: $0 COMPONENT-NAME COMPONENT-VERSION"
  exit 3
fi

COMPONENT_NAME=$1
COMPONENT_VERSION=$2

# copy recipe to greengrass-build
cp recipe.yaml ./greengrass-build/recipes

# create custom build directory
rm -rf ./custom-build
mkdir ./custom-build

# Create builder instance
docker buildx create --name greengrass-docker-builder \
  --platform linux/arm/v7 \
  --use

# build & save Docker image to tar file 
docker buildx build \
  --platform linux/arm/v7 \
  --cache-to "type=local,dest=/tmp/.buildx-cache" \
  --cache-from "type=local,src=/tmp/.buildx-cache" \
  --output "type=docker,push=false,name=robocatcontainer,dest=./custom-build/container.tar" .

# build & push Docker image to ECR
aws ecr get-login-password --region ap-southeast-2 | \
docker login --username AWS --password-stdin 536829251200.dkr.ecr.ap-southeast-2.amazonaws.com
docker buildx build \
  --platform linux/arm/v7 \
  --cache-to "type=local,dest=/tmp/.buildx-cache" \
  --cache-from "type=local,src=/tmp/.buildx-cache" \
  --output "type=registry,name=536829251200.dkr.ecr.ap-southeast-2.amazonaws.com/robocatcontainer:latest" .

# Remove builder instance
docker buildx rm greengrass-docker-builder

# zip up archive
zip -r -j -X ./custom-build/container.zip ./custom-build

# copy archive to greengrass-build
cp ./custom-build/container.zip ./greengrass-build/artifacts/$COMPONENT_NAME/$COMPONENT_VERSION/
