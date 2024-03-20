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
RUN pip install gradio
RUN pip install ffmpeg
RUN pip install ffmpeg-python
RUN pip install praat-parselmouth
RUN pip install pyworld
RUN pip install numpy==1.23.5
RUN pip install numba==0.56.4
RUN pip install librosa==0.9.1
RUN pip install -r requirements.txt
RUN pip install --upgrade lxml
RUN pip install --upgrade ffmpy
#RUN pip install -r requirements.txt