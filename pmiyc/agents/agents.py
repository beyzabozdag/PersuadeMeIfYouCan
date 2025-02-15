from abc import ABC, abstractmethod
import copy
from pmiyc.constants import *
from copy import deepcopy
from pmiyc.utils import advanced_parse, support_to_int, get_response_str
from pmiyc.constants import *


class Agent(ABC):
    """
    Representing a Single LLM Agent
    """

    agent_class = __qualname__

    def __init__(self, agent_name: str):
        """
        Base agent class, all agents should inherit from this class. Class
        is abstract and provides a template for the methods that should be
        implemented by the child classes.

        :param agent_name:
        :param kwargs:
        """
        self.model = None
        self.agent_name = agent_name
        self.claim = None
        # self.turn = 0

        self.prompt_entity_initializer = None

        if self.agent_name not in [PERSUADER, PERSUADEE]:
            raise ValueError(
                f"Agent name must be either {PERSUADER} or {PERSUADEE}"
            )

    @abstractmethod
    def chat(self):
        pass

    @abstractmethod
    def update_conversation_tracking(self, entity, message):
        pass

    def set_state(self, state_dict):
        self.conversation = state_dict["conversation"]
        self.run_epoch_time_ms = state_dict["run_epoch_time_ms"]

    def dump_conversation(self, file_name):
        with open(file_name, "w") as f:
            for index, text in enumerate(self.conversation):
                c = text["content"].replace("\n", " ")

                if index % 2 == 0:
                    f.write(f"= = = = = Iteration {index // 2} = = = = =\n\n")
                    f.write(f'{text["role"]}: {c}' "\n\n")
                else:
                    f.write(f'\t\t{text["role"]}: {c}' "\n\n")

    def init_agent(self, system_prompt, role="", claim=None):
        self.claim = claim
        self.update_conversation_tracking(self.prompt_entity_initializer, system_prompt + role)

    def resume_conversation(self, conversation_history):
        self.conversation = conversation_history

    def think(self, try_count=5, expected_keys=None, visible_ranks=False):
        """
        Think method calls the chat function and updates the history of the conversation.
        Next time the agents chats, it will use the updated history.

        :return:
        """
        # call agent / make agent think
        response = None
        while response is None and try_count > 0:
            response = self.chat()
            if expected_keys and response:
                response = advanced_parse(response, expected_keys)
            try_count -= 1

        # format response into a string before adding to conversation history
        response_str = get_response_str(response, visible_ranks=visible_ranks)
        # update agent history
        self.update_conversation_tracking("assistant", response_str)
        
        return response

    def step(self, message, expected_keys=None, visible_ranks=False):
        """
        Make agent take a step in a ratbench:

        1. get state from negobench
        2. genereate a response to state
        3. return response

        """

        if message:
            self.update_conversation_tracking("user", message)

        response = self.think(expected_keys = expected_keys, visible_ranks=visible_ranks)

        if response and RANKING_TAG in response:
            ranking = support_to_int(response[RANKING_TAG])
            response[RANKING_TAG_INT] = ranking

        return response

    def get_state(self):
        try:
            c = {
                "class": self.__class__.__name__,
                **deepcopy(self).__dict__,
            }
        except Exception as e:
            print(e)
            for k, v in self.__dict__.items():
                print(k, v, type(v))
            exit()

        return c

    @classmethod
    def from_dict(cls, state_dict):
        state_dict = copy.deepcopy(state_dict)
        class_name = state_dict.pop("class")
        subclasses = cls.get_all_subclasses()
        constructor = (
            cls
            if class_name == cls.__name__
            else next(
                (sub for sub in subclasses if sub.__name__ == class_name), None
            )
        )
        if constructor:
            obj = constructor(**state_dict)
            obj.set_state(state_dict)
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

    def copy_agent_conversation(self):
        return deepcopy(self.conversation)
        
    def reset(self, full_reset=False):
        if full_reset:
            # only keep the system prompt in the conversation history
            self.conversation = [self.conversation[0]]
        else:
            # only remove the last user and assistant messages
            self.conversation = self.conversation[:-2]