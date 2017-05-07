import copy
import json
import re
from collections import OrderedDict

from django.core.cache import cache
from django.db.models import Model
from django.forms.models import model_to_dict as model_to_dict_default
from django.utils.translation import ugettext_lazy as _

from configfactory.exceptions import (
    CircularInjectError,
    InjectKeyError,
    JSONEncodeError,
)
from configfactory.settings import GLOBAL_SETTINGS_DEFAULTS

key_re = r'[a-zA-Z][(\-|\.)a-zA-Z0-9_]*'
inject_regex = re.compile(r'(?<!\$)(\$(?:{param:(%(n)s)}))'
                          % ({'n': key_re}))
pytype_regex = re.compile(r'\"pytype:.+\"')


def merge_dict(d1, d2):
    """Merge two dictionaries."""

    if not isinstance(d2, dict):
        return d2

    ret = copy.deepcopy(d1)

    for k, v in d2.items():
        if k in ret \
                and isinstance(ret[k], dict):
            ret[k] = merge_dict(ret[k], v)
        else:
            ret[k] = copy.deepcopy(v)
    return ret


def flatten_dict(d, parent_key='', sep='.'):
    """Flatten dictionary keys."""

    if not isinstance(d, dict):
        return d

    items = []

    for k, v in d.items():
        new_key = sep.join([parent_key, k]) if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return OrderedDict(items)


def cleanse_dict(d, hidden=None, substitute=None):
    """Hide dictionary secured data."""

    ret = copy.deepcopy(d)

    for k, v in d.items():
        if isinstance(v, dict):
            ret[k] = cleanse_dict(v, hidden=hidden, substitute=substitute)
        else:
            ret[k] = cleanse_value(
                key=k,
                value=v,
                hidden=hidden,
                substitute=substitute
            )
    return ret


def cleanse_value(key, value, hidden=None, substitute=None):
    """Hide secured data."""

    if hidden is None:
        hidden = global_settings['cleansed_hidden']

    if isinstance(hidden, str):
        hidden = hidden.split()

    hidden_re = re.compile('|'.join(hidden), flags=re.IGNORECASE)

    if substitute is None:
        substitute = global_settings['cleansed_substitute']

    try:
        if hidden_re.search(key):
            cleansed = substitute
        else:
            if isinstance(value, dict):
                cleansed = OrderedDict([
                    (k, cleanse_value(k, v,
                                      hidden=hidden,
                                      substitute=substitute))
                    for k, v in value.items()
                ])
            else:
                cleansed = value
    except TypeError:
        cleansed = value

    return cleansed


class JSONDecoder(json.JSONDecoder):

    def decode(self, s, **kwargs):
        s = pytype_regex.sub(self.replace, s)
        return super().decode(s, **kwargs)

    @staticmethod
    def replace(match):
        s = match.group()
        val = s.replace('\"', '').split(':')[-1]
        if val == 'True':
            return 'true'
        elif val == 'False':
            return 'false'
        return val


def json_dumps(obj, indent=None):
    return json.dumps(obj, indent=indent)


def json_loads(s):
    try:
        return json.loads(s,
                          object_pairs_hook=OrderedDict,
                          cls=JSONDecoder)
    except Exception as e:
        raise JSONEncodeError(
            'Invalid JSON: {}.'.format(e)
        )


def inject_params(
        content: str,
        params: dict,
        calls: int=0,
        raise_exception: bool=True
):
    """Inject params to content."""

    circular_threshold = 100

    if calls > circular_threshold:
        if raise_exception:
            raise CircularInjectError(
                'Circular injections detected.'
            )
        return content

    calls += 1

    def replace(match):
        whole, key = match.groups()
        try:
            val = params[key]
            if not isinstance(val, str):
                return 'pytype:{}'.format(params[key])
            return val
        except KeyError:
            if raise_exception:
                raise InjectKeyError(
                    message=_('Injection key `%(key)s` does not exist.') % {
                        'key': key
                    },
                    key=key
                )
            return whole

    content = inject_regex.sub(replace, content)

    if inject_regex.search(content):
        return inject_params(
            content=content,
            params=params,
            calls=calls,
            raise_exception=raise_exception
        )

    return content


def model_to_dict(instance: Model, fields=None, exclude=None):
    if hasattr(instance, 'to_dict'):
        return instance.to_dict()
    else:
        return model_to_dict_default(instance, fields=fields, exclude=exclude)


class GlobalSettingsHandler:
    """Global settings handler."""

    cache_prefix = 'globals'

    def __init__(self):
        self.defaults = GLOBAL_SETTINGS_DEFAULTS

    def get(self, key, default=None):
        return cache.get(
            self._make_key(key),
            default=self.defaults.get(key, default)
        )

    def set(self, key, value):
        return cache.set(
            self._make_key(key),
            value,
            timeout=None
        )

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def _make_key(self, key):
        return '{}:{}'.format(
            self.cache_prefix,
            key
        )


global_settings = GlobalSettingsHandler()
