Okay, let's simplify the structure and create the README for the Human vs. LLM Pygame version first.

**Simplified Structure Proposal:**

We can combine the UI management directly into the main script (`main_pygame.py`) for simplicity, while keeping the game state logic separate in `game_manager.py`.

```
.
├── logs/                 # Directory for all output files
│   ├── llm_interactions.log # LLM prompt/response log for the last run
│   └── game_data_*.csv    # CSV data log for analysis (timestamped)
├── config.py           # Configuration (LLM settings, game rules, UI constants)
├── llm_player.py       # Defines the LLMPlayer class (AI opponent logic)
├── game_manager.py     # Manages game state (scores, history), scoring logic
├── main_pygame.py      # Main script: Initializes Pygame, UI, GameManager, runs game loop
├── .env                # Stores sensitive API keys (!!! DO NOT COMMIT THIS FILE !!!)
├── .gitignore          # Specifies intentionally untracked files (logs/, .env, venv/)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

**Key Simplifications:**

*   No separate `ui_manager.py`. All Pygame initialization, event handling, and drawing logic will reside within `main_pygame.py`.
*   `game_manager.py` focuses purely on game state (scores, history), rules (scoring), and interacting with the `LLMPlayer`. It doesn't run the main loop.
*   `main_pygame.py` drives the game, handles user input via Pygame, calls the `GameManager` to update state and get the LLM's move, and renders the UI.

---

**README.md Content:**

```markdown
# Human vs LLM Iterated Game with Pygame UI

## Overview

This project pits a human player against a Large Language Model (LLM) agent (e.g., GPT-4, Claude, Gemini) in a multi-round strategic number game, using a graphical interface built with Pygame. The goal for both the human and the LLM is to maximize their own score over a series of rounds. The game mechanics encourage predicting the opponent's next move, creating a dynamic competitive environment that tests the LLM's strategic reasoning against a human opponent.

The core game is a variation of common iterated games: players choose a number from a small set, and receive a bonus if their choice correctly anticipates the opponent's choice according to a specific rule (Your Choice = Opponent's Choice - 1).

## Game Rules

1.  **Players:** One Human player (using the Pygame interface) and one LLM agent.
2.  **Choices:** In each round, both players simultaneously choose an integer from a predefined set (default: 1, 2, 3, 4, 5). The human selects via buttons, the LLM generates its choice.
3.  **Scoring:**
    *   A player choosing number `N` receives `N` points as a base score for the round.
    *   **Bonus:** If the Human chooses `N_h` and the LLM chooses `N_llm`, and if `N_h == N_llm - 1`, the Human gets an additional `BONUS_POINTS` (default: 10) for that round.
    *   Similarly, if `N_llm == N_h - 1`, the LLM gets the `BONUS_POINTS`.
    *   Note: Choosing `N=1` means the opponent cannot get a bonus by choosing `0`, as `0` is not a valid choice.
4.  **Objective:** Maximize the total score accumulated over `NUM_ROUNDS` (default: 60).
5.  **Information:**
    *   The Human sees the current scores, round number, and the **result of the last round** on the Pygame screen.
    *   The LLM receives the game rules, its current score, the human's current score, the current round number, and the **full conversation history** (including all past round results and its own previous choices/analyses) before making its choice.

## Features

*   **Pygame Interface:** Simple graphical UI for human interaction (viewing scores, history, choosing numbers).
*   **Human vs. AI Gameplay:** Directly compete against a configured LLM.
*   **Configurable LLM Opponent:** Set the LLM model (e.g., GPT-4o, Claude 3 Sonnet) and temperature via `config.py`.
*   **Configurable Game:** Adjust the number of rounds, available choices, and bonus points in `config.py`.
*   **Real-time Feedback:** UI updates instantly with scores and round results.
*   **Last Round Display:** Shows the choices and score changes from the previous round in the UI.
*   **Logging:** Saves detailed LLM prompts/responses (`logs/llm_interactions.log`) and structured game data (`logs/game_data_*.csv`) in a dedicated `logs/` directory.

## Project Structure

```
.
├── logs/                 # Directory for all output files
│   ├── llm_interactions.log # LLM prompt/response log for the last run
│   └── game_data_*.csv    # CSV data log for analysis (timestamped)
├── config.py           # Configuration (LLM settings, game rules, UI constants)
├── llm_player.py       # Defines the LLMPlayer class (AI opponent logic)
├── game_manager.py     # Manages game state (scores, history), scoring logic
├── main_pygame.py      # Main script: Initializes Pygame, UI, GameManager, runs game loop
├── .env                # Stores sensitive API keys (!!! DO NOT COMMIT THIS FILE !!!)
├── .gitignore          # Specifies intentionally untracked files (logs/, .env, venv/)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

*\*API Keys should be stored in the `.env` file, not directly in `config.py`.*

## Getting Started

### Prerequisites

*   Python 3.8+
*   Pygame (`pip install pygame`)
*   Access to an LLM API (e.g., OpenAI, Anthropic via OpenRouter) and a corresponding API key.

### Installation

1.  **Clone or download the repository:**
    ```bash
    git clone <your-repo-url> # Or download the ZIP file
    cd <repository-directory>
    ```

2.  **(Recommended) Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install required packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This will install `pygame`, `openai` (or the specific LLM client), and `python-dotenv`.*

### Configuration

1.  **Set up API Key:**
    *   Create a file named `.env` in the project's root directory.
    *   Add your LLM API key to this file. Example for OpenRouter:
        ```dotenv
        # .env file
        LLM_API_KEY="sk-or-v1-..."
        ```
    *   **Important:** Ensure `.env` and `logs/` are listed in your `.gitignore` file.

2.  **Configure LLM, Game, and UI Settings:**
    *   Open `config.py`.
    *   Set `LLM_MODEL` to the specific model identifier you want the AI opponent to use (e.g., `"openai/gpt-4o"`, `"anthropic/claude-3-sonnet"`).
    *   Adjust `LLM_TEMPERATURE` if desired (controls LLM response randomness).
    *   Modify `NUM_ROUNDS`, `CHOICES`, `BONUS_POINTS` for the game rules.
    *   (Optional) Adjust UI constants like colors, screen size, font sizes if defined in `config.py`.

## Running the Game

Execute the main Pygame script from the project's root directory:

```bash
python main_pygame.py
```

This will launch the Pygame window where you can play the game.

## Output

*   **Pygame Window:** The main interface showing:
    *   Current round number.
    *   Human and LLM scores.
    *   Buttons for the human player to choose a number (1-5).
    *   A display area for the **previous round's result** (choices, score changes).
    *   Status messages (e.g., "Your Turn", "Waiting for LLM...", "Game Over").
*   **`logs/llm_interactions.log`:** Detailed log of system prompt, user prompts (last round results), and LLM responses for the most recent game run.
*   **`logs/game_data_*.csv`:** CSV file containing structured data for each round (human choice, LLM choice, scores, timestamp) for later analysis. Saved in the `logs/` directory.

## Customization

*   **Change LLM:** Modify `config.py` and potentially `llm_player.py` if using a different API provider structure.
*   **Modify Game Rules:** Adjust scoring or choices in `config.py` and update the logic in `game_manager.py`.
*   **Enhance UI:** Modify drawing functions and event handling in `main_pygame.py` to change appearance or add features.
*   **Tune LLM Prompt:** Experiment with the system prompt or the format of the round result prompt in `llm_player.py` to influence the AI's strategy and adherence to the expected output format (1-sentence analysis + "My choice is: [number]").

## License

(Optional: Add license information here, e.g., MIT License)
```

---

This README reflects the simplified structure and the Human vs. LLM gameplay using Pygame. Let me know when you're ready to start adapting the Python code based on this plan!