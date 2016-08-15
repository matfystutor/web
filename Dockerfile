FROM python:2.7


RUN apt-get update
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y python-mysqldb

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install mysql-python
ADD . /code/