import datetime
import time
import requests
import humanfriendly

from functools import wraps
from typing import Any, Callable
from os import path


def timeit(func: Callable[..., Any]) -> Callable[..., Any]:
    """Times a function, usually used as decorator"""

    @wraps(func)
    def timed_func(*args: Any, **kwargs: Any) -> Any:
        """Returns the timed function"""
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = datetime.timedelta(seconds=(time.time() - start_time))
        print(f"Time spent on {func.__name__}: {elapsed_time}")
        return result

    return timed_func


def read_in_chunks(file_object, chunk_size: int = 1024) -> str:
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        # Loop until we reach a word end
        while not data[-1] == ' ':
            new_data = file_object.read(1)
            if not new_data:
                break
            data += new_data

        yield data


def get_file_size_friendly(file_path: str):
    file_size = path.getsize(file_path)
    return humanfriendly.format_size(file_size, binary=True)


@timeit
def download_text_file(url: str, chunk_size: int = 1024, base_path=None):
    """Basic file downloader using an iterator.
    Default chunk size: 1k."""
    # TODO: Document assumption that files name is available in the url
    local_filename = url.split('/')[-1]
    full_path = path.join(base_path, local_filename)
    print(f"Downloading to {full_path}")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        with open(full_path, "wb") as text_file:
            for chunk in response.iter_content(chunk_size):
                text_file.write(chunk)
            # TODO: cleanup this file (should be a temp)

    print(f"Downloaded {get_file_size_friendly(full_path)}")
    return full_path
