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

if [ $# -ne 3 ]; then
  echo 1>&2 "Usage: $0 COMPONENT-NAME COMPONENT-VERSION CONTAINER-TAG"
  exit 3
fi

COMPONENT_NAME=$1
COMPONENT_VERSION=$2
CONTAINER_TAG=$3

# copy recipe to greengrass-build
cp recipe.yaml ./greengrass-build/recipes

# create custom build directory
rm -rf ./custom-build
mkdir ./custom-build

# build Docker image
docker buildx build --platform linux/amd64,linux/arm/v7 -t $CONTAINER_TAG .

# save Docker images as tar
docker save --output ./custom-build/container.tar $CONTAINER_TAG

# zip up archive
zip -r -j -X ./custom-build/container.zip ./custom-build

# copy archive to greengrass-build
cp ./custom-build/container.zip ./greengrass-build/artifacts/$COMPONENT_NAME/$COMPONENT_VERSION/
