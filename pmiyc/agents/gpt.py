import copy
from openai import AzureOpenAI, OpenAI
import os
import random
from pmiyc.agents.agents import Agent
import time
from pmiyc.constants import PERSUADEE, PERSUADER
from copy import deepcopy
from pmiyc.constants import MESSAGE_TAG

class ChatGPTAgent(Agent):
    def __init__(
        self,
        agent_name: str,
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=400,
        seed=None,
    ):
        super().__init__(agent_name)
        self.run_epoch_time_ms = str(round(time.time() * 1000))
        self.model = model
        self.conversation = []
        self.prompt_entity_initializer = "system"
        self.seed = (
            int(self.run_epoch_time_ms) + random.randint(0, 2**16)
            if seed is None
            else seed
        )

        # print(f"Using model: {self.model}")
        api_version = "2024-02-15-preview" if "gpt-4o" in model.lower() else "2025-01-01-preview"
        # print(f"Using API version: {api_version}")
        
        # if "qwen" in self.model.lower():
        #     self.client = OpenAI(
        #         api_key=os.getenv("QWEN_KEY"),
        #     )

        self.client = AzureOpenAI( 
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY") if not self.model == "gpt-4o-IB" else os.getenv("IB_KEY"),
            api_version=api_version,
        )

        self.temperature = temperature
        self.max_tokens = max_tokens

    def __deepcopy__(self, memo):
        """
        Deepcopy is needed because we cannot pickle the llama object.
        :param memo:
        :return:
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "client" and not isinstance(v, str):
                v = v.__class__.__name__
            setattr(result, k, deepcopy(v, memo))
        return result
    
    def _chat_reasoning(self):
        chat = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
            #max_completion_tokens=self.max_tokens,  # no max tokens defined as it was causing issues with the API
            seed=self.seed,
        )
        return chat.choices[0].message.content
        

    def chat(self):
        if "gpt" not in self.model.lower():
            return self._chat_reasoning()
        
        chat = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            seed=self.seed,
        )
        
        return chat.choices[0].message.content

    def update_conversation_tracking(self, role, message):
        self.conversation.append({"role": role, "content": message})
