FROM ubuntu:20.04

WORKDIR /workplace

COPY . .

RUN apt-get update
RUN apt-get install -y python3.8 python3.8-dev python3-pip libpq-dev
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
