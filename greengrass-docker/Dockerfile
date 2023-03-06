FROM python:3.11-bullseye

RUN apt-get update && apt-get install -y cmake

COPY requirements.txt ./
RUN pip install -r ./requirements.txt

COPY src/robocat.py ./

CMD ["python", "robocat.py"]
