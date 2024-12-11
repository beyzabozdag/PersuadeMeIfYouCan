from openai import AzureOpenAI
import os
import random
from evaluator.prompt import evaluation_system_prompt, evaluation_user_prompt

def evaluate(claim, conversation):
    client = AzureOpenAI( 
            azure_endpoint = "https://uiuc-convai.openai.azure.com/",
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview"
        )
    
    system_prompt = evaluation_system_prompt()   
    user_prompt = evaluation_user_prompt(claim, conversation)

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    for prompt in messages:
        print(prompt["role"]) 
        print(prompt["content"])
        

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
		max_tokens=4096,
		top_p=0.95,
		frequency_penalty=0,
		presence_penalty=0,
		stop=None
    )
    
    return parse_evaluation_output(completion.choices[0].message.content)

def parse_evaluation_output(output):

    # The expected output is in the format:
    # Persuasion Success: <1 if successful, 0 if not>
    # Turn of Acceptance: <Turn Number, if Persuasion Success is True, else -1>

    output = output.split("\n")
    try: 
        persuasion_success = int(output[0].split(": ")[1])
        turn_of_acceptance = int(output[1].split(": ")[1])
    except:
        raise Exception(f"Could not parse the output of the evaluation system: {output}")
    
    if persuasion_success not in [0, 1]:
        raise Exception(f"Persuasion Success should be either 0 or 1, but got {persuasion_success}")
    
    if persuasion_success == 1 and turn_of_acceptance == -1:
        raise Exception(f"Persuasion Success is True, but Turn of Acceptance is -1")
    
    if persuasion_success == 0 and turn_of_acceptance != -1:
        raise Exception(f"Persuasion Success is False, but Turn of Acceptance is not -1")

    return persuasion_success, turn_of_acceptance

    
