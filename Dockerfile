FROM python:3.11.6

ENV DockerHOME=/home/app/webapp

RUN mkdir -p ${DockerHOME}

WORKDIR ${DockerHOME}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . ${DockerHOME}