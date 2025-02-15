import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from pmiyc.agents import LLamaChatAgent, ChatGPTAgent, ClaudeAgent
from pmiyc.constants import PERSUADEE, RANKING_TAG
from prompt import pre_asess_system_prompt
from datasets import load_dataset
from tenacity import retry, stop_after_attempt, wait_fixed
import regex as re
from pmiyc.utils import support_to_int
from runner.run_subj_game import get_claims
import pandas as pd



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", type=str)
    parser.add_argument("iteration", type=int)
    parser.add_argument("output_file", type=str)
    parser.add_argument("url", type=str, nargs='?', default="http://localhost:8000/v1")
    return parser.parse_args()

def get_agent():
    if "gpt" in model_name.lower():
        print("Using ChatGPTAgent for model2")
        a2 = ChatGPTAgent(
            model=model_name,
            agent_name=PERSUADEE
        )
    elif "claude" in model_name.lower():
        print("Using ClaudeAgent for model2")
        a2 = ClaudeAgent(
            model=model_name,
            agent_name=PERSUADEE
        )
    else:
        print("Using LLamaChatAgent for model2")
        a2 = LLamaChatAgent(
            model=model_name,
            agent_name=PERSUADEE,
            base_url=model_path
        )

    return a2

def main():
    # print all the arugments
    print(f"model_name: {model_name}")
    print(f"iteration: {iteration}")
    print(f"output_file: {output_file}")
    print(f"url: {model_path}")

    results = []

    # load the output file
    if os.path.exists(f"results/{output_file}.csv"):
        df = pd.read_csv(f"results/{output_file}.csv")
        results = df.to_dict("records")

    for i, claim in enumerate(get_claims()):
        
        if any([claim == result["claim"] for result in results]):
            print("Already processed")
            continue

        print(f"{i}: {claim}")
        scores = []
        for j in range(iteration):
            attempt = 0
            while attempt < 3:
                agent = get_agent()
                agent.init_agent(system_prompt=pre_asess_system_prompt())
                
                message = f"Claim: {claim}\nYour response: "
                try:
                    response = agent.step(message)
                except Exception as e:
                    print(f"Error: {e}")
                    response = None
                
                print(f"Response: {response}")
                
                if response:
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

    args = get_args()
    model_name = args.model_name
    iteration = args.iteration
    output_file = args.output_file
    model_path = args.url

    main()