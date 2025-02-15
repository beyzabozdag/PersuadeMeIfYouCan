from pmiyc.alternating_game import AlternatingGame
from pmiyc.parser import GameParser
from pmiyc.constants import *
from pmiyc.utils import *
from pmiyc.agent_message import AgentMessage
from games.prompt import *
from typing import List

import json
import random


class PersuasionAgentMessage(AgentMessage):
    def __init__(self):
        super().__init__()
        
    def message_to_other_player(self):
        message = self.public[MESSAGE_TAG]

        r = f"""<{OTHER_AGENT_MESSAGE_TAG}> {message} </{OTHER_AGENT_MESSAGE_TAG}>"""
        return r
    
class PersuasionGameDefaultParser(GameParser):
    def instantiate_prompt(self, agent_name, question, claim, strategy=None, game_type=None):
        if game_type == "misinformation":
            if agent_name == PERSUADEE:
                return persuadee_prompt_misinformation(claim, question=question)
            elif agent_name == PERSUADER:
                return persuader_prompt_misinformation(claim, question=question)
            else:
                raise ValueError("Unknown agent name")
        else:
            if agent_name == PERSUADEE:
                return persuadee_prompt(claim, question=question)
            elif agent_name == PERSUADER:
                return persuader_prompt(claim, question=question)
            else:
                raise ValueError("Unknown agent name")
    
    def parse(self, response):
        ms = PersuasionAgentMessage()
        
        try:
            ms.add_public(MESSAGE_TAG, response[MESSAGE_TAG])
            ms.add_secret(RANKING_TAG, response[RANKING_TAG])  
        except Exception as e:
            print(f"Conversation failed. Error: {e}")
            raise e

        return ms
        

class PersuasionGame(AlternatingGame):

    def __init__(self, 
                 players: List,
                 claims: List[str],
                 belief_file: str,
                 question: str = None,
                 iterations: int = 2, 
                 log_dir: str = ".logs", 
                 log_path = None, 
                 strategy: List[str] = None, 
                 end_game = False,
                 visible_ranks = False,
                 test = False,
                 player_roles: List[str] = ["", ""]
                 ):
        
        super().__init__(players=players, log_dir=log_dir, log_path=log_path, iterations=iterations)
        
        self.question = question
        self.claims = claims
        self.strategy = strategy
        self.end_game = end_game
        self.visible_ranks = visible_ranks
        self.test = test
        self.player_roles = player_roles
        self.belief_file = belief_file

        # set the game interface
        self.game_interface = PersuasionGameDefaultParser()

        # add logging information
        self.game_state: List[dict] = [
            {
                "current_iteration": "START",
                "turn": "None",
                "settings": dict(
                    claims=self.claims,
                ),
            }
        ]

        # init players
        self.init_players()

    def init_players(self):
        
        settings = self.game_state[0]["settings"]

        # Now we have to tell each agent of its role for each player
        for idx, player in enumerate(self.players):

            # we instantiate a player specific prompt, meaning that
            # each agent is going to have it's own prompt

            game_prompt = self.game_interface.instantiate_prompt(
                player.agent_name, 
                question=self.question, 
                claim=self.claims[idx],
                strategy=self.strategy
                )

            player.init_agent(game_prompt, claim=self.claims[idx])
            

    def game_over(self):
        if self.current_iteration >= self.iterations:
            return True
        # if end_game is true, and it is the persuadee's turn and 
        # the persuadee has given a 5 in the most recent turn, return True
        if self.end_game and self.turn == 1:
            if self.conversation[self.current_iteration]["response"][RANKING_TAG_INT] == 5:
                return True
        
    
    def after_game_ends(self):
        datum = dict(current_iteration="END", turn="None", summary=dict())
        self.game_state.append(datum)


    def get_initial_response(self):
        persuadee = self.players[1]
        persuadee_claim = self.claims[1]
        model_name = self.players[1].model
        response = None

        message_to_agent = persuadee_starter_prompt()

        # check if the persuadee's initial ranking exists in the db
        # if it does, return it to be added to the conversation history

        # if in test mode, do not save or attempt to retrieve the persuadee's initial ranking
        if not self.test:
            # check the model_beliefs.json file for the persuadee's initial ranking
            with open(self.belief_file, "r") as f:
                data = json.load(f)
                if model_name in data and persuadee_claim in data[model_name]:
                    print("Retrieving persuadee's initial ranking from model_beliefs.json")
                    response = data[model_name][persuadee_claim]
                    response_str = get_response_str(response, visible_ranks=self.visible_ranks)

                    # update agent history
                    persuadee.update_conversation_tracking("user", message_to_agent)
                    persuadee.update_conversation_tracking("assistant", response_str)

        if response is None:
            response = self.players[1].step(message_to_agent, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=self.visible_ranks)

            if not self.test:
                # save the persuadee's initial ranking to the model_beliefs.json file
                with open(self.belief_file, "r") as f:
                    data = json.load(f)
                    if model_name not in data:
                        data[model_name] = {}
                    data[model_name][persuadee_claim] = response
                    with open(self.belief_file, "w") as f:
                        json.dump(data, f, indent=4)

        return response

    def run(self):
        
        # first prompt the persuadee with the claim
        # to get initial belief
        
        self.turn = 1 # persuadee's turn
        response = self.get_initial_response()
        self.conversation[self.current_iteration] = {
            "turn": self.turn, 
            "response": response,
            "agent_history": self.players[1].copy_agent_conversation()
            }
        
        self.write_game_state(self.players, response)

        # for debug
        self.view_state(
            ignore=[
                "player_public_answer_string",
                "player_public_info_dict",
                "player_private_info_dict",
                "player_state",
            ]
        )

        # for logging / reproducibility
        self.log_state()
        self.get_next_player()
        print("=============\n")
        
        # start with iteration = 1
        for iteration in range(1, self.iterations + 1):
            self.current_iteration = iteration

            # get ratbench state from last iteration
            message = self.read_iteration_message(iteration)

            message += "\n" + reminder_prompt()
            
            # player to take a step/action based on current ratbench state
            response = self.players[self.turn].step(message, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=self.visible_ranks)
            
            self.conversation[self.current_iteration] = {
                "turn": self.turn, 
                "response": response,
                "agent_history": self.players[self.turn].copy_agent_conversation()
                }

            self.write_game_state(self.players, response)

            # for debug
            self.view_state(
                ignore=[
                    "player_public_answer_string",
                    "player_public_info_dict",
                    "player_private_info_dict",
                    "player_state",
                ]
            )

            # for logging / reproducibility
            self.log_state()

            if self.game_over():
                self.after_game_ends()
                self.log_state()
                break

            self.get_next_player()
            print("=============\n")

        
        print("\n--- Conversation Over, asking persuadee's final decision ----\n")
        # ask Persuadee its final decision given the conversation history
        self.current_iteration += 1
        self.turn = 1
        # get ratbench state from last iteration
        message = self.read_iteration_message(self.current_iteration)

        # Add final decision prompt
        message += "\n" + persuadee_final_decision_prompt(self.claims[1])

        response = self.players[self.turn].step(message, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=self.visible_ranks)

        self.conversation[self.current_iteration] = {
            "turn": self.turn, 
            "response": response,
            "agent_history": self.players[self.turn].copy_agent_conversation()
            }

        # update ratbench state
        self.write_game_state(self.players, response)

        # for debug
        self.view_state(
            ignore=[
                "player_public_answer_string",
                "player_public_info_dict",
                "player_private_info_dict",
                "player_state",
            ]
        )

        # log final state
        self.log_state()
        
        self.after_game_ends()
        self.log_state()
        
        return self.conversation




class MisinformationGame(AlternatingGame):

    def __init__(self, 
                 players: List,
                 claim: List[str],
                 belief_file: str,
                 question: str = None,
                 iterations: int = 2, 
                 log_dir: str = ".logs", 
                 log_path = None, 
                 strategy: List[str] = None, 
                 end_game = False,
                 visible_ranks = False,
                 test = False,
                 player_roles: List[str] = ["", ""]
                 ):
        
        super().__init__(players=players, log_dir=log_dir, log_path=log_path, iterations=iterations)
        
        self.question = question
        self.claim = claim
        self.strategy = strategy
        self.end_game = end_game
        self.visible_ranks = visible_ranks
        self.test = test
        self.player_roles = player_roles
        self.belief_file = belief_file

        # set the game interface
        self.game_interface = PersuasionGameDefaultParser()

        # add logging information
        self.game_state: List[dict] = [
            {
                "current_iteration": "START",
                "turn": "None",
                "settings": dict(
                    claim=self.claim,
                ),
            }
        ]

        # init players
        self.init_players()

    def init_players(self):
        
        settings = self.game_state[0]["settings"]

        # Now we have to tell each agent of its role for each player
        for idx, player in enumerate(self.players):

            # we instantiate a player specific prompt, meaning that
            # each agent is going to have it's own prompt

            game_prompt = self.game_interface.instantiate_prompt(
                player.agent_name, 
                question=self.question, 
                claim=self.claim,
                strategy=self.strategy,
                game_type="misinformation"
                )

            player.init_agent(game_prompt, claim=self.claim)

    def game_over(self):
        if self.current_iteration >= self.iterations:
            return True
        # if end_game is true, and it is the persuadee's turn and 
        # the persuadee has given a 5 in the most recent turn, return True
        if self.end_game and self.turn == 1:
            if self.conversation[self.current_iteration]["response"][RANKING_TAG_INT] == 5:
                return True
           
    def after_game_ends(self):
        datum = dict(current_iteration="END", turn="None", summary=dict())
        self.game_state.append(datum)

    def get_initial_response(self):
        persuadee = self.players[1]
        persuadee_claim = self.claim
        model_name = self.players[1].model
        response = None

        message_to_agent = persuadee_starter_prompt_misinformation()

        # check if the persuadee's initial ranking exists in the db
        # if it does, return it to be added to the conversation history

        # if in test mode, do not save or attempt to retrieve the persuadee's initial ranking
        if not self.test:
            # check the model_beliefs.json file for the persuadee's initial ranking
            with open(self.belief_file, "r") as f:
                data = json.load(f)
                if model_name in data and persuadee_claim in data[model_name]:
                    print("Retrieving persuadee's initial ranking from model_beliefs.json")
                    response = data[model_name][persuadee_claim]
                    response_str = get_response_str(response, visible_ranks=self.visible_ranks)

                    # update agent history
                    persuadee.update_conversation_tracking("user", message_to_agent)
                    persuadee.update_conversation_tracking("assistant", response_str)

        if response is None:
            response = self.players[1].step(message_to_agent, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=self.visible_ranks)

            if not self.test:
                # save the persuadee's initial ranking to the model_beliefs.json file
                with open(self.belief_file, "r") as f:
                    data = json.load(f)
                    if model_name not in data:
                        data[model_name] = {}
                    data[model_name][persuadee_claim] = response
                    with open(self.belief_file, "w") as f:
                        json.dump(data, f, indent=4)

        return response

    def run(self):
        
        # first prompt the persuadee with the claim
        # to get initial belief
        
        self.turn = 1 # persuadee's turn
        response = self.get_initial_response()
        self.conversation[self.current_iteration] = {
            "turn": self.turn, 
            "response": response,
            "agent_history": self.players[1].copy_agent_conversation()
            }
        
        self.write_game_state(self.players, response)

        # for debug
        self.view_state(
            ignore=[
                "player_public_answer_string",
                "player_public_info_dict",
                "player_private_info_dict",
                "player_state",
            ]
        )

        # for logging / reproducibility
        self.log_state()
        self.get_next_player()
        print("=============\n")
        
        # start with iteration = 1
        for iteration in range(1, self.iterations + 1):
            self.current_iteration = iteration

            # get ratbench state from last iteration
            message = self.read_iteration_message(iteration)

            message += "\n" + reminder_prompt()
            
            # player to take a step/action based on current ratbench state
            response = self.players[self.turn].step(message, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=self.visible_ranks)
            
            self.conversation[self.current_iteration] = {
                "turn": self.turn, 
                "response": response,
                "agent_history": self.players[self.turn].copy_agent_conversation()
                }

            self.write_game_state(self.players, response)

            # for debug
            self.view_state(
                ignore=[
                    "player_public_answer_string",
                    "player_public_info_dict",
                    "player_private_info_dict",
                    "player_state",
                ]
            )

            # for logging / reproducibility
            self.log_state()

            if self.game_over():
                self.after_game_ends()
                self.log_state()
                break

            self.get_next_player()
            print("=============\n")

        
        print("\n--- Conversation Over, asking persuadee's final decision ----\n")
        # ask Persuadee its final decision given the conversation history
        self.current_iteration += 1
        self.turn = 1
        # get ratbench state from last iteration
        message = self.read_iteration_message(self.current_iteration)

        # Add final decision prompt
        message += "\n" + persuadee_final_decision_prompt_misinformation(self.claim)

        response = self.players[self.turn].step(message, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=self.visible_ranks)

        self.conversation[self.current_iteration] = {
            "turn": self.turn, 
            "response": response,
            "agent_history": self.players[self.turn].copy_agent_conversation()
            }

        # update ratbench state
        self.write_game_state(self.players, response)

        # for debug
        self.view_state(
            ignore=[
                "player_public_answer_string",
                "player_public_info_dict",
                "player_private_info_dict",
                "player_state",
            ]
        )

        # log final state
        self.log_state()
        
        self.after_game_ends()
        self.log_state()
        
        return self.conversation
