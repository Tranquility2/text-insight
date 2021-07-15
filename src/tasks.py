"""
Word count tasks for Text Insight
"""
import re
import redis
import os
import requests

from celery import Celery
from os import path

from utils import read_in_chunks, get_file_size_friendly

app = Celery('tasks', broker='redis://localhost:6379/1')
redis = redis.Redis(host='localhost', port=6379, db=0)


@app.task
def count_words_in_string(source_string: str):
    # First do some sanity on the input data
    if not isinstance(source_string, str):
        raise ValueError("Source string is not valid")

    words = re.findall(r'\w+', source_string.lower())
    print(f"Found #{len(words)} elements", end="")
    pipe = redis.pipeline()
    for word in words:
        pipe.hincrby('known', word, 1)  # This is atomic
    pipe.execute()


@app.task
def count_words_in_local_file(file_path: str):
    os_file_path = os.path.normcase(file_path)
    # First do some sanity on the input data
    if not path.isfile(os_file_path):
        raise ValueError(f"Could not find the file: {os_file_path}")

    with open(file_path, encoding='UTF-8') as f:
        for piece in read_in_chunks(file_object=f,
                                    chunk_size=1024 * 1024):
            count_words_in_string.apply_async(kwargs={'source_string': piece})


@app.task
def download_text_file(url: str, chunk_size: int = 1024, base_path=None):
    """Basic file downloader using an iterator.
    Default chunk size: 1k."""
    # TODO: Document assumption that files name is available in the url
    local_filename = url.split('/')[-1]
    full_path = path.join(base_path, local_filename)
    print(f"Downloading to {full_path}")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        with open(full_path, "wb") as file:
            for chunk in response.iter_content(chunk_size):
                file.write(chunk)
            # TODO: cleanup this file (should be a temp)

    print(f"Downloaded {get_file_size_friendly(full_path)}")
    return full_path
