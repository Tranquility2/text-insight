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

    options = {
        'string': word_count_service.count_words_in_string,       # Handel Simple
        'path': word_count_service.count_words_in_local_file,   # Handel Local File Path
        'url':  word_count_service.count_words_from_url         # Handel URL
    }

    def raise_(ex):
        """Simple raiser to help with the lambda.
        (as we cannot raise in lambda but we can invoke a method)"""
        raise ex

    try:
        input_type = request.args.get('type')
        # Get the option based on the input type, if not found raise error
        option = options.get(input_type,
                             lambda x: raise_(ValueError("Unknown/Missing input type")))
        option(request.args.get('input'))
    except (ValueError, HTTPError) as e:
        # TODO: More excepts should go here
        print(f"[Error] {e}")
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
