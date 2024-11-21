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


if __name__ == "__main__":
    a1 = ChatGPTAgent(
        model="gpt-4o-mini",
        agent_name=PERSUADER,
    )
    a2 = ChatGPTAgent(
        model="gpt-4o-mini",
        agent_name=PERSUADEE,
    )

    c = PersuasionGame(
        players=[a1, a2],
        iterations=6,
        player_roles=[
            "Start persuading!",
            "",
        ], # no specific roles
        log_dir="./.logs/persuasion_game/",
    )

    c.run()