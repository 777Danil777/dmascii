FROM python:latest

WORKDIR /usr/web
ADD . /usr/web
RUN pip install -r /usr/web/requirements.txt
EXPOSE 5000
CMD python ascii.py