import os
import warnings

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
        config_filename = os.environ.get('CONFIGFACTORY_CONFIG')
        if config_filename is None:
            warnings.warn(
                "Configuration environment variable (CONFIGFACTORY_CONFIG)"
                " is not set. Using default settings."
            )
            return
        self.read(config_filename)


config = ConfigParser()
config.setup()

get = config.get
getfloat = config.getfloat
getint = config.getint
getboolean = config.getboolean
