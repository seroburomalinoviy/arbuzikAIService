FROM python:3.10-bullseye as builder

WORKDIR /app
COPY ./requirements.txt /app

# from makefile of the vanialla repo:
#apt-get -y install build-essential python3-dev ffmpeg
#pip install --upgrade setuptools wheel
#pip install --upgrade pip
#pip install faiss-gpu fairseq gradio ffmpeg ffmpeg-python praat-parselmouth pyworld numpy==1.23.5 numba==0.56.4 librosa==0.9.1
#pip install -r requirements.txt
#pip install --upgrade lxml
#pip install --upgrade ffmpy
#apt-get update
#apt -y install -qq aria2

# 1 - linux packeages will be installed in the target stage
# 2 - the pip install packages to the site-packages directory
RUN apt-get -y install build-essential python3-dev
RUN pip install --upgrade setuptools wheel
RUN pip install --upgrade pip
RUN pip install faiss-gpu fairseq gradio ffmpeg ffmpeg-python praat-parselmouth pyworld numpy==1.23.5 numba==0.56.4 librosa==0.9.1
RUN pip install -r requirements.txt
RUN pip install --upgrade lxml
RUN pip install --upgrade ffmpy




FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu24.04
RUN apt-get -y install build-essential python3-dev ffmpeg


COPY --from=builder /root/.local/lib/python3.10/site-packages /root/.local/lib/python3.10/site-packages


RUN apt-get update
RUN apt -y install -qq aria2