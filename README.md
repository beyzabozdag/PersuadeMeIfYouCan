# Overview
This repository is a modified version of the original [NegotiationArena](https://github.com/vinid/NegotiationArena/tree/main). The framework enables the generation of conversations between agents using the OpenAI API or compatible models.
# How to Generate Conversations
The agents in this framework rely on the OpenAI API. Any model that supports inference through the OpenAI API can be integrated seamlessly. Below, we demonstrate how to generate a conversation using Llama-3.1-8B-Instruct. 
## Step 1: Host the Model Locally
To host the model on your local machine, use the following command. By default, this will serve the model on port 8000:
```
vllm serve meta-llama/Llama-3.1-8B-Instruct
```
## Step 2: Configure the Runner Script
If you're running `runner/misalignment_game.py`, update the following settings in the script:
1. Specify the models to use:
```
model1 = "meta-llama/Llama-3.1-8B-Instruct"
model2 = "meta-llama/Llama-3.1-8B-Instruct"
```
2. Set the base URLs for the agents:
```
a1 = LLamaChatAgent(
        model= model1,
        agent_name=PERSUADER,
        base_url="http://localhost:8000/v1",
    )
a2 = LLamaChatAgent(
        model= model2,
        agent_name=PERSUADEE,
        base_url="http://localhost:8000/v1",
    )
```
## Step 3: Specify the Directory for Logs
Define the directory where all logs and `results.json` files will be saved:
```
dir_name = "directory_name"
```


