# greengrass-batch-uploader

## Deploy

```bash
git clone https://github.com/t04glovern/aws-greengrass-bricks.git
cd aws-greengrass-bricks/greengrass-batch-uploader/sam

pip3 install aws-sam-cli==1.94.0

sam validate --lint
sam build

sam deploy --parameter-overrides \
    Name=robocat-greengrass \
    IcebergTableName=greengrass_data_iceberg \
    DatabaseName=default
```
