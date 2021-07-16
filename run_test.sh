# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker does not seem to be running, run it first and retry"
    exit 1
fi

# Check if httpie is running
if ! http --version > /dev/null 2>&1; then
    echo "Httpie does not seem to be running, run it first and retry"
    exit 1
fi

BASE_POST_URL_COMMAND="http --print b POST 0.0.0.0:5000"
BASE_GET_URL_COMMAND="http --print b GET 0.0.0.0:5000"
TEST_STRING_1="Hi! My name is (what?), my name is (who?), my name is Slim Shady"

function cleanup {
  docker kill "$id" > /dev/null 2>&1
  echo "-> Cleanup Done"
}
trap cleanup EXIT

function upload_file() {
  upload=$(http --form --print b POST 0.0.0.0:5000/upload file@"$1")
  printf '%s\n' "$upload"
  #TODO: add some more sanity on upload
}

function test_word_count() {
  printf 'Running Test Word Count\ntype=%s input=%s\nExpected_Result=%s |' "$1" "$2" "$3"
  res=$($BASE_POST_URL_COMMAND/word_counter type=="$1" input=="$2")
  if [ "$res" == "$3" ]; then
    echo " worked 💙"
  else
    echo " failed ✕ (got $res)"
    exit 1
  fi
}

function test_word_statistics() {
  printf 'Running Test Word Statistics woth the word: %s\nExpected_Result=%s |' "$1" "$2"
  res=$($BASE_GET_URL_COMMAND/word_statistics/"$1")
  if [ "$res" == "$2" ]; then
    echo " success 💙"
  else
    echo " failed ✕ (got $res)"
    exit 1
  fi
}

echo "*** Running Tests ***"

echo "-> Building"
docker build --tag text_insight . > /dev/null 2>&1
echo "-> Running"
id=$(docker run --rm -p 5000:5000/tcp -d text_insight)
echo "-> Warmup..."
sleep 5 # NOTE: you may need to set this to a higher number

# String test
test_word_count "string" "$TEST_STRING_1" "Success"
test_word_statistics "my" 3
test_word_statistics "what" 1
test_word_statistics "hello" 0

# Local file Test
echo "-> Uploading test file"
upload_file ./tmp/hamlet.txt
test_word_count "path" "hamlet.txt" "Success"
test_word_statistics "lord" 0 # Not updated yet, need to give it some time to process
echo "-> Waiting on update"
sleep 2 # NOTE: you may need to set this to a higher number
test_word_statistics "lord" 226
test_word_statistics "good" 109

# URL Test
test_word_count "url" "https://norvig.com/big.txt" "Success"
echo "-> Waiting on update"
sleep 10 # NOTE: you may need to set this to a higher number
test_word_statistics "in" 22474

echo "*** All tests are successful 😊 ***"

# Another cool test: https://www.gutenberg.org/files/1524/1524-0.txt