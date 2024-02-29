FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY django_bot /app
COPY client /app
COPY pre_client /app
RUN pip install --upgrade pip && pip install -r requirements.txt