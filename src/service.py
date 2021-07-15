"""
Word count service for Text Insight
"""
import re
import os
import tempfile
from typing import List

import validators
import redis

from os import path

from utils import timeit, read_in_chunks, download_text_file


class WordCountService:
    """
    Word Count Service, handle flows for getting input text from URL, File ,String.
    """

    def __init__(self, logger):
        self.logger = logger
        self.logger.info(f"New -WordCountService-")
        self.rd = redis.Redis(host='localhost', port=6379, db=0)

    def update_words_in_redis(self, words: List[str]):
        for word in words:
            self.rd.hincrby('known', word, 1)  # This is atomic

    def get_word_count_from_redis(self, word: str):
        return self.rd.hget('known', word)

    def count_words_in_string(self, source_string: str):
        # First do some sanity on the input data
        if not isinstance(source_string, str):
            raise ValueError("Source string is not valid")

        words = re.findall(r'\w+', source_string.lower())
        self.logger.debug(f"Found #{len(words)} elements")
        self.update_words_in_redis(words)

    @timeit
    def count_words_in_local_file(self, file_path: str):
        os_file_path = os.path.normcase(file_path)
        # First do some sanity on the input data
        if not path.isfile(os_file_path):
            raise ValueError(f"Could not find the file: {os_file_path}")

        with open(file_path, encoding='UTF-8') as f:
            for piece in read_in_chunks(file_object=f,
                                        chunk_size=1024 * 100):
                self.count_words_in_string(piece)

    @timeit
    def count_words_from_url(self, url: str):
        # First do some sanity on the input data
        if not validators.url(url):
            raise ValueError(f"The URL: {url} is not valid")

        local_filename = download_text_file(logger=self.logger,
                                            url=url,
                                            chunk_size=4096,
                                            base_path=tempfile.gettempdir())
        self.count_words_in_local_file(local_filename)

    def get_option(self, input_type: str):
        """ Get the option based on the input type.
         if not known - raise error. """
        options = {
            'string': self.count_words_in_string,       # Handel Simple
            'path': self.count_words_in_local_file,     # Handel Local File Path
            'url': self.count_words_from_url            # Handel URL
        }

        # First do some sanity on the input data
        if input_type not in options:
            raise ValueError("Unknown/Missing input type")

        return options.get(input_type)

