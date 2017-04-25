import json
from collections import OrderedDict


def _json_loads(s):
    return json.loads(s, object_pairs_hook=OrderedDict)


def _json_dumps(obj, indent=None):
    return json.dumps(obj, indent=indent)


def assert_json(actual, expected, indent=None):

    if isinstance(actual, str):
        actual = _json_loads(actual)

    if isinstance(expected, str):
        expected = _json_loads(expected)

    assert _json_dumps(actual, indent=indent) \
        == _json_dumps(expected, indent=indent)
