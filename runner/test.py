import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
from dotenv import load_dotenv
import inspect
import random
from tenacity import retry, stop_after_attempt, wait_fixed

from persuasion_arena.agents import *
from games.game import PersuasionGame
from games.strategies import persuasive_strategies
from persuasion_arena.constants import *
from datasets import load_dataset

import random
from datasets import load_dataset
from datasets.utils.logging import set_verbosity_error, disable_progress_bar

from persuasion_arena.utils import get_tag_contents
from evaluator.evaluate import evaluate

import json

import pandas as pd

# set seed
random.seed(42)
set_verbosity_error()
disable_progress_bar()

load_dotenv("../.env.local")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_claims():
    dataset = load_dataset("Anthropic/persuasion", split="train")
    # get all claims from the dataset
    unique_claims = set([item["claim"] for item in dataset])

    # add claims from "subjective_claims.csv"
    subjective_claims = pd.read_csv("../pre_assesment/subjective_claims.csv")
    subj = set()
    for claim in subjective_claims["Claim"]:
        subj.add(claim)
    
    retval = sorted(list(unique_claims)) + sorted(list(subj))
    return retval

def get_conversation_string(conversation_dict):
    conversation = ""
    for iteration, utterance in conversation_dict.items():
        agent = "Agent 1" if utterance[0] == 0 else "Agent 2"
        if iteration == len(conversation_dict):
            message = get_tag_contents(utterance[1], FINAL_DECISION_TAG) # use final decision tag
        else:
            message = get_tag_contents(utterance[1], MESSAGE_TAG)
        conversation += f"Turn: {iteration}\n{agent}: {message}\n\n"

    return conversation.strip()

def get_agents():
    a1 = LLamaChatAgent(
        model=model1,
        agent_name=PERSUADER,
        base_url="http://localhost:8000/v1",
    )

    a2 = LLamaChatAgent(
        model=model2,
        agent_name=PERSUADEE,
        base_url="http://localhost:8000/v1",
    )
    
    return a1, a2

def main():

    results = json.load(open(f"./.logs/persuasion_game/subj_claims/{dir_name}/results.json", "r")) if os.path.exists(f"./.logs/persuasion_game/subj_claims/{dir_name}/results.json") else []
    skipped = []


    # for strategy, strategy_description in persuasive_strategies().items():
    #     strategy_dir = "_".join(strategy.lower().split())
    for i, claim in enumerate(get_claims()):

        print(f"{i}: {claim}")

        a1, a2 = get_agents()
        claims = [claim, claim] # same claim for both agents, one is prompted to support it, the other to oppose it

        c = PersuasionGame(
            players=[a1, a2],
            claims=claims,
            question=None, # not needed when claims are enough alone
            iterations=7, # use odd number of iterations, so that agent 2 can make the final decision after agent 1's last turn
            #strategy=[strategy, strategy_description],
            player_roles=[
                "Start persuading!",
                "",
            ],
            log_dir=f"./.logs/persuasion_game/subj_claims/{dir_name}/logs", #/{strategy_dir}",
        )

        try:
            c.run()
        except Exception as e:
            skipped.append((i,claim))
            continue

        conversation = get_conversation_string(c.conversation)
        
        # Use this for the LLM-as-a-Judge evaluation
        # persuasion_success, turn_persuaded = evaluate(claim, conversation)

        data = {
            "model1": model1,
            "model2": model2,
            "claim": claim,
            # "strategy": strategy,
            # "strategy_description": strategy_description,
            # "persuasion_success": persuasion_success,
            # "turn_persuaded": turn_persuaded,
            "conversation_string": conversation,
            "conversation": c.conversation,
        }

        results.append(data)

        # write results to json file
        with open(f"./.logs/persuasion_game/subj_claims/{dir_name}/results.json", "w") as f:
            json.dump(results, f, indent=4)

    # report the skipped claims
    print("Skipped:")
    for i, claim in skipped:
        print(f"{i}: {claim}")


if __name__ == "__main__":
    model1 = "meta-llama/Llama-3.1-8B-Instruct"
    model2 = "meta-llama/Llama-3.1-8B-Instruct"
    dir_name = "llama8b_llama8b_test"

    main()
    
