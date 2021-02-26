from io import StringIO
import json
import unittest
from naya.json import parse
from naya.lossless import find_start_and_parse, JsonDataSource


class TestJsonTokenization(unittest.TestCase):

    def test_basic_stream(self):
        data = [
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

        data_io = StringIO()
        json.dump(data, data_io)
        data_io.seek(0)

        for item, full in find_start_and_parse(data_io):
            print(json.dumps(item, indent=4))

        print(json.dumps(full, indent=4))
        self.assertTrue(True)

    def test_skip_to_start_of_array(self):
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

        for item, full in find_start_and_parse(data_io, skip_to_array):
            print(json.dumps(item, indent=4))

        print(json.dumps(full, indent=4))
        self.assertTrue(True)

    def test_functional_api_lossless(self):
        pass

    def test_class_api_lossless(self):
        return
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

        for item, full in find_start_and_parse(request.raw, find_start):
            print(item)
        print(full)

    def test_functional_api_lossy(self):
        pass

    def test_class_api_lossy(self):
        pass

    def test_large_sample(self):
        with open("tests/sample.json", "r", encoding="utf-8") as file:
            obj2 = json.load(file)
        with open("tests/sample.json", "r", encoding="utf-8") as file:
            obj = parse(file)

        self.assertDictEqual(obj, obj2)
