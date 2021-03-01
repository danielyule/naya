import json
from io import StringIO
from . json import *
from typing import IO, Callable, Iterator, Tuple, Optional


PrepareFunction = Callable[[IO, StringIO], None]
TupleIter = Iterator[Tuple[dict, Optional[dict]]]


class JsonDataSource:
    def __init__(self, fp: IO, chunk_size: int = 1024, lossless=True):
        self.fp = fp
        self.chunk_size = chunk_size
        self.lossless = lossless

        # Buffer for reading 1 char at a time for Naya
        self.bit_buffer = []

        # Buffer to use to store entire set of JSON
        self.data_buffer = StringIO()

    def prepare(self, fp: IO, skip_buffer: StringIO) -> None:
        """
        Customize as needed for your unique dataset.
        Provided as a convenience for custom data sources to implement.
        """

    def read(self, num_bytes: int) -> str:
        """
        This method ensures that Naya is fed only a single char each read.
        """
        if self.bit_buffer:  # Return any data leftover from last read()
            return self.bit_buffer.pop(0)
        
        try:
            data = self.fp.read(self.chunk_size)
            self.data_buffer.write(data)

            if data:  # Store the rest for next read()
                first_char = data[0]
                self.bit_buffer.extend(data[1:])
                return first_char

        except StopIteration:
            return ''

    def finish(self) -> None:
        if not self.lossless:
            return

        data = self.read(self.chunk_size)

        while data:
            data = self.read(self.chunk_size)

        self.data_buffer.seek(0)

    def json(self) -> dict:
        if not self.lossless:
            return

        if self.data_buffer.tell():
            self.finish()

        return json.load(self.data_buffer)
    
    def __iter__(self):
        try:
            self.prepare(self, StringIO())
        except RuntimeError as e:
            raise Exception(
                'End of stream searching for array start'
            ) from e

        try:
            for item in stream_array(tokenize(self)):
                yield item
        except RuntimeError as e:
            raise Exception(
                'End of stream in middle of array item'
            ) from e

        try:
            self.finish()
        except RuntimeError as e:
            raise Exception(
                'End of stream while collecting rest data after array'
            ) from e


def find_start_and_parse(
    fp: IO,
    fn_find_start: PrepareFunction = None,
    lossless: bool = True
) -> TupleIter:
    data = JsonDataSource(fp, lossless=lossless)

    if fn_find_start:
        data.prepare = fn_find_start

    data_iter = iter(data)

    try:
        prev = next(data_iter)
    except StopIteration:
        yield None, None
    
    for item in data_iter:
        yield prev, None
        prev = item

    # Pair full JSON with last item for reference outside of for loop
    yield prev, data.json()
