import os
from configparser import (
    ConfigParser as BaseConfigParser,
    ExtendedInterpolation,
)


class ConfigParser(BaseConfigParser):

    def __init__(self, **kwargs):
        super().__init__(
            interpolation=ExtendedInterpolation(),
            **kwargs
        )

    def setup(self):
        self.read(
            filenames=os.environ.get('CONFIGFACTORY_CONFIG')
        )


config = ConfigParser()
config.setup()

get = config.get
getfloat = config.getfloat
getint = config.getint
getboolean = config.getboolean
