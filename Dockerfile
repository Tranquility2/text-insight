FROM ubuntu:18.04

# Install packages
RUN apt update && apt install nginx python3 python3-pip redis-server -y

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./src .
COPY run_server.sh .

# Update nginx conf
COPY ./conf/nginx.conf /etc/nginx/conf.d/nginx.conf
# Remove nginx default conf
RUN echo > /etc/nginx/sites-available/default

EXPOSE 5000

CMD /etc/init.d/nginx start && ./run_server.sh;