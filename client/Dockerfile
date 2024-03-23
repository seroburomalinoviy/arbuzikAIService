FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get -y install build-essential python3-dev ffmpeg
RUN pip install --upgrade pip && pip install --upgrade setuptools wheel
RUN pip install -r requirements.txt
RUN pip install --upgrade lxml && pip install --upgrade ffmpy