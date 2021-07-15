"""
Backend APIs for Text Insight web service
"""
from flask import Flask
from flask import request

from werkzeug.utils import secure_filename
from requests import HTTPError

from service import WordCountService
from utils import get_file_size_friendly, config_logs


class BackendApi:
    def __init__(self):
        self.logger = config_logs(__name__)
        self.word_count_service = WordCountService(logger=self.logger)

    def get_app(self):
        app = Flask(__name__)

        @app.route("/ping", methods=['GET'])
        def ping():
            return "pong"

        @app.route("/upload", methods=['POST'])
        def upload():
            """
            Upload a file to local app dir
            """
            try:
                file = request.files.get('file')
                if file:
                    file_name = secure_filename(file.filename)
                    file.save(file_name)
                    self.logger.info(f"Received file {file.filename}, Size={get_file_size_friendly(file_name)}")
                    return f"{file.filename} saved successfully"
                else:
                    return "Missing file"
            except (TypeError, KeyError) as e:
                # TODO: More excepts should go here
                self.logger.error(f"[Error] {e}")
                return e

        @app.route("/word_counter", methods=['POST'])
        def word_counter():
            """Receives a text input and counts the number of appearances for each word in the input."""
            self.logger.debug(request.args.to_dict())

            input_type = request.args.get('type')
            input_string = request.args.get('input')
            try:
                option = self.word_count_service.get_option(input_type)
                option(input_string)
            except (ValueError, HTTPError) as e:
                # TODO: More excepts should go here
                self.logger.error(f"[Error] {e}")

            return 'Success'

        @app.route("/word_statistics/<word>", methods=['GET'])
        def word_statistics(word: str):
            """Receives a word and returns the number of times the word appeared so far
            (in all previous inputs)."""
            count = int(self.word_count_service.get_word_count_from_redis(word) or 0)

            # The design docs asked for a number but for the debugging I prefer a nice info text :)
            if app.debug:
                return f'The word "{word}" appear {count} times'
            else:
                return str(count)

        return app
