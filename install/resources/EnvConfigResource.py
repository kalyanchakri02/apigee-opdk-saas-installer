# resources/BaseResource.py
from abc import ABC, abstractmethod
from install.setup.Connection import  Connection

class EnvConfigResource(ABC):
    def __init__(self, name, config, connection : Connection):
        self.name = name
        self.config = config
        self.connection = connection

    @abstractmethod
    def apply(self):
        pass

