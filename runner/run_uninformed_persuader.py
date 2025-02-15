import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
from persuasion_arena.agents import *
from persuasion_arena.constants import *
from runner.run_new_game import get_claims
from games.uninformed_persuader.game import UninformedPersuader

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--persuader", type=str, required=True)
    parser.add_argument("--persuader_path", type=str, required=True)
    parser.add_argument("--dir_name", type=str, required=True)
    parser.add_argument("--log_dir", type=str, required=True)
    return parser.parse_args()

def get_agent():
    if "gpt" in persuader.lower():
        print("Using ChatGPTAgent for persuader")
        a = ChatGPTAgent(
            model=persuader,
            agent_name=PERSUADER
        )
    elif "claude" in persuader.lower():
        print("Using ClaudeAgent for persuader")
        a = ClaudeAgent(
            model=persuader,
            agent_name=PERSUADER
        )
    else:
        print("Using LLamaChatAgent for persuader")
        a = LLamaChatAgent(
            model=persuader,
            agent_name=PERSUADER,
            base_url=persuader_path,
        )
    return a

def generate_arguments():

    skipped = []
    for i, claim in enumerate(get_claims(anthropic_only=True)):
        print()
        print(i, claim)
        persuader = get_agent()
        game = UninformedPersuader(persuader, f"{log_dir}/{dir_name}.json")
        try:
            game.generate(claim)
        except Exception as e:
            print(f"Error: {e}")
            skipped.append((i, claim))
            continue

    with open(f"{log_dir}/{dir_name}_skipped.txt", "a") as f:
        for i, claim in skipped:
            f.write(f"{i}. {claim}\n")

if __name__ == "__main__":
    args = get_args()
    persuader = args.persuader
    persuader_path = args.persuader_path
    dir_name = args.dir_name
    log_dir = args.log_dir

    generate_arguments()