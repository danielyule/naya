from io import StringIO
import json
import unittest
from naya.json import parse
from naya.lossless import find_start_and_parse, JsonDataSource


class TestJsonTokenization(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.data1 = [
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

        self.data2 = {
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

    def test_basic_stream(self):
        data_io = StringIO()
        json.dump(self.data1, data_io)
        data_io.seek(0)

        for i, (item, full) in enumerate(find_start_and_parse(data_io)):
            self.assertDictEqual(item, self.data1[i])

        self.assertListEqual(full, self.data1)

    def test_skip_to_start_of_array(self):
        data_io = StringIO()
        json.dump(self.data2, data_io)
        data_io.seek(0)

        def skip_to_array(fp, skip_buffer):
            while not skip_buffer.getvalue().endswith('"dataset":'):
                skip_buffer.write(fp.read(1))

        test_data = enumerate(find_start_and_parse(data_io, skip_to_array))

        for i, (item, full) in test_data:
            self.assertDictEqual(item, self.data2['dataset'][i])

        self.assertDictEqual(full, self.data2)

    def test_functional_api_lossless(self):
        data_io = StringIO()
        json.dump(self.data2, data_io)
        data_io.seek(0)

        def skip_to_array(fp, skip_buffer):
            while not skip_buffer.getvalue().endswith('"dataset":'):
                skip_buffer.write(fp.read(1))

        test_data = enumerate(
            find_start_and_parse(
                data_io,
                skip_to_array,
                lossless=True
            )
        )

        for i, (item, full) in test_data:
            self.assertDictEqual(item, self.data2['dataset'][i])

        self.assertDictEqual(full, self.data2)

    def test_class_api_lossless(self):
        data_io = StringIO()
        json.dump(self.data2, data_io)
        data_io.seek(0)

        class CustomData(JsonDataSource):
            def prepare(self, fp, skip_buffer):
                while not skip_buffer.getvalue().endswith('"dataset":'):
                    skip_buffer.write(fp.read(1))
        
        source = CustomData(data_io)
        for i, item in enumerate(source):
            self.assertDictEqual(item, self.data2['dataset'][i])

        self.assertDictEqual(source.json(), self.data2)

    def test_functional_api_lossy(self):
        data_io = StringIO()
        json.dump(self.data2, data_io)
        data_io.seek(0)

        def skip_to_array(fp, skip_buffer):
            while not skip_buffer.getvalue().endswith('"dataset":'):
                skip_buffer.write(fp.read(1))

        test_data = enumerate(
            find_start_and_parse(
                data_io,
                skip_to_array,
                lossless=False
            )
        )

        for i, (item, full) in test_data:
            self.assertDictEqual(item, self.data2['dataset'][i])

        self.assertIsNone(full)

    def test_class_api_lossy(self):
        data_io = StringIO()
        json.dump(self.data2, data_io)
        data_io.seek(0)

        class CustomData(JsonDataSource):
            def prepare(self, fp, skip_buffer):
                while not skip_buffer.getvalue().endswith('"dataset":'):
                    skip_buffer.write(fp.read(1))
        
        source = CustomData(data_io, lossless=False)
        for i, item in enumerate(source):
            self.assertDictEqual(item, self.data2['dataset'][i])

        self.assertIsNone(source.json())

    def test_large_sample_lossless(self):
        class CustomData(JsonDataSource):
            def prepare(self, fp, skip_buffer):
                while not skip_buffer.getvalue().endswith('"c":'):
                    char = fp.read(1)
                    if not char:
                        break
                    skip_buffer.write(char)

        data_io = open("tests/sample_lossless.json", "r", encoding="utf-8")

        # Don't discard any data
        source = CustomData(data_io, lossless=True)

        prev = None
        for item in source:
            if not prev:
                prev = item
                continue
            self.assertDictEqual(item, prev)
            prev = item

        data_io.close()
        self.assertIsNotNone(source.json())

    def test_large_sample_lossy(self):
        class CustomData(JsonDataSource):
            def prepare(self, fp, skip_buffer):
                while not skip_buffer.getvalue().endswith('"c":'):
                    char = fp.read(1)
                    if not char:
                        break
                    skip_buffer.write(char)

        data_io = open("tests/sample_lossless.json", "r", encoding="utf-8")
        source = CustomData(data_io, lossless=False)
        prev = None
        for item in source:
            if not prev:
                prev = item
                continue
            self.assertDictEqual(item, prev)
            prev = item

        self.assertIsNone(source.json())
        data_io.close()
