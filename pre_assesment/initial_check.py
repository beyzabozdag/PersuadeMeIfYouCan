import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from persuasion_arena.agents import LLamaChatAgent
from persuasion_arena.constants import PERSUADEE
from prompt import pre_asess_system_prompt
from datasets import load_dataset
from tenacity import retry, stop_after_attempt, wait_fixed
import regex as re
from persuasion_arena.utils import support_to_int

import pandas as pd




def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", type=str)
    parser.add_argument("iteration", type=int)
    parser.add_argument("output_file", type=str)
    parser.add_argument("url", type=str, nargs='?', default="http://localhost:8000/v1")
    return parser.parse_args()

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_claims():
    dataset = load_dataset("Anthropic/persuasion", split="train")
    # get all claims from the dataset
    unique_claims = set([item["claim"] for item in dataset])

    # add claims from "subjective_claims.csv"
    subjective_claims = pd.read_csv("./subjective_claims.csv")
    subj = set()
    for claim in subjective_claims["Claim"]:
        subj.add(claim)
    
    retval = sorted(list(unique_claims)) + sorted(list(subj))

    return retval

def main():

    args = get_args()
    model_name = args.model_name
    iteration = args.iteration
    output_file = args.output_file
    url = args.url

    # print all the arugments
    print(f"model_name: {model_name}")
    print(f"iteration: {iteration}")
    print(f"output_file: {output_file}")
    print(f"url: {url}")

    agent = LLamaChatAgent(
        model=model_name,
        agent_name=PERSUADEE,
        base_url=url,
        temperature=0.1,
    )

    agent.init_agent(
        system_prompt=pre_asess_system_prompt(),
        role="", # no role needed for pre-assessment
    )

    results = []

    for i, claim in enumerate(get_claims()):
        print(f"{i}: {claim}")
        scores = []
        for j in range(iteration):
            attempt = 0
            while attempt < 3:
                message = f"Claim: {claim}\nYour response: "
                response = agent.step(message)
                agent.reset(full_reset=True) # reset the agent after each prompt
                int_response = support_to_int(response)
                if int_response is not None:
                    scores.append(int_response)
                    break
                attempt += 1

        if len(scores) > 0:
            avg = sum(scores) / len(scores)
            standard_deviation = round(sum([(score - avg) ** 2 for score in scores]) / len(scores), 2)
            print(f"Scores: {scores}") 
            print(f"Average: {avg}")
            print(f"Standard Deviation: {standard_deviation}")
            print(f"Skipped: {iteration - len(scores)}")
        else:
            avg = 0
            print("No valid responses")
        
        results.append({"i": i, "claim": claim, "scores": scores, "average": avg, "std_dev": standard_deviation, "skipped": iteration - len(scores)})
        
        print("")

        if i % 10 == 0:
            df = pd.DataFrame(results)
            df.to_csv(f"results/{output_file}.csv", index=False)

    df = pd.DataFrame(results)
    df.to_csv(f"results/{output_file}.csv", index=False)



    

if __name__ == "__main__":
    main()