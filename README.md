NAYA (Not Another Yet Another)
==============================
A fast streaming JSON parser for Python
---------------------------------------

NAYA is designed to parse JSON quickly and efficiently in pure Python 3 with no dependencies.

NAYA is different from other JSON parsers in that it can be used to stream a JSON array, even if the entire array
is not yet available.

## Usage

### stream_array

Given the following JSON which will be coming through a file like object:

```json
[
{
    "id": 1,
    "type": "message",
    "content": "Hello!"
},
{
    "id": 2,
    "type": "query",
    "user_name": "tarzan",
    "password": "not_jane"
},
{
    "id": 3,
    "type": "command",
    "action": "swing"
}
]
```

Even if each message will be sent one at a time on the file like object (called `fp`)

```python
messages = stream_array(tokenize(fp))
for message in messages:
    handle_message(message)
```

That is, `stream_array` returns an iterator, which will block until the next array item is available.

`handle_message` will be called three times with the following parameters:

```python
handle_message({
    "id": 1,
    "type": "message",
    "content": "Hello!"
})
handle_message({
    "id": 2,
    "type": "query",
    "user_name": "tarzan",
    "password": "not_jane"
})
handle_message({
    "id": 3,
    "type": "command",
    "action": "swing"
})
```

### parse

In addition to streaming array, NAYA also supports standard parsing, like the built in library:

```python
obj = parse(fp)
```

This method will block until the entire object is read.  There is also the convenience method

```python
obj = parse_string('{"key": "value"}')
```

## Dealing With Data That Does Not Start With An Array Without Losing Data

Most JSON data obtained from APIs is not returned as a flat array of objects. To
account for this, one can skip ahead to the start of the array and pass the file
pointer to Naya. However, this by default loses data. Additionally, any data
after the array will not be read by Naya. The following JSON illustrates what
this entails:

```jsonc
// This data cannot be read by Naya because it doesn't start with an array
{
    "key1": "value1",
    "key2": "value2",
    "dataset":
    [  // However, if the first 2 keys are discarded, it will ingest properly
        {
            "id": 1,
            "type": "message",
            "content": "Hello!"
        },
        {
            "id": 2,
            "type": "query",
            "user_name": "tarzan",
            "password": "not_jane"
        },
        {
            "id": 3,
            "type": "command",
            "action": "swing"
        }
    ],  // Naya ends it's processing at the end of the array
    "timestamp": 0  // This key is discarded
}
```

Unless a buffer of data is kept in memory to record the keys before and the keys
after the data array, they will be lost. To stream JSON data without losing keys
before or after the data array, use either the `JsonDataSource` class or the
`find_start_and_parse()` function.

They are equivalent in functionality but one is for a functional API and one is
for writing JSON streamers that are customized to a given known dataset.

To use them:

```python
from naya import JsonDataSource, find_start_and_parse

# Data from above example:
file = open('the_data.json')

# Functional API
def find_start_of_data(fp, skip_buffer):
    # fp is the file and skip_buffer is a StringIO for convenience
    while not skip_buffer.getvalue().endswith('"dataset":'):
        # Append the char to the temporary buffer
        skip_buffer.write(fp.read(1))

        # fp.read(1) calls JsonDataSource.read() which records all bytes

for item, all_json in find_start_and_parse(file, find_start_of_data):
    print(json.dumps(item, indent=4))

# If all items are successfully parsed, all_json == all json ;)
print(json.dumps(all_json, indent=4))
```

The above example will print these values when run:

```python
{
    "id": 1,
    "type": "message",
    "content": "Hello!"
}
{
    "id": 2,
    "type": "query",
    "user_name": "tarzan",
    "password": "not_jane"
}
{
    "id": 3,
    "type": "command",
    "action": "swing"
}
{
    "key1": "value1",
    "key2": "value2",
    "dataset": [
        {
            "id": 1,
            "type": "message",
            "content": "Hello!"
        },
        {
            "id": 2,
            "type": "query",
            "user_name": "tarzan",
            "password": "not_jane"
        },
        {
            "id": 3,
            "type": "command",
            "action": "swing"
        }
    ],
    "timestamp": 0
}
```

The class based API works exactly the same but bundles the find data function
along with its processing capability:

```python
# Data from above example:
file = open('the_data.json')

class CustomDataSource(JsonDataSource):
    def prepare(self, fp, skip_buffer):
        while not skip_buffer.getvalue().endswith('"dataset":'):
            # Append the char to the temporary buffer
            skip_buffer.write(fp.read(1))

data_source = CustomDataSource(file)

for item in data_source:
    print(json.dumps(item, indent=4))

print(json.dumps(data_source.json(), indent=4))
```

When run the above code example prints the same as the functional API.

To take advantage of using preprocessor functions without keeping the entire
data set in memory, simply pass `lossless=False` to `CustomDataSource`
constructor or `find_start_and_parse()` when working with large datasets. This
will of course make the entire JSON dataset unavailable but iterating through
the data array will work as expected.

## Related Projects

### Yajl-Py

[Yajl-Py](http://pykler.github.io/yajl-py/) is a wrapper around the Yajl JSON library that can be used to generate SAX style events while parsing JSON.  It also has a pure python implementation.

### UltraJSON

[UltraJSON](https://github.com/esnme/ultrajson) is a super fast JSON Parser written in C with python bindings.

