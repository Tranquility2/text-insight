import re
import os
import tempfile
import validators

from collections import Counter
from os import path

from src.utils import timeit, read_in_chunks, download_text_file


class WordCount:
    WORDS_COUNT = Counter()

    @timeit
    def count_words_in_blob(self, source_string: str):
        # First do some sanity on the input data
        if not isinstance(source_string, str):
            raise ValueError("Source string is not valid")

        words = re.findall(r'\w+', source_string.lower())
        self.WORDS_COUNT.update(words)

        # TODO: Print only on debug
        print(f"Added #{len(words)} elements to the Counter")

    @timeit
    def count_words_in_local_file(self, file_path: str):
        os_file_path = os.path.normcase(file_path)
        # First do some sanity on the input data
        if not path.isfile(os_file_path):
            raise ValueError(f"Could not find the file: {os_file_path}")

        with open(file_path, encoding='UTF-8') as f:
            for piece in read_in_chunks(file_object=f,
                                        chunk_size=1024 * 1024):
                self.count_words_in_blob(piece)

    @timeit
    def count_words_from_url(self, url: str):
        # First do some sanity on the input data
        if not validators.url(url):
            raise ValueError(f"The URL: {url} is not valid")

        local_filename = download_text_file(url=url,
                                            chunk_size=4096,
                                            base_path=tempfile.gettempdir())
        self.count_words_in_local_file(local_filename)
