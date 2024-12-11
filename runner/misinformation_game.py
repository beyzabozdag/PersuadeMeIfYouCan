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
from persuasion_arena.constants import *
from datasets import load_dataset


load_dotenv("../.env.local")

@retry(stop=stop_after_attempt(5))
def process_truthful_qa_elem(model1, model2, elem):
    question = elem["question"]

    correct_answer = None
    choices,labels = elem["mc1_targets"]["choices"],elem["mc1_targets"]["labels"]
    for i,label in enumerate(labels):
        if label == 1: 
            correct_answer = choices[i]
            break
    
    incorrect_answers = []
    choices,labels = elem["mc1_targets"]["choices"],elem["mc1_targets"]["labels"]
    for i,label in enumerate(labels):
        if label == 0: incorrect_answers.append(choices[i])


    persuader_claim = correct_answer
    persuadee_claim = random.choice(incorrect_answers)

    a1 = LLamaChatAgent(
        model=model1,
        agent_name=PERSUADER,
        base_url="http://localhost:8000/v1"
    )
    a2 = LLamaChatAgent(
        model=model2,
        agent_name=PERSUADEE,
        base_url="http://localhost:8000/v1"
    )

    c = PersuasionGame(
        players=[a1, a2],
        iterations=5,
        player_roles=["Start persuading!", ""],
        question=question,
        claims=[persuader_claim, persuadee_claim],
        log_dir=f"./.logs/persuasion_game/truthful_qa/{model1}_vs_{model2}",
    )

    c.run()

def run_truthful_qa(model1, model2):
    ds = load_dataset("truthfulqa/truthful_qa", "multiple_choice")["validation"]

    agree,disagree = 0,0
    for elem in ds:
        final_response = process_truthful_qa_elem(model1, model2, elem)

        if "DISAGREE" in final_response: disagree += 1
        elif "AGREE" in final_response: agree += 1

        if agree+disagree > 10: break #TODO

    print(f"Total agree = {agree}\nTotal disagree = {disagree}")


if __name__ == "__main__":
    model1 = "meta-llama/Llama-3.1-8B-Instruct"
    model2 = "meta-llama/Llama-3.1-8B-Instruct"
    run_truthful_qa(model1, model2)

# vllm serve meta-llama/Llama-3.1-8B-Instruct --port 8000
# vllm serve meta-llama/Llama-2.7B-Instruct --port 8001