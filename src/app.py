from flask import Flask
from flask import request

from service import WordCountService

app = Flask(__name__)
word_count_service = WordCountService()

# TODO: Document assumption regarding txt files + utf-8


@app.route("/ping", methods=['GET'])
def ping():
    return "pong"


@app.route("/word_counter", methods=['POST'])
def word_counter():
    """Receives a text input and counts the number of appearances for each word in the input."""
    if app.debug:
        # Print some useful stuff if we are debugging
        print(request.args.to_dict())

    input_type = request.args.get('type')
    input_string = request.args.get('input')
    word_count_service.run_option(input_type, input_string)

    return 'Success'


@app.route("/word_statistics/<word>", methods=['GET'])
def word_statistics(word: str):
    """Receives a word and returns the number of times the word appeared so far
    (in all previous inputs)."""
    count = int(word_count_service.WORDS_COUNT.get(word) or 0)

    # The design docs asked for a number but for the debugging I prefer a nice info text :)
    if app.debug:
        return f'The word "{word}" appear {count} times'
    else:
        return count


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
