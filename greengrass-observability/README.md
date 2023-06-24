# Greengrass Observability

```bash
pip install -r requirements-dev.txt
```

## Build and Deploy

```bash
pip install -r requirements-dev.txt
gdk component build
gdk component deploy
```

## Local Debug Console

```bash
ssh -L 1441:localhost:1441 -L 1442:localhost:1442 <user>@<your-greengrass-core-ip>
sudo /greengrass/v2/bin/greengrass-cli get-debug-password
# Username: debug
# Password: O95f8XULvRlJ-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Password expires at: 2023-06-24T22:51:26.541950941+08:00
```

Open [http://localhost:1441](http://localhost:1441) in your browser, logging in with the credentials above.
