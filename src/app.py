import asyncio

from quart import Quart
from quart import Response
from quart import request
from requests import HTTPError

from service import WordCount

app = Quart(__name__)
word_count_service = WordCount()

# TODO: Document assumption regarding txt files + utf-8


@app.route("/word_counter", methods=['POST'])
async def word_counter() -> Response:
    """Receives a text input and counts the number of appearances for each word in the input."""
    if app.debug:
        # Print some useful stuff if we are debugging
        print(request.args.to_dict())
    try:
        input_type = request.args.get('type')
        input_string = request.args.get('input')
        option = word_count_service.get_option(input_type)
        asyncio.create_task(option(input_string))
    except (ValueError, HTTPError) as e:
        # TODO: More excepts should go here
        print(f"[Error] {e}")
        status_code = Response(response='', status=500)
    else:
        status_code = Response(response='', status=200)

    return status_code


@app.route("/word_statistics/<word>", methods=['GET'])
async def word_statistics(word: str):
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
