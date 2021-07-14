import re
import os
import tempfile
import validators

from collections import Counter
from os import path

from flask import Flask
from flask import Response
from flask import request

from src.utils import timeit, read_in_chunks, download_text_file

app = Flask(__name__)

WORDS_COUNT = Counter()

# TODO: Document assumption regarding txt files + utf-8


@timeit
def count_words_in_blob(source_string: str):
    # First do some sanity on the input data
    if not isinstance(source_string, str):
        raise ValueError("Source string is not valid")

    words = re.findall(r'\w+', source_string.lower())
    WORDS_COUNT.update(words)

    if app.debug:
        print(f"Added #{len(words)} elements to the Counter")


@timeit
def count_words_in_local_file(file_path: str):
    os_file_path = os.path.normcase(file_path)
    # First do some sanity on the input data
    if not path.isfile(os_file_path):
        raise ValueError(f"Could not find the file: {os_file_path}")

    with open(file_path, encoding='UTF-8') as f:
        for piece in read_in_chunks(file_object=f, chunk_size=1024 * 1024):
            count_words_in_blob(piece)


@timeit
def count_words_from_url(url: str):
    # First do some sanity on the input data
    if not validators.url(url):
        raise ValueError(f"The URL: {url} is not valid")

    local_filename = download_text_file(url, chunk_size=4096, base_path=tempfile.gettempdir())
    count_words_in_local_file(local_filename)


@app.route("/word_counter", methods=['POST'])
def word_counter() -> Response:
    """Receives a text input and counts the number of appearances for each word in the input."""
    if app.debug:
        # Print some useful stuff if we are debugging
        print(request.args.to_dict())

    try:
        # Simple
        simple_string = request.args.get('string')
        if simple_string:
            count_words_in_blob(simple_string)

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

    # The design docs asked for a number but for the debugging I prefer a nice info text :)
    if app.debug:
        return f'The word "{word}" appear {count} times'
    else:
        return count


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
