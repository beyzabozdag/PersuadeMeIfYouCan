PERSUADER = "Persuader"
PERSUADEE = "Listener" # make sure the model doesn't know it's trying to be persuaded (call this "listener" or something)
STRATEGY_REASONING_TAG = "strategy_reasoning"
RANKING_TAG = "support_ranking"
RANKING_TAG_INT = "support_ranking_int"
MESSAGE_TAG = "message"
OTHER_AGENT_MESSAGE_TAG = "other_agent_message"
REASONING_TAG = "reasoning" # later to be updated to only reason about which strategies to use. 
FINAL_DECISION_TAG = "final_decision"
SUPPORT = {
    "completely support": 5,
    "support": 4,
    "neutral": 3,
    "oppose": 2,
    "completely oppose": 1
}
