import json
from io import StringIO
from . json import *
from typing import IO, Callable, Iterator


PrepareFunction = Callable[[IO, StringIO], None]
TupleIter = Iterator[Tuple[dict, Optional[dict]]


class JsonDataSource:
    def __init__(self, fp: IO, chunk_size: int = 1024):
        self.fp = fp
        self.chunk_size = chunk_size

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
        data = self.read(self.chunk_size)

        while data:
            data = self.read(self.chunk_size)

        self.data_buffer.seek(0)

    def json(self) -> dict:
        if self.data_buffer.tell():
            self.finish()

        return json.load(self.data_buffer)
    
    def __iter__(self):
        self.prepare(self, StringIO())

        for item in stream_array(tokenize(self)):
            yield item

        self.finish()


def parse_lossless(fp: IO, fn_find_start: PrepareFunction = None) -> TupleIter:
    data = JsonDataSource(fp)

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








data = {
    'name': 'abcdefghijklmnopqrstuvwxyz1234567890',
    'type': 'foo',
    'dataset': [
        {
            'a': 1,
            'b': []
        },
        {
            'a': 2,
            'b': []
        },
        {
            'a': 3,
            'b': []
        }
    ]
}

data_io = StringIO()
json.dump(data, data_io)
data_io.seek(0)

def skip_to_array(fp, skip_buffer):
    while not skip_buffer.getvalue().endswith('"dataset":'):
        skip_buffer.write(fp.read(1))

for item, full in parse_lossless(data_io, skip_to_array):
    print(json.dumps(item, indent=4))

print(json.dumps(full, indent=4))

quit()


a = JsonDataSource(request.raw)
for item in a:
    print(item)
print(a.json())

class CustomData(JsonDataSource):
    def prepare(self, skip_buffer):
        while skip_buffer.getvalue() != '{"ignore_this": 1, "array":':
            skip_buffer.write(self.read(1))


def find_start(skip_buffer):
    while skip_buffer.getvalue() != '{"ignore_this": 1, "array":':
        skip_buffer.write(self.read(1))

for item, full in parse_lossless(request.raw, find_start):
    print(item)
print(full)
