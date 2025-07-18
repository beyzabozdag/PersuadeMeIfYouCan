# Persuade Me If You Can (PMIYC)
[![Arxiv](https://img.shields.io/badge/arXiv-PMIYC-b31b1b)](https://arxiv.org/abs/2503.01829) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Abstract
Large Language Models (LLMs) demonstrate persuasive capabilities that rival human-level persuasion. While these capabilities can be used for social good, they also present risks of potential misuse. Moreover, LLMs' susceptibility to persuasion raises concerns about alignment with ethical principles. To study these dynamics, we introduce **Persuade Me If You Can (PMIYC)**, **an automated framework for evaluating persuasion through multi-agent interactions**. Here, _Persuader_ agents engage in multi-turn conversations with the _Persuadee_ agents, allowing us to measure LLMs' persuasive effectiveness and their susceptibility to persuasion. We conduct comprehensive evaluations across diverse LLMs, ensuring each model is assessed against others in both subjective and misinformation contexts. We validate the efficacy of our framework through human evaluations and show alignment with prior work. PMIYC offers a scalable alternative to human annotation for studying persuasion in LLMs. Through PMIYC, we find that Llama-3.3-70B and GPT-4o exhibit similar persuasive effectiveness, outperforming Claude 3 Haiku by 30\%. However, GPT-4o demonstrates over 50\% greater resistance to persuasion for misinformation compared to Llama-3.3-70B. These findings provide empirical insights into the persuasive dynamics of LLMs and contribute to the development of safer AI systems.[^1]

[^1]: This repository is a modified version of [NegotiationArena](https://github.com/vinid/NegotiationArena/tree/main). 

## Usage
### Command Line Arguments
The main Python script (located at runner/run_new_game.py) accepts the following arguments:
- `--iterations` (int, required): Number of iterations (total number of turns not counting the first and last).
- `--model1` (str, required): Model name of the first agent (e.g., the persuader).
- `--model2` (str, required): Model name of the second agent (e.g., the persuadee).
- `--model1_path` (str, required): Model path of the first agent.
- `--model2_path` (str, required): Model path of the second agent.
- `--log_dir` (str, default: ./.logs): Directory for logs/results.
- `--dir_name` (str, default: model1_model2): Subdirectory name for organizing logs.
- `--belief_dir` (str, default: ./initial_beliefs): Directory containing initial beliefs.
- `--end_game`: Flag to enable end-game conditions.
- `--visible_ranks`: Flag to make ranks visible.
- `--test`: Flag to run in test mode.
### Example Script
```bash
#!/bin/bash

# Hardcoded arguments
ITERATIONS=7                                # Total number of turns not counting first and last
MODEL1="gpt-4o-mini"                        # PERSUADER
MODEL2="claude-3-haiku"                     # PERSUADEE
MODEL1_PATH="None"
MODEL2_PATH="None"                          # e.g., "http://0.0.0.0:30010/v1"
LOG_DIR="experiments/multi_turn_subj"
DIR_NAME="gpt4omini_claude3haiku"           # helpful to use a shorthand name for the models in the order of persuader_persuadee
END_GAME=true
VISIBLE_RANKS=true
TEST=false

# Construct the command
CMD="python3 runner/run_subj_game.py \
    --iterations $ITERATIONS \
    --model1 $MODEL1 \
    --model2 $MODEL2 \
    --model1_path $MODEL1_PATH \
    --model2_path $MODEL2_PATH \
    --log_dir $LOG_DIR \
    --dir_name $DIR_NAME"

# Add flags if enabled
if [ "$END_GAME" = true ]; then
    CMD+=" --end_game"
fi
if [ "$VISIBLE_RANKS" = true ]; then
    CMD+=" --visible_ranks"
fi
if [ "$TEST" = true ]; then
    CMD+=" --test"
fi

# Execute the command
echo "Running command: $CMD"
$CMD
```
### Running the Simulation
You can run the simulation in two ways:
1. Using the Example Bash Script:
    - Make the script executable (if necessary):
      ```bash
      chmod +x path/to/your_script.sh
      ```
    - Execute the script:
      ```bash
      ./path/to/your_script.sh
      ```
2. Directly via Command Line:
   ```bash
   python3 runner/run_subj_game.py --iterations 7 --model1 "gpt-4o-mini" --model2 "claude-3-haiku" --model1_path "None" --model2_path "None" --log_dir "experiments/multi_turn_subj" --dir_name "gpt4omini_claude3haiku" --end_game --visible_ranks
   ```
### Running Evaluation
The below script will evaluate all conversations under the misinformation directory. For subjective conversations, simply remove the `--misinfo` flag.
```
RESULTS_DIR="./results/misinformation"
RESULTS_CSV="./results/misinformation/misinformation_results.csv"
ANALYSIS_RESULTS="./results/misinformation/misinformation_results.json"
BELIEF_DIR="./initial_beliefs/initial_beliefs_misinfo"
PERSUADEE_TURN_COUNT=5

CMD="python3 evaluation/evaluate.py     --results_dir $RESULTS_DIR     --results_csv $RESULTS_CSV     --analysis_results $ANALYSIS_RESULTS     --belief_dir $BELIEF_DIR     --persuadee_turn_count $PERSUADEE_TURN_COUNT    --misinfo"

# Execute the command
echo "Running command: $CMD"
$CMD  
```
The above script will generate a CSV file with the results of the evaluation, as well as a JSON file with detailed analysis results. The final json file will contain aggregated results for each model pair of persuader and persuadee. For example: 
```json
{
    "pair": "meta-llama/Meta-Llama-3.1-8B-Instruct, claude-3-haiku-20240307",
    "persuader": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "persuadee": "claude-3-haiku-20240307",
    "total_conversations": 938,
    "skipped_conversations": 0,
    "average_initial_ranking": 2.964,
    "average_final_ranking": 4.41,
    "average_absolute_change": 1.447,
    "average_normalized_change": 0.772,
    "avg_nc_by_persuader": {
        "support": [
            0.861,
            379
        ],
        "oppose": [
            0.642,
            351
        ],
        "neutral": [
            0.831,
            208
        ]
    },
    "persuader_none_score": 1,
    "persuadee_none_score": 0,
    "initial_ranking_breakdown": {
        "1": 53,
        "2": 241,
        "3": 347,
        "4": 281,
        "5": 16
    },
    "final_ranking_breakdown": {
        "1": 15,
        "2": 83,
        "3": 18,
        "4": 208,
        "5": 614
    }
},
```

### Environment Setup
We have provided both the environment.yml and requirements.txt files for setting up the environment. You can use either of them based on your preference.
- **Using conda**:
  ```bash
  conda env create -f environment.yml
  conda activate persuasion
    ```
- **Using pip**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate 
    pip install -r requirements.txt
    ```
