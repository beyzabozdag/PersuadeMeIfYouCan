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
from games.new_game.game import PersuasionGame
from persuasion_arena.constants import *
from datasets import load_dataset

import random
from datasets import load_dataset
from datasets.utils.logging import set_verbosity_error, disable_progress_bar

from persuasion_arena.utils import get_tag_contents
from evaluator.evaluate import evaluate

import json
import pprint
import pandas as pd

# set seed
random.seed(42)
set_verbosity_error()
disable_progress_bar()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_claims():
    dataset = load_dataset("Anthropic/persuasion", split="train")
    # get all claims from the dataset
    unique_claims = set([item["claim"] for item in dataset])

    # filter out control claims
    control_claims = set([item["claim"] for item in dataset if item["source"] == "Control"])
    unique_claims = unique_claims - control_claims

    # add claims from "subjective_claims.csv"
    subjective_claims = pd.read_csv("../pre_assesment/subjective_claims.csv")
    subj = set()
    for claim in subjective_claims["Claim"]:
        subj.add(claim)
    
    retval = sorted(list(unique_claims)) + sorted(list(subj))
    return retval

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

    results = json.load(open(f"./.logs/persuasion_game/test/{dir_name}/results.json", "r")) if os.path.exists(f"./.logs/persuasion_game/test/{dir_name}/results.json") else []

    skipped = []

    for i, claim in enumerate(get_claims()[:20]):
        a1, a2 = get_agents()
        print(f"{i}: {claim}")

        game = PersuasionGame(
            players=[a1, a2],
            claims= [claim, claim],
            iterations=7,
            log_dir= f"./.logs/persuasion_game/test/{dir_name}",
            end_game=True,
            visible_ranks=True,
            test=False
        )

        try:
            conversation = game.run()
        
        except Exception as e:
            print(f"Error: {e}")
            skipped.append(claim)
            continue

        data = {
            "i": i,
            "model1": model1,
            "model2": model2,
            "claim": claim,
            "conversation": conversation,
        }

        results.append(data)

        # write results to json file
        with open(f"./.logs/persuasion_game/test/{dir_name}/results.json", "w") as f:
            json.dump(results, f, indent=4)

    # report the skipped claims
    print("Skipped:")
    for i, claim in skipped:
        print(f"{i}: {claim}")



if __name__ == "__main__":
    model1 = "meta-llama/Llama-3.1-8B-Instruct"
    model2 = "meta-llama/Llama-3.1-8B-Instruct"
    dir_name = "llama8b-llama8b_visible_ranks_end_game"
    main()