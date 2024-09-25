FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get --no-install-recommends -y install build-essential python3-dev ffmpeg && \
rm -rf /var/cache/apt  && apt clean && rm -rf /var/lib/apt/lists/*
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --no-deps -r requirements.txt && pip install --no-cache-dir -v "torch==2.0.0" && \
pip install --upgrade pip && pip install --no-cache-dir --upgrade setuptools wheel && \
pip install --upgrade --no-cache-dir lxml && pip install --no-cache-dir --upgrade ffmpy
# RUN apt-get update && apt-get -y install build-essential python3-dev ffmpeg && \
# rm -rf /var/cache/apt  && apt clean && rm -rf /var/lib/apt/lists/*
# RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade setuptools wheel && \
# pip install --upgrade --no-cache-dir lxml && pip install --no-cache-dir --upgrade ffmpy
# RUN pip install --upgrade lxml && pip install --upgrade ffmpy
COPY . /app
