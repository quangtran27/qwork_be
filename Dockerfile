# base image
FROM python:3.11.6

# environtment variable
ENV DockerHOME=/home/app/webapp

# set work 
RUN mkdir -p ${DockerHOME}

# where your code lives
WORKDIR ${DockerHOME}

# set environtment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# upgrade pip
RUN pip install --upgrade pip

# copy project to docker home dir
COPY . ${DockerHOME}

# install all depedencies
RUN pip install -r requirements.txt

# port of django app run
EXPOSE 8000

# run the server
CMD python guinicorn qwork_be.wgsi