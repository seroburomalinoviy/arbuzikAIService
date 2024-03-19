FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN apt-get update
RUN apt-get -y install build-essential python3-dev ffmpeg
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools wheel
# RUN pip install --upgrade pip
RUN pip install faiss-gpu fairseq gradio ffmpeg ffmpeg-python praat-parselmouth pyworld numpy==1.23.5 numba==0.56.4 librosa==0.9.1
RUN pip install -r requirements.txt
RUN pip install --upgrade lxml
RUN pip install --upgrade ffmpy
RUN pip install -r requirements.txt