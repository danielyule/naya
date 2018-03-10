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

## Related Projects

### Yajl-Py

[Yajl-Py](http://pykler.github.io/yajl-py/) is a wrapper around the Yajl JSON library that can be used to generate SAX style events while parsing JSON.  It also has a pure python implementation.

### UltraJSON

[UltraJSON](https://github.com/esnme/ultrajson) is a super fast JSON Parser written in C with python bindings.

