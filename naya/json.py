from io import StringIO


class TOKEN_TYPE:
    OPERATOR = 0
    STRING = 1
    NUMBER = 2
    BOOLEAN = 3
    NULL = 4


class __TOKENIZER_STATE:
    WHITESPACE = 0
    INTEGER_0 = 1
    INTEGER_SIGN = 2
    INTEGER = 3
    INTEGER_EXP = 4
    INTEGER_EXP_0 = 5
    FLOATING_POINT_0 = 6
    FLOATING_POINT = 8
    STRING = 9
    STRING_ESCAPE = 10
    STRING_END = 11
    TRUE_1 = 12
    TRUE_2 = 13
    TRUE_3 = 14
    FALSE_1 = 15
    FALSE_2 = 16
    FALSE_3 = 17
    FALSE_4 = 18
    NULL_1 = 19
    NULL_2 = 20
    NULL_3 = 21
    UNICODE_1 = 22
    UNICODE_2 = 23
    UNICODE_3 = 24
    UNICODE_4 = 25


def tokenize(stream):
    def is_delimiter(char):
        return char.isspace() or char in "{}[]:,"

    token = []
    charcode = 0
    completed = False
    now_token = ""

    def process_char(char, charcode):
        nonlocal token, completed, now_token
        advance = True
        add_char = False
        next_state = state
        if state == __TOKENIZER_STATE.WHITESPACE:
            if char == "{":
                completed = True
                now_token = (TOKEN_TYPE.OPERATOR, "{")
            elif char == "}":
                completed = True
                now_token = (TOKEN_TYPE.OPERATOR, "}")
            elif char == "[":
                completed = True
                now_token = (TOKEN_TYPE.OPERATOR, "[")
            elif char == "]":
                completed = True
                now_token = (TOKEN_TYPE.OPERATOR, "]")
            elif char == ",":
                completed = True
                now_token = (TOKEN_TYPE.OPERATOR, ",")
            elif char == ":":
                completed = True
                now_token = (TOKEN_TYPE.OPERATOR, ":")
            elif char == "\"":
                next_state = __TOKENIZER_STATE.STRING
            elif char in "123456789":
                next_state = __TOKENIZER_STATE.INTEGER
                add_char = True
            elif char == "0":
                next_state = __TOKENIZER_STATE.INTEGER_0
                add_char = True
            elif char == "-":
                next_state = __TOKENIZER_STATE.INTEGER_SIGN
                add_char = True
            elif char == "f":
                next_state = __TOKENIZER_STATE.FALSE_1
            elif char == "t":
                next_state = __TOKENIZER_STATE.TRUE_1
            elif char == "n":
                next_state = __TOKENIZER_STATE.NULL_1
            elif not char.isspace():
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.INTEGER:
            if char in "0123456789":
                add_char = True
            elif char == ".":
                next_state = __TOKENIZER_STATE.FLOATING_POINT_0
                add_char = True
            elif char == "e" or char == 'E':
                next_state = __TOKENIZER_STATE.INTEGER_EXP_0
                add_char = True
            elif is_delimiter(char):
                next_state = __TOKENIZER_STATE.WHITESPACE
                completed = True
                now_token = (TOKEN_TYPE.NUMBER, int("".join(token)))
                advance = False
            else:
                raise ValueError("A number must contain only digits.  Got '{}'".format(char))
        elif state == __TOKENIZER_STATE.INTEGER_0:
            if char == ".":
                next_state = __TOKENIZER_STATE.FLOATING_POINT_0
                add_char = True
            elif char == "e" or char == 'E':
                next_state = __TOKENIZER_STATE.INTEGER_EXP_0
                add_char = True
            elif is_delimiter(char):
                next_state = __TOKENIZER_STATE.WHITESPACE
                completed = True
                now_token = (TOKEN_TYPE.NUMBER, 0)
                advance = False
            else:
                raise ValueError("A 0 must be followed by a '.' or a 'e'.  Got '{0}'".format(char))
        elif state == __TOKENIZER_STATE.INTEGER_SIGN:
            if char == "0":
                next_state = __TOKENIZER_STATE.INTEGER_0
                add_char = True
            elif char in "123456789":
                next_state = __TOKENIZER_STATE.INTEGER
                add_char = True
            else:
                raise ValueError("A - must be followed by a digit.  Got '{0}'".format(char))
        elif state == __TOKENIZER_STATE.INTEGER_EXP_0:
            if char == "+" or char == "-" or char in "0123456789":
                next_state = __TOKENIZER_STATE.INTEGER_EXP
                add_char = True
            else:
                raise ValueError("An e in a number must be followed by a '+', '-' or digit.  Got '{0}'".format(char))
        elif state == __TOKENIZER_STATE.INTEGER_EXP:
            if char in "0123456789":
                add_char = True
            elif is_delimiter(char):
                completed = True
                now_token = (TOKEN_TYPE.NUMBER, float("".join(token)))
                next_state = __TOKENIZER_STATE.WHITESPACE
                advance = False
            else:
                raise ValueError("A number exponent must consist only of digits.  Got '{}'".format(char))
        elif state == __TOKENIZER_STATE.FLOATING_POINT:
            if char in "0123456789":
                add_char = True
            elif char == "e" or char == "E":
                next_state = __TOKENIZER_STATE.INTEGER_EXP_0
                add_char = True
            elif is_delimiter(char):
                completed = True
                now_token = (TOKEN_TYPE.NUMBER, float("".join(token)))
                next_state = __TOKENIZER_STATE.WHITESPACE
                advance = False
            else:
                raise ValueError("A number must include only digits")
        elif state == __TOKENIZER_STATE.FLOATING_POINT_0:
            if char in "0123456789":
                next_state = __TOKENIZER_STATE.FLOATING_POINT
                add_char = True
            else:
                raise ValueError("A number with a decimal point must be followed by a fractional part")
        elif state == __TOKENIZER_STATE.FALSE_1:
            if char == "a":
                next_state = __TOKENIZER_STATE.FALSE_2
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.FALSE_2:
            if char == "l":
                next_state = __TOKENIZER_STATE.FALSE_3
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.FALSE_3:
            if char == "s":
                next_state = __TOKENIZER_STATE.FALSE_4
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.FALSE_4:
            if char == "e":
                next_state = __TOKENIZER_STATE.WHITESPACE
                completed = True
                now_token = (TOKEN_TYPE.BOOLEAN, False)
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.TRUE_1:
            if char == "r":
                next_state = __TOKENIZER_STATE.TRUE_2
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.TRUE_2:
            if char == "u":
                next_state = __TOKENIZER_STATE.TRUE_3
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.TRUE_3:
            if char == "e":
                next_state = __TOKENIZER_STATE.WHITESPACE
                completed = True
                now_token = (TOKEN_TYPE.BOOLEAN, True)
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.NULL_1:
            if char == "u":
                next_state = __TOKENIZER_STATE.NULL_2
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.NULL_2:
            if char == "l":
                next_state = __TOKENIZER_STATE.NULL_3
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.NULL_3:
            if char == "l":
                next_state = __TOKENIZER_STATE.WHITESPACE
                completed = True
                now_token = (TOKEN_TYPE.NULL, None)
            else:
                raise ValueError("Invalid JSON character: '{0}'".format(char))
        elif state == __TOKENIZER_STATE.STRING:
            if char == "\"":
                completed = True
                now_token = (TOKEN_TYPE.STRING, "".join(token))
                next_state = __TOKENIZER_STATE.STRING_END
            elif char == "\\":
                next_state = __TOKENIZER_STATE.STRING_ESCAPE
            else:
                add_char = True
        elif state == __TOKENIZER_STATE.STRING_END:
            if is_delimiter(char):
                advance = False
                next_state = __TOKENIZER_STATE.WHITESPACE
            else:
                raise ValueError("Expected whitespace or an operator after strin.  Got '{}'".format(char))
        elif state == __TOKENIZER_STATE.STRING_ESCAPE:
            next_state = __TOKENIZER_STATE.STRING
            if char == "\\" or char == "\"":
                add_char = True
            elif char == "b":
                char = "\b"
                add_char = True
            elif char == "f":
                char = "\f"
                add_char = True
            elif char == "n":
                char = "\n"
                add_char = True
            elif char == "t":
                char = "\t"
                add_char = True
            elif char == "r":
                char = "\r"
                add_char = True
            elif char == "/":
                char = "/"
                add_char = True
            elif char == "u":
                next_state = __TOKENIZER_STATE.UNICODE_1
                charcode = 0
            else:
                raise ValueError("Invalid string escape: {}".format(char))
        elif state == __TOKENIZER_STATE.UNICODE_1:
            if char in "0123456789":
                charcode = (ord(char) - 48) * 4096
            elif char in "abcdef":
                charcode = (ord(char) - 87) * 4096
            elif char in "ABCDEF":
                charcode = (ord(char) - 55) * 4096
            else:
                raise ValueError("Invalid character code: {}".format(char))
            next_state = __TOKENIZER_STATE.UNICODE_2
            char = ""
        elif state == __TOKENIZER_STATE.UNICODE_2:
            if char in "0123456789":
                charcode += (ord(char) - 48) * 256
            elif char in "abcdef":
                charcode += (ord(char) - 87) * 256
            elif char in "ABCDEF":
                charcode += (ord(char) - 55) * 256
            else:
                raise ValueError("Invalid character code: {}".format(char))
            next_state = __TOKENIZER_STATE.UNICODE_3
            char = ""
        elif state == __TOKENIZER_STATE.UNICODE_3:
            if char in "0123456789":
                charcode += (ord(char) - 48) * 16
            elif char in "abcdef":
                charcode += (ord(char) - 87) * 16
            elif char in "ABCDEF":
                charcode += (ord(char) - 55) * 16
            else:
                raise ValueError("Invalid character code: {}".format(char))
            next_state = __TOKENIZER_STATE.UNICODE_4
            char = ""
        elif state == __TOKENIZER_STATE.UNICODE_4:
            if char in "0123456789":
                charcode += ord(char) - 48
            elif char in "abcdef":
                charcode += ord(char) - 87
            elif char in "ABCDEF":
                charcode += ord(char) - 55
            else:
                raise ValueError("Invalid character code: {}".format(char))
            next_state = __TOKENIZER_STATE.STRING
            char = chr(charcode)
            add_char = True

        if add_char:
            token.append(char)

        return advance, next_state, charcode
    state = __TOKENIZER_STATE.WHITESPACE
    char = stream.read(1)
    index = 0
    while char:
        try:
            advance, state, charcode = process_char(char, charcode)
        except ValueError as e:
            raise ValueError("".join([e.args[0], " at index {}".format(index)]))
        if completed:
            completed = False
            token = []
            yield now_token
        if advance:
            char = stream.read(1)
            index += 1
    process_char(" ", charcode)
    if completed:
        yield now_token


def parse_string(string):
    return parse(StringIO(string))

def parse(file):
    token_stream = tokenize(file)
    val = __parse(token_stream, next(token_stream))
    try:
        next(token_stream)
    except StopIteration:
        return val

    raise ValueError("Improperly closed JSON object")


def __parse(token_stream, first_token):
    class KVP:
        def __init__(self, key):
            self.key = key
            self.value = None
            self.set = False

        def __str__(self):
            if self.set:
                return "{}: {}".format(self.key, self.value)
            else:
                return "{}: <NULL>".format(self.key)

    stack = []
    token_type, token = first_token
    if token_type == TOKEN_TYPE.OPERATOR:
        if token == "{":
            stack.append({})
        elif token == "[":
            stack.append([])
        else:
            raise ValueError("Expected object or array.  Got '{}'".format(token))
    else:
        raise ValueError("Expected object or array.  Got '{}'".format(token))

    last_type, last_token = token_type, token
    try:
        token_type, token = next(token_stream)
    except StopIteration as e:
        raise ValueError("Too many opening braces") from e
    try:
        while True:
            # print(",".join([str(obj) for obj in stack]))
            if isinstance(stack[-1], list):
                if last_type == TOKEN_TYPE.OPERATOR:
                    if last_token == "[":
                        if token_type == TOKEN_TYPE.OPERATOR:
                            if token == "{":
                                stack.append({})
                            elif token == "[":
                                stack.append([])
                            elif token != "]":
                                raise ValueError("Array must either be empty or contain a value.  Got '{}'".
                                                 format(token))
                        else:
                            stack.append(token)
                    elif last_token == ",":
                        if token_type == TOKEN_TYPE.OPERATOR:
                            if token == "{":
                                stack.append({})
                            elif token == "[":
                                stack.append([])
                            else:
                                raise ValueError("Array value expected.  Got '{}'".format(token))
                        else:
                            stack.append(token)
                    elif last_token == "]":
                        value = stack.pop()
                        if len(stack) == 0:
                            return value
                        if isinstance(stack[-1], list):
                            stack[-1].append(value)
                        elif isinstance(stack[-1], dict):
                            stack[-1][value.key] = value.value
                        elif isinstance(stack[-1], KVP):
                            stack[-1].value = value
                            stack[-1].set = True
                            value = stack.pop()
                            if len(stack) == 0:
                                return value
                            if isinstance(stack[-1], list):
                                stack[-1].append(value)
                            elif isinstance(stack[-1], dict):
                                stack[-1][value.key] = value.value
                            else:
                                raise ValueError("Array items must be followed by a comma or closing bracket.  "
                                                 "Got '{}'".format(value))
                        else:
                            raise ValueError("Array items must be followed by a comma or closing bracket.  "
                                             "Got '{}'".format(value))
                    elif last_token == "}":
                        raise ValueError("Array closed with a '}'")
                    else:
                        raise ValueError("Array should not contain ':'")
                else:
                    raise ValueError("Unknown Error")
            elif isinstance(stack[-1], dict):
                if last_type == TOKEN_TYPE.OPERATOR:
                    if last_token == "{":
                        if token_type == TOKEN_TYPE.OPERATOR:
                            if token == "{":
                                stack.append({})
                            elif token == "[":
                                stack.append([])
                            elif token != "}":
                                raise ValueError("Object must either be empty or contain key value pairs."
                                                 "  Got '{}'".format(token))
                        elif token_type == TOKEN_TYPE.STRING:
                            stack.append(KVP(token))
                        else:
                            raise ValueError("Object keys must be strings.  Got '{}'".format(token))
                    elif last_token == ",":
                        if token_type == TOKEN_TYPE.OPERATOR:
                            if token == "{":
                                stack.append({})
                            elif token == "[":
                                stack.append([])
                            else:
                                raise ValueError("Object key expected.  Got '{}'".format(token))
                        elif token_type == TOKEN_TYPE.STRING:
                            stack.append(KVP(token))
                        else:
                            raise ValueError("Object keys must be strings.  Got '{}'".format(token))
                    elif last_token == "}":
                        value = stack.pop()
                        if len(stack) == 0:
                            return value
                        if isinstance(stack[-1], list):
                            stack[-1].append(value)
                        elif isinstance(stack[-1], dict):
                            stack[-1][value.key] = value.value
                        elif isinstance(stack[-1], KVP):
                            stack[-1].value = value
                            stack[-1].set = True
                            value = stack.pop()
                            if len(stack) == 0:
                                return value
                            if isinstance(stack[-1], list):
                                stack[-1].append(value)
                            elif isinstance(stack[-1], dict):
                                stack[-1][value.key] = value.value
                            else:
                                raise ValueError("Object key value pairs must be followed by a comma or "
                                                 "closing bracket.  Got '{}'".format(value))
                    elif last_token == "]":
                        raise ValueError("Object closed with a ']'")
                    else:
                        raise ValueError("Object key value pairs should be separated by comma, not ':'")
            elif isinstance(stack[-1], KVP):
                if stack[-1].set:
                    if token_type == TOKEN_TYPE.OPERATOR:
                        if token != "}" and token != ",":
                            raise ValueError("Object key value pairs should be followed by ',' or '}'.  Got '"
                                             + token + "'")
                        value = stack.pop()
                        if len(stack) == 0:
                            return value
                        if isinstance(stack[-1], list):
                            stack[-1].append(value)
                        elif isinstance(stack[-1], dict):
                            stack[-1][value.key] = value.value
                        else:
                            raise ValueError("Object key value pairs must be followed by a comma or closing bracket.  "
                                             "Got '{}'".format(value))
                        if token == "}" and len(stack) == 1:
                            return stack[0]
                    else:
                        raise ValueError("Object key value pairs should be followed by ',' or '}'.  Got '"
                                         + token + "'")
                else:
                    if token_type == TOKEN_TYPE.OPERATOR and token == ":" and last_type == TOKEN_TYPE.STRING:
                        pass
                    elif last_type == TOKEN_TYPE.OPERATOR and last_token == ":":
                        if token_type == TOKEN_TYPE.OPERATOR:
                            if token == "{":
                                stack.append({})
                            elif token == "[":
                                stack.append([])
                            else:
                                raise ValueError("Object property value expected.  Got '{}'".format(token))
                        else:
                            stack[-1].value = token
                            stack[-1].set = True
                    else:
                        raise ValueError("Object keys must be separated from values by a single ':'.  "
                                         "Got '{}'".format(token))
            else:
                value = stack.pop()
                if isinstance(stack[-1], list):
                    stack[-1].append(value)
                elif isinstance(stack[-1], dict):
                    stack[-1][value.key] = value.value
                else:
                    raise ValueError("Array items must be followed by a comma or closing bracket.  "
                                     "Got '{}'".format(value))

            last_type, last_token = token_type, token
            token_type, token = next(token_stream)
    except StopIteration as e:
        if len(stack) == 1:
            return stack[0]
        else:
            raise ValueError("JSON Object not properly closed") from e


def stream_array(token_stream):
    token_type, token = next(token_stream)

    if token_type != TOKEN_TYPE.OPERATOR or token != '[':
        raise ValueError("Array must start with '['.  Got '{}'".format(token))

    while True:
        token_type, token = next(token_stream)
        if token_type == TOKEN_TYPE.OPERATOR:
            if token == ']':
                return
            elif token == ",":
                token_type, token = next(token_stream)
                if token_type == TOKEN_TYPE.OPERATOR:
                    if token == "[" or token == "{":
                        yield __parse(token_stream, (token_type, token))
                    else:
                        raise ValueError("Expected an array value.  Got '{}'".format(token))
                else:
                    yield token
            else:
                raise ValueError("Array entries must be followed by ',' or ']'.  Got '{}'".format(token))
        else:
            yield token
