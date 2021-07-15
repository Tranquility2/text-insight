FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./src .

EXPOSE 5000

CMD [ "hypercorn", "--bind", "0.0.0.0:5000", "app:app"]