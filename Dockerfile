FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04
FROM python:3.9-slim

RUN apt-get update && apt-get install -y git
RUN apt-get install -y ffmpeg
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
CMD ["python", "test.py"]
