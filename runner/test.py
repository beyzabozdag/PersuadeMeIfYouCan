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
from persuasion_arena.constants import *
from datasets import load_dataset

import random
from datasets import load_dataset
from datasets.utils.logging import set_verbosity_error, disable_progress_bar

from persuasion_arena.utils import get_tag_contents

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
    
    test_agent = ClaudeAgent(agent_name="Persuader")

    test_agent.init_agent("You're an helpful AI assistant. Answer the user's requests. Always end your messages with a :)")
    print(test_agent.step("What is the capital of France?"))

if __name__ == "__main__":

    main()
    
