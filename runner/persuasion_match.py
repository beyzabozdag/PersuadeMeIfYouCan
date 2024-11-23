import os
import sys
# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
from dotenv import load_dotenv
import inspect
from persuasion_arena.agents import *
from games.game import PersuasionGame
from persuasion_arena.constants import *

load_dotenv("../.env.local")

model1 = "gpt-4o-mini"
model2 = "gpt-4o-mini"

if __name__ == "__main__":
    a1 = ChatGPTAgent(
        model=model1,
        agent_name=PERSUADER,
    )
    a2 = ChatGPTAgent(
        model=model2,
        agent_name=PERSUADEE,
    )

    c = PersuasionGame(
        players=[a1, a2],
        iterations=8,
        player_roles=[
            "Start persuading!",
            "",
        ],
        log_dir=f"./.logs/persuasion_game/{model1}_vs_{model2}",
    )

    c.run()