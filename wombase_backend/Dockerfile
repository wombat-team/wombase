FROM python:3.10

COPY ./server /opt/server
COPY manage.py docker-entrypoint.sh /opt/
COPY requirements.txt /opt/

ENV SECRET_KEY='${SECRET_KEY}'
ENV DB_NAME='${DB_NAME}'
ENV DB_USER='${DB_USER}'
ENV DB_PASSWORD='${DB_PASSWORD}'
ENV DB_HOST='${DB_HOST}'

WORKDIR /opt/

RUN pip install -r requirements.txt

CMD bash docker-entrypoint.sh

EXPOSE 8000