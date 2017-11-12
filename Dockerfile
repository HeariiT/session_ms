FROM ubuntu:latest
MAINTAINER Juan Vivero "jsviveroj@unal.edu.co"


RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install --upgrade pip


COPY . /app
WORKDIR /app

RUN apt-get -y install  python-mysqldb
RUN pip install -r requirements.txt



ENTRYPOINT ["python"]
CMD ["session.py"]
