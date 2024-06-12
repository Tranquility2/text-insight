# Check if docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Docker does not seem to be running, run it first and retry"
    exit 1
fi
# Build
docker build --tag text_insight .
# Run
docker run --rm -p 5000:5000/tcp -it text_insight