FROM python:2.7.9

RUN mkdir -p /var/www/carcassonne
WORKDIR /var/www/carcassonne
ADD requirements.txt /var/www/carcassonne/
RUN pip install -r requirements.txt
ADD . /var/www/carcassonne
