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
from games.new_game.game import PersuasionGame,MisinformationGame
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
import argparse

# set seed
random.seed(42)
set_verbosity_error()
disable_progress_bar()

def get_args():
    parser = argparse.ArgumentParser()
    # required model1 name
    parser.add_argument("--model1", type=str, required=True, help="Model name of the first agent")
    # required model2 name
    parser.add_argument("--model2", type=str, required=True, help="Model name of the second agent")
    # required model 1 path 
    parser.add_argument("--model1_path", type=str, required=True, help="Model path of the first agent")
    # required model 2 path
    parser.add_argument("--model2_path", type=str, required=True, help="Model path of the second agent")
    # results/log directory
    parser.add_argument("--log_dir", type=str, default="/shared/storage-01/users/mehri2/Persuasion/PersuasionArena/logs/misinformation", help="Log directory")
    # results/log subdirectory name
    parser.add_argument("--dir_name", type=str, default="model1_model2", help="Subdirectory name")
    # end game flag
    parser.add_argument("--end_game", action="store_true", help="End game flag")
    # visible ranks flag
    parser.add_argument("--visible_ranks", action="store_true", help="Make ranks invisible")
    # test flag
    parser.add_argument("--test", action="store_true", help="Test flag")

    return parser.parse_args()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_claims():
    dataset = load_dataset("truthfulqa/truthful_qa", "generation")["validation"]

    retval = [{"question": elem["question"], "claim": random.choice(elem["incorrect_answers"])} for elem in dataset]

    print(f"Number of claims: {len(retval)}")
    print()
    return retval


def conv_to_str(conversation):
    conversation_str = ""
    for iter in range(len(conversation)):
        agent = conversation[iter]["turn"]
        message = conversation[iter]["response"]["message"]
        conversation_str += f"Agent {agent}: {message}\n\n"
    return conversation_str.strip()

def get_agents():
    print("\n\n", "-"*50)
    if "gpt" in model1.lower():
        print("Using ChatGPTAgent for model1")
        a1 = ChatGPTAgent(
            model=model1,
            agent_name=PERSUADER
        )
    elif "claude" in model1.lower():
        print("Using ClaudeAgent for model1")
        a1 = ClaudeAgent(
            model=model1,
            agent_name=PERSUADER
        )
    else:
        print("Using LLamaChatAgent for model1")
        a1 = LLamaChatAgent(
            model=model1,
            agent_name=PERSUADER,
            base_url=model1_path,
        )

    if "gpt" in model2.lower():
        print("Using ChatGPTAgent for model2")
        a2 = ChatGPTAgent(
            model=model2,
            agent_name=PERSUADEE
        )
    elif "claude" in model2.lower():
        print("Using ClaudeAgent for model2")
        a2 = ClaudeAgent(
            model=model2,
            agent_name=PERSUADEE
        )
    else:
        print("Using LLamaChatAgent for model2")
        a2 = LLamaChatAgent(
            model=model2,
            agent_name=PERSUADEE,
            base_url=model2_path,
        )

    return a1, a2

def main():

    results = json.load(open(f"{log_dir}/{dir_name}/results.json", "r")) if os.path.exists(f"{log_dir}/{dir_name}/results.json") else []

    skipped = []

    START_INDEX = 0

    for i, elem in enumerate(get_claims()[START_INDEX:]):
        a1, a2 = get_agents()
        print("\n\n", "-"*50)

        j = i + START_INDEX
        
        print(f"{j}: {elem}")

        game = MisinformationGame(
            players=[a1, a2],
            question=elem["question"],
            claim= elem["claim"],
            iterations=7,
            log_dir= f"{log_dir}/{dir_name}/.logs",
            end_game=end_game,
            visible_ranks=visible_ranks,
            test=test,
            belief_file=belief_file
        )

        try:
            conversation = game.run()
        
        except Exception as e:
            print(f"Error: {e}")
            skipped.append(claim)
            continue

        data = {
            "i": j,
            "model1": model1,
            "model2": model2,
            "questoin": elem["question"],
            "claim": elem["claim"],
            "conversation": conversation,
            "conversation_str": conv_to_str(conversation)
        }

        results.append(data)

        # write results to json file
        with open(f"{log_dir}/{dir_name}/results.json", "w") as f:
            json.dump(results, f, indent=4)

    # write the skipped claims to a file
    with open(f"{log_dir}/{dir_name}/skipped_claims2.txt", "w") as f:
        for claim in skipped:
            f.write(f"{claim}\n")



if __name__ == "__main__":
    args = get_args()

    model1 = args.model1
    model1_path = args.model1_path

    model2 = args.model2
    model2_path = args.model2_path
    
    # vr = visible ranks, 3t = persuder gets 3 turns, i = informed persuader
    log_dir = args.log_dir
    dir_name = args.dir_name

    end_game = args.end_game
    visible_ranks = args.visible_ranks
    test = args.test

    belief_file = f"/shared/storage-01/users/mehri2/Persuasion/PersuasionArena/logs/misinformation/initial_beliefs/{dir_name.split('_')[1]}.json"

    # check if beliefs file exists, if not create empty json file
    if not os.path.exists(belief_file):
        print(f"Creating empty belief file: {belief_file}")
        with open(belief_file, "w") as f:
            json.dump({}, f, indent=4)

    # # print all arguments
    # print("\n\n", "-"*50)
    # print("Arguments:")
    # for arg in vars(args):
    #     print(f"{arg}: {getattr(args, arg)}")
    # print("-"*50, "\n\n")

    main()