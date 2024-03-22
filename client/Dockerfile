FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt-get -y install build-essential python3-dev ffmpeg
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools wheel
# RUN pip install fairseq
RUN pip install -r requirements.txt
RUN pip install --upgrade lxml
RUN pip install --upgrade ffmpy