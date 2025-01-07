"""
this game will regenerate the final response of the persuadee given the persuadee's initial decision, 
the conversation history, and the final decision prompt. 
"""
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

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model1", type=str, required=True)
    parser.add_argument("--model2", type=str, required=True)
    parser.add_argument("--model2_path", type=str, required=True)
    parser.add_argument("--dir_name", type=str, required=True)
    parser.add_argument("--log_dir", type=str, required=True)
    parser.add_argument("--replace", action="store_true", help="Replaces the persuader's message with the uninformed version")
    return parser.parse_args()

def get_agent():
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

    return a2

def replace_persuader_message(claim):
    # find replacement message
    with open(f"{replacement_dir}/{dir_name.split("_")[0]}.json", "r") as f:
        data = json.load(f)
        replacement = data[model1][claim]["message"]

    return f"<{OTHER_AGENT_MESSAGE_TAG}> {replacement} </{OTHER_AGENT_MESSAGE_TAG}>"

def gen_final_res():
    
    results_file = f"{dir}/{dir_name}/results.json"
    new_results_file = f"{log_dir}/{dir_name}/results.json"
    new_results = []
    skipped = []

    with open(results_file, "r") as f:
        results = json.load(f)
        for res in results:
            print()
            print(res["i"], res["claim"])
            a2 = get_agent()

            try: 
                ### GET & UPDATE CONVERSATION HISTORY ###
                # prep conversation history
                assert res["conversation"]["2"]["turn"] == 1 # make sure the persuadee is the second agent
                conversation_history = res["conversation"]["2"]["agent_history"][:-1]
                # edit the last user message to ask the final decision prompt
                last_user_message = conversation_history[-1]["content"]

                if replace:
                    last_user_message = replace_persuader_message(res["claim"]) + " " + persuadee_final_decision_prompt(res["claim"])

                else:
                    # split from the "Reminder: " part, and add the final decision prompt
                    last_user_message = last_user_message.split("Reminder: ")[0] + " " + persuadee_final_decision_prompt(res["claim"])
                
                # update the conversation history
                conversation_history[-1]["content"] = last_user_message

                ### GET FINAL RESPONSE ###
                # update the agent's conversation history
                a2.resume_conversation(conversation_history)    
                # get the persuadee's final response
                response = a2.step(None, expected_keys=[MESSAGE_TAG, RANKING_TAG], visible_ranks=True)
                
                print(response)

                ### WRITE RESULTS ###
                updated_conversation = {"0": res["conversation"]["0"], "1": res["conversation"]["1"], "2": res["conversation"]["2"]}

                updated_conversation["2"]["response"] = response
                updated_conversation["2"]["agent_history"][-1]["content"] = get_response_str(response, visible_ranks=True)

            except Exception as e:
                print(e)
                skipped.append((res["i"], res["claim"]))
                continue

            data = {
                "i": res["i"],
                "model1": res["model1"],
                "model2": res["model2"],
                "claim": res["claim"],
                "conversation": updated_conversation
            }

            new_results.append(data)

            with open(new_results_file, "w") as f:
                json.dump(new_results, f, indent=4)

    with open(new_results_file, "w") as f:
        json.dump(new_results, f, indent=4) 

    with open(f"{log_dir}/{dir_name}/skipped_claims.txt", "w") as f:
        for claim in skipped:
            f.write(f"{claim}\n")


if __name__ == "__main__":
    dir = "/shared/storage-01/users/nbozdag2/multi_turn/vr_4t_i"
    replacement_dir = "/shared/storage-01/users/nbozdag2/uninformed_args"
    args = get_args()
    model1 = args.model1
    model2 = args.model2
    model2_path = args.model2_path
    dir_name = args.dir_name
    log_dir = args.log_dir
    replace = args.replace

    if not os.path.exists(f"{log_dir}/{dir_name}"):
        os.makedirs(f"{log_dir}/{dir_name}")

    gen_final_res()