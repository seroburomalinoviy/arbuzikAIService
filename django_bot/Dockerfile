FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
RUN mkdir -p /app/static
WORKDIR /app
COPY requirements.txt /app
RUN apt install ffmpeg && pip install --upgrade pip && pip install -r requirements.txt
COPY . /app
