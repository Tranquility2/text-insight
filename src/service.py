import re
import os
import tempfile
from typing import Callable

import validators

from collections import Counter
from os import path

from utils import timeit, read_in_chunks, download_text_file


class WordCount:
    """
    Word Count Service, handle flows for getting input text from URL, File ,String.
    """
    WORDS_COUNT = Counter()

    #@timeit
    async def count_words_in_string(self, source_string: str):
        # First do some sanity on the input data
        if not isinstance(source_string, str):
            raise ValueError("Source string is not valid")

        words = re.findall(r'\w+', source_string.lower())
        self.WORDS_COUNT.update(words)

        # TODO: Print only on debug
        print(f"Added #{len(words)} elements to the Counter")

    #@timeit
    async def count_words_in_local_file(self, file_path: str):
        os_file_path = os.path.normcase(file_path)
        # First do some sanity on the input data
        if not path.isfile(os_file_path):
            raise ValueError(f"Could not find the file: {os_file_path}")

        with open(file_path, encoding='UTF-8') as f:
            for piece in read_in_chunks(file_object=f,
                                        chunk_size=1024 * 1024):
                await self.count_words_in_string(piece)

    #@timeit
    async def count_words_from_url(self, url: str):
        # First do some sanity on the input data
        if not validators.url(url):
            raise ValueError(f"The URL: {url} is not valid")

        local_filename = download_text_file(url=url,
                                            chunk_size=4096,
                                            base_path=tempfile.gettempdir())
        await self.count_words_in_local_file(local_filename)

    def get_option(self, input_type) -> Callable:
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
