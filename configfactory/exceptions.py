class InjectKeyError(Exception):

    def __init__(self, message: str, key: str):
        self._message = message
        self._key = key

    @property
    def message(self):
        return self._message

    @property
    def key(self) -> str:
        return self._key

    def __str__(self):
        return self.message


class CircularInjectError(RuntimeError):
    pass


class JSONEncodeError(Exception):
    pass


class ConfigUpdateError(Exception):
    pass


class ComponentDeleteError(Exception):

    def __init__(self, message: str):
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    def __str__(self):
        return self.message
