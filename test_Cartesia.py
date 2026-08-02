import re
def normalize_string(text: str) -> str:
    # TODO: убери из text символы . , ! $ % : @ ? { } = - _ ` ~ ( ) '
    # а затем схлопни 2+ пробела подряд в один пробел.
    # Подсказка: в Python вместо .replace(regex, ...) как в JS
    # используется re.sub(pattern, replacement, text)
    return re.sub(r"\s{2,}", " ", re.sub("[.,!$%:@?}{=\-_`~()']", "", text))
    pass
def test_normalize_removes_punctuation():
    assert normalize_string("Hello, world!") == "Hello world"
def test_normalize_collapses_multiple_spaces():
    assert normalize_string("Hello    world") == "Hello world"
def test_normalize_handles_both():
    assert normalize_string("Hi!!  there,  friend.") == "Hi there friend"