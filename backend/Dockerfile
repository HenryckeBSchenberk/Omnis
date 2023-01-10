FROM python:latest as builder

RUN apt-get update -y 
RUN /usr/local/bin/python -m pip install --upgrade pip
# RUN apt-get install ffmpeg pkg-config libsm6 libxext6 -y
# RUN apt-get install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev -y

COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

FROM python:latest
RUN apt-get update && apt-get install -y

RUN apt-get install ffmpeg pkg-config libsm6 libxext6 -y
COPY --from=builder /root/.local /root/.local
WORKDIR /app

ENV PATH=/root/.local:$PATH
