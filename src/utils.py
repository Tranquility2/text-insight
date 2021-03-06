"""
Utils for Text Insight web service
"""
import datetime
import logging
import time
import humanfriendly

from functools import wraps
from typing import Any, Callable
from os import path


def config_logs(name: str, level=logging.DEBUG):
    """ Config logger """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    formatter.datefmt = '%H:%M:%S'
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


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


def get_file_size_friendly(file_path: str) -> str:
    file_size = path.getsize(file_path)
    return humanfriendly.format_size(file_size, binary=True)
