from collections import Counter
from flask import Flask
from flask import Response
from flask import request
from requests import HTTPError

from src.service import WordCount

app = Flask(__name__)
word_count_service = WordCount()

# TODO: Document assumption regarding txt files + utf-8


@app.route("/word_counter", methods=['POST'])
def word_counter() -> Response:
    """Receives a text input and counts the number of appearances for each word in the input."""
    if app.debug:
        # Print some useful stuff if we are debugging
        print(request.args.to_dict())

    try:
        # Handel Simple
        simple_string = request.args.get('string')
        if simple_string:
            word_count_service.count_words_in_blob(simple_string)

        # Handel Local File Path
        local_file_path = request.args.get('path')
        if local_file_path:
            word_count_service.count_words_in_local_file(local_file_path)

        # Handel URL
        url = request.args.get('url')
        if url:
            word_count_service.count_words_from_url(url)

    except (ValueError, HTTPError) as e:
        # TODO: More excepts should go here
        print(f"Error: {e}")
        status_code = Response(status=500)
    else:
        status_code = Response(status=200)

    return status_code


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
