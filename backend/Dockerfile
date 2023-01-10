FROM python:latest as builder

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

FROM python:latest as main

RUN apt-get update && apt-get install --no-install-recommends ffmpeg pkg-config libsm6 libxext6 -y
COPY --from=builder /root/.local /root/.local
WORKDIR /app

ENV PATH=/root/.local:$PATH
