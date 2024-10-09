from ttex.config import Config, ConfigFactory
from .. import dummy_log_handler


class DummyConfig(Config):
    def __init__(self, a, b, c=None, d=3):
        self.a = a
        self.b = b
        self.c = c
        self.d = d


class EmptyConfig(Config):
    def __init__(self):
        pass
