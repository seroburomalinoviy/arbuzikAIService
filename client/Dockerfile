FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get -y install build-essential python3-dev ffmpeg
RUN pip install --upgrade pip && pip install --upgrade setuptools wheel
RUN pip install --upgrade lxml && pip install --upgrade ffmpy