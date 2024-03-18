FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
# RUN apt install redis-server