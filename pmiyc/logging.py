import json
from pmiyc.agents.agents import Agent
from pmiyc.parser import GameParser


class GameDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs
        )

    def object_hook(self, obj):
        if "_type" not in obj:
            return obj
        # type = obj["_type"]
        # if type == "support":
        #     return Support.from_json(obj["_value"])
        return obj


class GameEncoder(json.JSONEncoder):
    def default(self, obj):
        # TODO: consider adding the support object here
        # if isinstance(obj, Support):
        #     return {"_type": "support", "_value": obj.json()}

        if isinstance(obj, Agent):
            return obj.get_state()

        if isinstance(obj, GameParser):
            return {"class": obj.__class__.__name__}

        return super().default(obj)