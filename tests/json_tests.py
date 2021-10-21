from io import StringIO
import json
import unittest
from naya.json import tokenize, TOKEN_TYPE, parse_string, parse, stream_array


class TestJsonTokenization(unittest.TestCase):

    def tokenize_sequence(self, string):
        return [token for token in tokenize(StringIO(string))]

    def tokenize_single_token(self, string):
        token_list = self.tokenize_sequence(string)
        self.assertEqual(1, len(token_list))
        _, token = token_list[0]
        return token

    def assertNumberEquals(self, expected, actual):
        token_list = self.tokenize_sequence(actual)
        self.assertEqual(1, len(token_list))
        ttype, token = token_list[0]
        self.assertEqual(expected, token)
        self.assertEqual(ttype, TOKEN_TYPE.NUMBER)

    def assertOperatorEquals(self, expected, actual):

        token_list = self.tokenize_sequence(actual)
        ttype, token = token_list[0]
        self.assertEqual(expected, token)
        self.assertEqual(ttype, TOKEN_TYPE.OPERATOR)

    def assertStringEquals(self, expected, actual):
        token_list = [token for token in tokenize(StringIO('"{}"'.format(actual)))]
        self.assertEqual(1, len(token_list))
        ttype, token = token_list[0]
        self.assertEqual(expected, token)
        self.assertEqual(ttype, TOKEN_TYPE.STRING)

    def test_number_parsing(self):
        self.assertNumberEquals(0, "0")
        self.assertNumberEquals(0.5, "0.5")
        self.assertNumberEquals(0, "-0")
        self.assertNumberEquals(12, "12")
        self.assertNumberEquals(3.5, "3.5")
        self.assertNumberEquals(1.2e11, "12e10")
        self.assertNumberEquals(7.8e-14, "78E-15")
        self.assertNumberEquals(0, "0e10")
        self.assertNumberEquals(65.7, "65.7")
        self.assertNumberEquals(892.978, "892.978")
        self.assertNumberEquals(8.9e7, "8.9E7")
        self.assertRaises(ValueError, self.tokenize_single_token, "01")
        self.assertRaises(ValueError, self.tokenize_single_token, "1.")
        self.assertRaises(ValueError, self.tokenize_single_token, "-01")
        self.assertRaises(ValueError, self.tokenize_single_token, "2a")
        self.assertRaises(ValueError, self.tokenize_single_token, "-a")
        self.assertRaises(ValueError, self.tokenize_single_token, "3.b")
        self.assertRaises(ValueError, self.tokenize_single_token, "3.e10")
        self.assertRaises(ValueError, self.tokenize_single_token, "3.6ea")
        self.assertRaises(ValueError, self.tokenize_single_token, "67.8e+a")

    def test_operator_parsing(self):
        self.assertOperatorEquals("{", "{")
        self.assertOperatorEquals("}", "}")
        self.assertOperatorEquals("[", "[")
        self.assertOperatorEquals("]", "]")
        self.assertOperatorEquals(":", ":")
        self.assertOperatorEquals(",", ",")

    def test_string_parsing(self):
        self.assertStringEquals("word", "word")
        self.assertStringEquals("with\tescape", "with\\tescape")
        self.assertStringEquals("with\n a different escape", "with\\n a different escape")
        self.assertStringEquals("using a \bbackspace", "using a \\bbackspace")
        self.assertStringEquals("now we have \f a formfeed", "now we have \\f a formfeed")
        self.assertStringEquals("\"a quote\"", "\\\"a quote\\\"")
        self.assertStringEquals("", "")
        self.assertStringEquals("/", "\\/")
        self.assertStringEquals("this char: \u0202", "this char: \\u0202")
        self.assertStringEquals("\uaf78", "\\uaf78")
        self.assertStringEquals("\u8A0b", "\\u8A0b")
        self.assertStringEquals("\ub3e7", "\\uB3e7")
        self.assertStringEquals("\u12ef", "\\u12eF")
        self.assertRaises(ValueError, self.tokenize_single_token, "\"\\uay76\"")
        self.assertRaises(ValueError, self.tokenize_single_token, "\"\\h\"")
        self.assertRaises(ValueError, self.tokenize_single_token, "\"\\2\"")
        self.assertRaises(ValueError, self.tokenize_single_token, "\"\\!\"")
        self.assertRaises(ValueError, self.tokenize_single_token, "\"\\u!\"")

    def test_sequence(self):
        result = [token for token in tokenize(StringIO("123 \"abc\":{}"))]
        self.assertEqual(result, [(2, 123), (1, 'abc'), (0, ':'), (0, '{'), (0, '}')])

        # Borrowed from http://en.wikipedia.org/wiki/JSON
        big_file = """{
          "firstName": "John",
          "lastName": "Smith",
          "isAlive": true,
          "age": 25,
          "height_cm": 167.6,
          "address": {
            "streetAddress": "21 2nd Street",
            "city": "New York",
            "state": "NY",
            "postalCode": "10021-3100"
          },
          "phoneNumbers": [
            {
              "type": "home",
              "number": "212 555-1234"
            },
            {
              "type": "office",
              "number": "646 555-4567"
            }
          ],
          "children": [],
          "spouse": null
        }"""
        result = [token for token in tokenize(StringIO(big_file))]
        expected = [(0, '{'), (1, 'firstName'), (0, ':'), (1, 'John'), (0, ','), (1, 'lastName'), (0, ':'),
                    (1, 'Smith'), (0, ','), (1, 'isAlive'), (0, ':'), (3, True), (0, ','), (1, 'age'), (0, ':'),
                    (2, 25), (0, ','), (1, 'height_cm'), (0, ':'), (2, 167.6), (0, ','), (1, 'address'), (0, ':'),
                    (0, '{'), (1, 'streetAddress'), (0, ':'), (1, '21 2nd Street'), (0, ','), (1, 'city'), (0, ':'),
                    (1, 'New York'), (0, ','), (1, 'state'), (0, ':'), (1, 'NY'), (0, ','), (1, 'postalCode'),
                    (0, ':'), (1, '10021-3100'), (0, '}'), (0, ','), (1, 'phoneNumbers'), (0, ':'), (0, '['), (0, '{'),
                    (1, 'type'), (0, ':'), (1, 'home'), (0, ','), (1, 'number'), (0, ':'), (1, '212 555-1234'),
                    (0, '}'), (0, ','), (0, '{'), (1, 'type'), (0, ':'), (1, 'office'), (0, ','), (1, 'number'),
                    (0, ':'), (1, '646 555-4567'), (0, '}'), (0, ']'), (0, ','), (1, 'children'), (0, ':'), (0, '['),
                    (0, ']'), (0, ','), (1, 'spouse'), (0, ':'), (4, None), (0, '}')]
        self.assertListEqual(result, expected)
        big_file_no_space = '{"firstName":"John","lastName":"Smith","isAlive":true,"age":25,"height_cm":167.6,"addres' \
                            's":{"streetAddress":"21 2nd Street","city":"New York","state":"NY","postalCode":"10021-3' \
                            '100"},"phoneNumbers":[{"type":"home","number":"212 555-1234"},{"type":"office","number":' \
                            '"646 555-4567"}],"children":[],"spouse":null}'
        result = [token for token in tokenize(StringIO(big_file_no_space))]
        self.assertListEqual(result, expected)
        result = [token for token in tokenize(StringIO("854.6,123"))]
        self.assertEqual(result, [(2, 854.6), (0, ','), (2, 123)])
        self.assertRaises(ValueError, self.tokenize_sequence, "123\"text\"")
        self.assertRaises(ValueError, self.tokenize_sequence, "23.9e10true")
        self.assertRaises(ValueError, self.tokenize_sequence, "\"test\"56")

    def test_arrays(self):
        arr = parse_string('[]')
        self.assertListEqual(arr, [])
        arr = parse_string('["People", "Places", "Things"]')
        self.assertListEqual(arr, ["People", "Places", "Things"])
        arr = parse_string('["Apples", "Bananas", ["Pears", "Limes"]]')
        self.assertListEqual(arr, ["Apples", "Bananas", ["Pears", "Limes"]])
        self.assertRaises(ValueError, parse_string, '["People", "Places", "Things"')
        self.assertRaises(ValueError, parse_string, '["People", "Places" "Things"]')
        self.assertRaises(ValueError, parse_string, '["People", "Places"] "Things"]')

    def test_objects(self):
        obj = parse_string('{"key1":"value1"}')
        self.assertDictEqual(obj, {"key1": "value1"})

        obj = parse_string("{}")
        self.assertDictEqual(obj, {})

        obj = parse_string('{"name": {"first":"Daniel", "last": "Yule"}}')
        self.assertDictEqual(obj, {"name": {"first": "Daniel", "last": "Yule"}})

        # Borrowed from http://en.wikipedia.org/wiki/JSON
        big_file = """{
          "firstName": "John",
          "lastName": "Smith",
          "isAlive": true,
          "age": 25,
          "height_cm": 167.6,
          "address": {
            "streetAddress": "21 2nd Street",
            "city": "New York",
            "state": "NY",
            "postalCode": "10021-3100"
          },
          "phoneNumbers": [
            {
              "type": "home",
              "number": "212 555-1234"
            },
            {
              "type": "office",
              "number": "646 555-4567"
            }
          ],
          "children": [],
          "spouse": null
        }"""
        obj = parse_string(big_file)
        self.assertDictEqual(obj, {
            "firstName": "John",
            "lastName": "Smith",
            "isAlive": True,
            "age": 25,
            "height_cm": 167.6,
            "address": {
                "streetAddress": "21 2nd Street",
                "city": "New York",
                "state": "NY",
                "postalCode": "10021-3100"
            },
            "phoneNumbers": [
                {
                    "type": "home",
                    "number": "212 555-1234"
                },
                {
                    "type": "office",
                    "number": "646 555-4567"
                }
            ],
            "children": [],
            "spouse": None
        })

        self.assertRaises(ValueError, parse_string, "{")
        self.assertRaises(ValueError, parse_string, '{"key": "value"')
        self.assertRaises(ValueError, parse_string, '{"key": "value"}}')
        self.assertRaises(ValueError, parse_string, '{"key": "value", "value2"}')
        self.assertRaises(ValueError, parse_string, '{"key", "value": "value2"}')
        self.assertRaises(ValueError, parse_string, '{"key", "value": "value2"]}')
        self.assertRaises(ValueError, parse_string, '{"key", "value": "value2" []}')
        self.assertRaises(ValueError, parse_string, '{"key", "value": ["value2"]}')

    def test_array_stream(self):
        arr = stream_array(tokenize(StringIO('[]')))
        self.assertListEqual([i for i in arr], [])
        arr = stream_array(tokenize(StringIO('["People", "Places", "Things"]')))
        self.assertListEqual([i for i in arr], ["People", "Places", "Things"])
        arr = stream_array(tokenize(StringIO('["Apples", "Bananas", ["Pears", "Limes"]]')))
        self.assertListEqual([i for i in arr], ["Apples", "Bananas", ["Pears", "Limes"]])
        arr = stream_array(tokenize(StringIO('["Apples", ["Pears", "Limes"], "Bananas"]')))
        self.assertListEqual([i for i in arr], ["Apples", ["Pears", "Limes"], "Bananas"])
        arr = stream_array(tokenize(StringIO('["Apples", {"key":"value"}, "Bananas"]')))
        self.assertListEqual([i for i in arr], ["Apples", {"key": "value"}, "Bananas"])

    def test_array_stream_of_objects_and_arrays(self):
        arr = stream_array(tokenize(StringIO('[{"key1": "value1"}, "Places", "Things"]')))
        self.assertListEqual([i for i in arr], [{"key1": "value1"}, "Places", "Things"])
        arr = stream_array(tokenize(StringIO('[{"key1": "value1"}, "Places", [0, 1, 2]]')))
        self.assertListEqual([i for i in arr], [{"key1": "value1"}, "Places", [0, 1, 2]])
        arr = stream_array(tokenize(StringIO('[[{"key1": "value1"}, "Places", [0, 1, 2]]]')))
        self.assertListEqual([i for i in arr], [[{"key1": "value1"}, "Places", [0, 1, 2]]])
        arr = stream_array(tokenize(StringIO('[[{"key1": "value1", "key2": 5}]]')))
        self.assertListEqual([i for i in arr], [[{"key1": "value1", "key2": 5}]])
        arr = stream_array(tokenize(StringIO('[[{"key1": "value1", "key2": 5}, {"key3": "value3", "key4": null}], {"key5": false, "key6": "5"}]')))
        self.assertListEqual([i for i in arr], [[{"key1": "value1", "key2": 5}, {"key3": "value3", "key4":None}], {"key5": False, "key6": "5"}])

    def test_large_sample(self):
        with open("tests/sample.json", "r", encoding="utf-8") as file:
            obj2 = json.load(file)
        with open("tests/sample.json", "r", encoding="utf-8") as file:
            obj = parse(file)

        self.assertDictEqual(obj, obj2)

    def test_stream_array_empty_data(self):
        arr = stream_array(tokenize(StringIO('')))
        with self.assertRaises(StopIteration):
            next(arr)
