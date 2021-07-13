import re
import os
import validators

from collections import Counter
from os import path

from flask import Flask
from flask import Response
from flask import request
from urllib import request as url_request

app = Flask(__name__)

WORDS_COUNT = Counter()


def count_words_in_string(source_string: str):
    # First do some sanity on the input data
    if not isinstance(source_string, str):
        raise ValueError("Source string is not valid")

    words = re.findall(r'\w+', source_string.lower())
    WORDS_COUNT.update(words)

    if app.debug:
        print(f"Added #{len(words)} elements to the Counter")


def count_words_in_local_file(file_path: str):
    os_file_path = os.path.normcase(file_path)
    # First do some sanity on the input data
    if not path.isfile(os_file_path):
        raise ValueError(f"Could not find the file: {os_file_path}")

    # TODO: This is very inefficient, try with reuse count_words_in_string
    words = re.findall(r'\w+', open(os_file_path).read().lower())
    WORDS_COUNT.update(words)

    if app.debug:
        print(f"Added #{len(words)} elements to the Counter")


def count_words_from_url(url: str):
    # First do some sanity on the input data
    if not validators.url(url):
        raise ValueError(f"The URL: {url} is not valid")

    words_counter = 0

    file = url_request.urlopen(url)
    for line in file:
        decoded_line = line.decode("utf-8")
        words = re.findall(r'\w+', decoded_line.lower())
        words_counter += len(words)
        WORDS_COUNT.update(words)

    if app.debug:
        print(f"Added #{words_counter} elements to the Counter")


@app.route("/word_counter", methods=['POST'])
def word_counter():
    """Receives a text input and counts the number of appearances for each word in the input."""
    if app.debug:
        # Print some useful stuff if we are debugging
        print(request.args.to_dict())

    try:
        # Simple
        simple_string = request.args.get('string')
        if simple_string:
            count_words_in_string(simple_string)

        # File Path (local)
        local_file_path = request.args.get('path')
        if local_file_path:
            count_words_in_local_file(local_file_path)

        # URL
        url = request.args.get('url')
        if url:
            count_words_from_url(url)

    except ValueError as e:
        print(f"Error: {e}")
        status_code = Response(status=500)
    else:
        status_code = Response(status=200)

    return status_code


@app.route("/word_statistics/<word>", methods=['GET'])
def word_statistics(word: str):
    """Receives a word and returns the number of times the word appeared so far
    (in all previous inputs)."""

    count = int(WORDS_COUNT.get(word) or 0)

    if app.debug:
        return f'The word "{word}" appear {count} times'
    else:
        return count


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
