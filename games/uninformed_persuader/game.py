import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import json

from persuasion_arena.agents.agents import Agent
from games.uninformed_persuader.prompt import persuader_system_prompt, persauder_user_prompt
from persuasion_arena.constants import *

class UninformedPersuader():
    def __init__(self, persuader, file_path: str):
        self.persuader = persuader 
        self.file_path = file_path

        # if file doesn't exist, create it and add empty dict
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write(json.dumps({self.persuader.model: {}}))

    def generate(self, claim):

        if self.check_if_claim_exists(claim):
            print(f"Already exists in the file.")
            return

        self.persuader.init_agent(persuader_system_prompt())
        response = self.persuader.step(persauder_user_prompt(claim), expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=True)

        print(response)

        self.save_to_file(claim, response)

    def check_if_claim_exists(self, claim):
        with open(self.file_path, "r") as f:
            data = json.load(f)
            return claim in data[self.persuader.model]

    def save_to_file(self, claim, response):
        # first load, then add, then save
        with open(self.file_path, "r") as f:
            data = json.load(f)
            data[self.persuader.model][claim] = response

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

