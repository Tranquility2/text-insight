"""
Word count service for Text Insight
"""
import tempfile
import validators
import redis
from celery import chain

from requests import HTTPError

from tasks import count_words_in_string, count_words_in_local_file, download_text_file


class WordCountService:
    """
    Word Count Service, handle flows for getting input text from URL, File ,String.
    """

    def __init__(self, logger):
        self.logger = logger
        self.logger.info(f"New -WordCountService-")
        self.rd = redis.Redis(host='localhost', port=6379, db=0)

    def get_word_count_from_redis(self, word: str):
        return self.rd.hget(f'known', word)

    @staticmethod
    def count_words_from_url(url: str):
        # First do some sanity on the input data
        if not validators.url(url):
            raise ValueError(f"The URL: {url} is not valid")

        chain(download_text_file.s(url=url,
                                   chunk_size=4096,
                                   base_path=tempfile.gettempdir()),
              count_words_in_local_file.s()).apply_async()

    def run_option(self, input_type: str, input_string: str):
        """ Run the word count option based on the input type."""
        options = {
            'string': count_words_in_string,    # Handel Simple
            'path': count_words_in_local_file,  # Handel Local File Path
            'url': self.count_words_from_url    # Handel URL
        }
        # First do some sanity on the input data
        if input_type not in options:
            self.logger.error("Unknown/Missing input type")
            return

        try:
            if input_type == 'string':
                count_words_in_string.apply_async(kwargs={'source_string': input_string})
            elif input_type == 'path':
                count_words_in_local_file.apply_async(kwargs={'file_path': input_string})
            elif input_type == 'url':
                self.count_words_from_url(url=input_string)
            else:
                raise Exception("Should not be here!")

        except (ValueError, HTTPError) as e:
            # TODO: More excepts should go here
            self.logger.error(f"[Error] {e}")
