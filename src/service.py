"""
Word count service for Text Insight
"""
import tempfile
import validators
import redis
import os

from celery import chain
from requests import HTTPError
from os import path

from tasks import count_words_in_string_task, count_words_in_local_file_task, download_text_file_task


class WordCountService:
    """
    Word Count Service, handle flows for getting input text from URL, File ,String.
    """

    def __init__(self, logger):
        self.logger = logger
        self.logger.info(f"New -WordCountService-")
        self.db = redis.Redis(host='localhost', port=6379, db=0)

    def get_word_count_from_redis(self, word: str):
        """ Fetch the word count from the DB"""
        return self.db.hget(f'known', word)

    @staticmethod
    def count_words_in_string(source_string: str):
        """ Wrapper for the task that counts words in a given string"""
        # First do some sanity on the input data
        if not isinstance(source_string, str):
            raise ValueError("Source string is not valid")

        count_words_in_string_task.apply_async(kwargs={'source_string': source_string})

    @staticmethod
    def count_words_in_local_file(file_path: str):
        """ Wrapper for the task that counts words in local file"""
        os_file_path = os.path.normcase(file_path)
        # First do some sanity on the input data
        if not path.isfile(os_file_path):
            raise ValueError(f"Could not find the file: {os_file_path}")

        count_words_in_local_file_task.apply_async(kwargs={'file_path': file_path})

    @staticmethod
    def count_words_from_url(url: str):
        """ Wrapper for the tasks that counts words based on a given URL.
        1st we download the file and then we count it ad a local file."""
        # First do some sanity on the input data
        if not validators.url(url):
            raise ValueError(f"The URL: {url} is not valid")
        # 1st Download and then count as a local file
        # TODO: file can be temporary
        chain(download_text_file_task.s(url=url,
                                        chunk_size=4096,
                                        base_path=tempfile.gettempdir()),
              count_words_in_local_file_task.s()).apply_async()

    def run_option(self, input_type: str, input_string: str):
        """ Run the word count option based on the input type."""
        options = {
            'string': count_words_in_string_task,    # Handel Simple
            'path': count_words_in_local_file_task,  # Handel Local File Path
            'url': self.count_words_from_url    # Handel URL
        }
        # First do some sanity on the input data
        if input_type not in options:
            self.logger.error("Unknown/Missing input type")
            return

        try:
            if input_type == 'string':
                self.count_words_in_string(source_string=input_string)
            elif input_type == 'path':
                self.count_words_in_local_file(file_path=input_string)
            elif input_type == 'url':
                self.count_words_from_url(url=input_string)
            else:
                raise Exception("Should not be here!")

        except (ValueError, HTTPError) as e:
            # More excepts should go here
            self.logger.error(f"[Error] {e}")
