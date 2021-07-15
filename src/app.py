from flask import Flask
from flask import request

from werkzeug.utils import secure_filename
from requests import HTTPError

from service import WordCountService
from utils import get_file_size_friendly

app = Flask(__name__)
word_count_service = WordCountService()

# TODO: Document assumption regarding txt files + utf-8


@app.route("/ping", methods=['GET'])
def ping():
    return "pong"


@app.route("/upload", methods=['POST'])
def upload():
    try:
        file = request.files.get('file')
        if file:
            file_name = secure_filename(file.filename)
            file.save(file_name)
            print(f"Received file {file.filename}, Size={get_file_size_friendly(file_name)}")
            return f"{file.filename} saved successfully"
        else:
            return "Missing file"
    except (TypeError, KeyError) as e:
        # TODO: More excepts should go here
        print(f"[Error] {e}")
        return e


@app.route("/word_counter", methods=['POST'])
def word_counter():
    """Receives a text input and counts the number of appearances for each word in the input."""
    if app.debug:
        # Print some useful stuff if we are debugging
        print(request.args.to_dict())

    input_type = request.args.get('type')
    input_string = request.args.get('input')
    try:
        option = word_count_service.get_option(input_type)
        option(input_string)
    except (ValueError, HTTPError) as e:
        # TODO: More excepts should go here
        print(f"[Error] {e}")

    return 'Success', 200


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
