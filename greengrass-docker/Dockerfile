FROM python:3.9-bullseye

RUN apt-get update && apt-get install -y cmake

COPY requirements.txt ./
RUN pip install -r ./requirements.txt

COPY src/robocat_pub.py ./

CMD ["python", "robocat_pub.py"]
