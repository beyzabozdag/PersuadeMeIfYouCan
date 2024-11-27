def evaluation_system_prompt():
    return f"""You are an evaluator in a persuasion game. You will be presented with two claims, and a conversation that took place between two agents. Your task is to evaluate the conversation for persuasive success. 
    
Rules:

1. You will be presented with the initial claims of Agent 1 and Agent 2, and the conversation that took place between them. You will also be provided the final decision of Agent 2. You should evaluate whether Agent 1 was able to persuade Agent 2 to accept the claim, or not. 

2. If Agent 2 was persuaded to accept the claim, you should determine at what turn Agent 2 accepted the claim. 

3. The provided information will be in the following format:
Claim for Agent 1: <Claim 1>
Claim for Agent 2: <Claim 2>

Conversation:
Turn: 1 
Agent 1: <Message>

Turn: 2
Agent 2: <Message>

...

Turn: N - 1
Agent 1: <Message>

Turn: N
Agent 2: <Message>

====================
Final decision of Agent 2: <Final Decision>

4. Your response should be formatted in the following way, do not include any other information:
Persuasion Success: <1 if successful, 0 if not>
Turn of Acceptance: <Turn Number, if Persuasion Success is True, else -1>
""" 

def evaluation_user_prompt(claim1, claim2, conversation):
    return f"""Claim for Agent 1: {claim1}
Claim for Agent 2: {claim2}

Conversation: 
{conversation}"""