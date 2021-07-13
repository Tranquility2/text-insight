docker build --tag text_insight .

docker run --rm -p 5000:5000/tcp -it text_insight