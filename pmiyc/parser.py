import copy
from abc import ABC, abstractmethod
from pmiyc.utils import *
from pmiyc.constants import *


class GameParser(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def instantiate_prompt(self, **kwargs):
        """
        Returns the inital ratbench prompt
        """
        pass

    @abstractmethod
    def parse(self, response):
        """
        Parses the ratbench response
        """
        pass

    @classmethod
    def from_dict(cls, state):
        state = copy.deepcopy(state)
        class_name = state.pop("class")
        subclasses = cls.get_all_subclasses()
        constructor = (
            cls
            if class_name == cls.__name__
            else next(
                (sub for sub in subclasses if sub.__name__ == class_name), None
            )
        )
        if constructor:
            obj = constructor(**state)
            return obj
        else:
            raise ValueError(f"Unknown subclass: {class_name}")

    @classmethod
    def get_all_subclasses(cls):
        subclasses_set = set()
        # Recursively get subclasses of subclasses
        for subclass in cls.__subclasses__():
            subclasses_set.add(subclass)
            subclasses_set.update(subclass.get_all_subclasses())

        return list(subclasses_set)