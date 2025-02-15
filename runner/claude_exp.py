
import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
from persuasion_arena.agents import *
from persuasion_arena.constants import *
from games.new_game.prompt import persuadee_final_decision_prompt
from persuasion_arena.utils import get_response_str
from runner.run_new_game import get_claims
from datasets import load_dataset

# import pretty print
from pprint import pprint


def get_claude_args():
    dataset = load_dataset("Anthropic/persuasion", split="train")

    arg_data = {}

    for item in dataset:
        source = item["source"]
        prompt_type = item["prompt_type"]
        claim = item["claim"]
        argument = item["argument"]

        if source not in arg_data:
            arg_data[source] = {}

        if claim not in arg_data[source]:
            arg_data[source][claim] = {}

        arg_data[source][claim][prompt_type] = argument

    return arg_data

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True)
    parser.add_argument("--er", type=str, required=True)
    parser.add_argument("--ee", type=str, required=True)
    parser.add_argument("--ee_path", type=str, required=True) 
    parser.add_argument("--log_dir", type=str, required=True)
    parser.add_argument("--dir_name", type=str, required=True)
    return parser.parse_args()

def get_agent():
    print("\n\n", "-"*50)

    if "gpt" in EE.lower():
        print("Using ChatGPTAgent for model1")
        agent = ChatGPTAgent(
            model=EE,
            agent_name=PERSUADEE
        )
    elif "claude" in EE.lower():
        print("Using ClaudeAgent for model1")
        agent = ClaudeAgent(
            model=EE,
            agent_name=PERSUADEE
        )
    else:
        print("Using LLamaChatAgent for model1")
        agent = LLamaChatAgent(
            model=EE,
            agent_name=PERSUADEE,
            base_url=EE_path,
        )

    return agent

def replace_persuader_message(replacement):
    return f"<{OTHER_AGENT_MESSAGE_TAG}> {replacement} </{OTHER_AGENT_MESSAGE_TAG}>"

def gen_new_response(a2, argument, res):
    
    try: 
        ### GET & UPDATE CONVERSATION HISTORY ###
        # prep conversation history
        assert res["conversation"]["2"]["turn"] == 1 # make sure the persuadee is the second agent

        conversation_history = res["conversation"]["2"]["agent_history"][:-1]
        # edit the last user message to ask the final decision prompt

        last_user_message = replace_persuader_message(argument) + " " + persuadee_final_decision_prompt(res["claim"])

        # update the conversation history
        conversation_history[-1]["content"] = last_user_message

        ### GET FINAL RESPONSE ###
        # update the agent's conversation history
        a2.resume_conversation(conversation_history)    
        # get the persuadee's final response
        response = a2.step(None, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=True)
        
        print(response)

        ### WRITE RESULTS ###
        updated_conversation = {"0": res["conversation"]["0"], "1": {}, "2": res["conversation"]["2"]}

        updated_conversation["2"]["response"] = response
        updated_conversation["2"]["agent_history"][-1]["content"] = get_response_str(response, visible_ranks=True)

    except Exception as e:
        print("Exception occurred")
        print(e)
        skipped.append((res["i"], res["claim"]))
        return None
    
    return updated_conversation


def main():
    file_to_copy_from =  f"{dir}/{copy_from}/results.json"
    file_to_write = f"{log_dir}/{dir_name}/results.json"
    new_results = []

    claims = get_claims(anthropic_only=True)
    # get claude args
    claude_args = get_claude_args()[source]

    with open(file_to_copy_from, "r") as f:
        results = json.load(f)
        for res in results:
            assert res["model2"] == EE
            if res["claim"] not in claims:
                continue
            
            print()
            print(res["i"], res["claim"])
            claims_args = claude_args[res["claim"]]

            for prompt_type in claims_args:
                argument = claims_args[prompt_type]
                print(f"Prompt Type: {prompt_type}")
                a2 = get_agent()
                updated_conversation = gen_new_response(a2, argument, res)

                if updated_conversation:
                    data = {
                        "i": res["i"],
                        "model1": ER,
                        "model2": res["model2"],
                        "claim": res["claim"],
                        "prompt_type": prompt_type,
                        "conversation":updated_conversation
                    }

                    new_results.append(data)

                    with open(file_to_write, "w") as f:
                        json.dump(new_results, f, indent=4)      

    with open(file_to_write, "w") as f:
        json.dump(new_results, f, indent=4) 

    with open(f"{log_dir}/{dir_name}/skipped_claims.txt", "w") as f:
        for claim in skipped:
            f.write(f"{claim}\n")

if __name__ == "__main__":

    skipped = []
    dir = "/shared/storage-01/users/nbozdag2/multi_turn/vr_4t_i"
    new_dir = "/shared/storage-01/users/nbozdag2/multi_turn/claude_only"
    args = get_args()
    source = args.source
    ER = args.er
    EE = args.ee
    EE_path = args.ee_path
    log_dir = args.log_dir
    dir_name = args.dir_name
    copy_from = f"gpt4omini_{dir_name.split('_')[1]}"

    if not os.path.exists(f"{log_dir}/{dir_name}"):
        os.makedirs(f"{log_dir}/{dir_name}")

    main()
