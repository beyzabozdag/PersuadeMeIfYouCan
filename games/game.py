from persuasion_arena.alternating_game import AlternatingGame
from persuasion_arena.parser import GameParser
from persuasion_arena.constants import *
from persuasion_arena.utils import *
from persuasion_arena.agent_message import AgentMessage
from games.prompt import persuadee_prompt, persuader_prompt

from typing import List
import random


class PersuasionAgentMessage(AgentMessage):
    def __init__(self):
        super().__init__()
        
    def message_to_other_player(self):
        message = self.public[MESSAGE_TAG]

        r = f"""<{OTHER_AGENT_MESSAGE_TAG}> {message} </{OTHER_AGENT_MESSAGE_TAG}>"""
        return r
    
class PersuasionGameDefaultParser(GameParser):
    def instantiate_prompt(self, agent_type, question, claim):
        if agent_type == PERSUADEE:
            return persuadee_prompt(question, claim)
        elif agent_type == PERSUADER:
            return persuader_prompt(question, claim)
        else:
            raise ValueError("Unknown agent name")
    
    def parse(self, response):
        ms = PersuasionAgentMessage()
        try:
            if MESSAGE_TAG in response:
                message = get_tag_contents(response, MESSAGE_TAG)
                ms.add_public(MESSAGE_TAG, message)

            if RANKING_TAG in response:
                ranking = get_tag_contents(response, RANKING_TAG)
                ms.add_secret(RANKING_TAG, ranking)

            if FINAL_DECISION_TAG in response:
                final_decision = get_tag_contents(response, FINAL_DECISION_TAG)
                ms.add_secret(FINAL_DECISION_TAG, final_decision)
                ms.add_public(MESSAGE_TAG, "") # no further message to the other agent
        
        except Exception as e:
            print(f"Error parsing response: {response}")
            
        return ms
        

class PersuasionGame(AlternatingGame):

    def __init__(self, players: List, player_roles: List[str], question, player_claims: List[str], log_dir: str = ".logs", log_path=None, iterations: int = 2):
        super().__init__(players=players, log_dir=log_dir, log_path=log_path, iterations=iterations)

        self.question = question
        self.player_claims = player_claims
        
        self.game_interface = PersuasionGameDefaultParser()

        #################
        # Game State    #
        #################

        self.player_roles = player_roles

        ####################################
        # Adding Some Logging Information  #
        ####################################

        self.game_state: List[dict] = [
            {
                "current_iteration": "START",
                "turn": "None",
                "settings": dict(
                    player_roles=self.player_roles,
                ),
            }
        ]

        # init players
        self.init_players()

    def init_players(self):
        
        settings = self.game_state[0]["settings"]

        #################
        # Agent Setup   #
        #################

        # Now we have to tell each GPT agent of its role
        # for each player
        for idx, player in enumerate(self.players):

            # we instantiate a player specific prompt, meaning that
            # each agent is going to have it's own prompt with its own resources

            game_prompt = self.game_interface.instantiate_prompt(player.agent_name, self.question, self.player_claims[idx])
            print(game_prompt)

            player.init_agent(game_prompt, role=settings["player_roles"][idx])
            

    def game_over(self):
        return self.current_iteration >= self.iterations
    
    def after_game_ends(self):
        datum = dict(current_iteration="END", turn="None", summary=dict())

        self.game_state.append(datum)




