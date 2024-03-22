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
RUN pip install faiss-gpu 
# RUN pip install fairseq
RUN pip install gradio==3.34.0
RUN pip install ffmpeg
RUN pip install ffmpeg-python==0.2.0
RUN pip install praat-parselmouth==0.4.2
RUN pip install pyworld==0.3.2
RUN pip install numpy==1.23.5
RUN pip install numba==0.56.4
RUN pip install librosa==0.9.1
RUN pip3 download --cache-dir ./tmp/pipcache -r requirements.txt
RUN pip install --upgrade lxml
RUN pip install --upgrade ffmpy
WORKDIR /app/MangioRVC
RUN cd /app/MangioRVC
#RUN pip install -r requirements.txt