FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r ./requirements.txt

COPY src/robocat_pub.py ./
COPY src/robocat_sub.py ./

ENTRYPOINT [ "python" ]
CMD ["robocat_pub.py"]
