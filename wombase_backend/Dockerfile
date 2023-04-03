FROM python:3.10

COPY ./server /opt/server
COPY manage.py docker-entrypoint.sh /opt/
COPY requirements.txt /opt/

WORKDIR /opt/

RUN pip install -r requirements.txt

CMD bash docker-entrypoint.sh