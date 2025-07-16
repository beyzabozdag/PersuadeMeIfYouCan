import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
from dotenv import load_dotenv
import inspect
import random
from tenacity import retry, stop_after_attempt, wait_fixed

from pmiyc.agents import *
from games.game import PersuasionGame, MisinformationGame
from pmiyc.constants import *
from datasets import load_dataset

import random
from datasets import load_dataset
from datasets.utils.logging import set_verbosity_error, disable_progress_bar

from pmiyc.utils import get_tag_contents

import json
import pprint
import pandas as pd
import argparse

load_dotenv()

# set seed
random.seed(42)
set_verbosity_error()
disable_progress_bar()

def get_args():
    parser = argparse.ArgumentParser()
    # required number of iterations
    parser.add_argument("--iterations", type=int, required=True, help="Number of iterations")
    # required model1 name
    parser.add_argument("--model1", type=str, required=True, help="Model name of the first agent")
    # required model2 name
    parser.add_argument("--model2", type=str, required=True, help="Model name of the second agent")
    # required model 1 path 
    parser.add_argument("--model1_path", type=str, required=True, help="Model path of the first agent")
    # required model 2 path
    parser.add_argument("--model2_path", type=str, required=True, help="Model path of the second agent")
    # results/log directory
    parser.add_argument("--log_dir", type=str, default="./results/misinformation", help="Log directory")
    # results/log subdirectory name
    parser.add_argument("--dir_name", type=str, default="model1_model2", help="Subdirectory name")
    # belief dir
    parser.add_argument("--belief_dir", type=str, default="./initial_beliefs/initial_beliefs_misinfo", help="Initial beliefs directory")
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

    retval = [{"question": elem["question"], "claim": elem["incorrect_answers"][0]} for elem in dataset]

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
    if "gpt" in model1.lower() or "o4" in model1.lower():
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

    if "gpt" in model2.lower() or "o4" in model2.lower():
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

    claims_to_skip = set()
    for elem in results:
        claims_to_skip.add(elem["i"])

    if len(claims_to_skip) > 0:
        print(f"Skipping {len(claims_to_skip)} claims that are already processed.")

    START_INDEX = 0

    for i, elem in enumerate(get_claims()[START_INDEX:1]):
        if i in claims_to_skip:
            print(f"Skipping claim {i} as it is already processed.")
            continue

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
            skipped.append(elem)
            continue

        data = {
            "i": j,
            "model1": model1,
            "model2": model2,
            "question": elem["question"],
            "claim": elem["claim"],
            "conversation": conversation,
            "conversation_str": conv_to_str(conversation)
        }

        results.append(data)

        # write results to json file
        with open(f"{log_dir}/{dir_name}/results.json", "w") as f:
            json.dump(results, f, indent=4)

    try:
        # sort results by "i" key in every element
        results.sort(key=lambda x: x["i"])
        # write results to json file
        with open(f"{log_dir}/{dir_name}/results.json", "w") as f:
            json.dump(results, f, indent=4)

    except Exception as e:
        print(f"Error sorting results: {e}")

    # write the skipped claims to a file
    if not os.path.exists(f"{log_dir}/{dir_name}"):
        os.makedirs(f"{log_dir}/{dir_name}")
    with open(f"{log_dir}/{dir_name}/skipped_claims.txt", "w") as f:
        for claim in skipped:
            f.write(f"{claim}\n")


    print(f"Completed misinformation game for persuader {model1} and persuadee {model2} with {len(results)} claims.")


if __name__ == "__main__":
    args = get_args()

    iterations = args.iterations

    model1 = args.model1
    model1_path = args.model1_path

    model2 = args.model2
    model2_path = args.model2_path
    
    log_dir = args.log_dir
    dir_name = args.dir_name

    end_game = args.end_game
    visible_ranks = args.visible_ranks
    test = args.test

    belief_file = f"{args.belief_dir}/{dir_name.split('_')[1]}.json"

    # check if beliefs file exists, if not create empty json file
    if not os.path.exists(belief_file):
        print(f"Creating empty belief file: {belief_file}")
        os.makedirs(os.path.dirname(belief_file), exist_ok=True)
        # create empty json file
        with open(belief_file, "w") as f:
            json.dump({}, f, indent=4)

    main()