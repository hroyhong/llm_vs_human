import os
import logging
import json
import re # Added
import random # Added
from openai import OpenAI
import config  # Import our configuration

# --- Logging Setup ---

# Root logger configuration (handles console output)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()] # Only console output for root logger
)

# Interaction logger (logs prompts/responses to file)
interaction_logger = logging.getLogger("InteractionLogger")
interaction_logger.setLevel(logging.INFO) # Log info level and above
interaction_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
interaction_handler = logging.FileHandler(config.LLM_INTERACTION_LOG_FILE, mode='w')
interaction_handler.setFormatter(interaction_formatter)
interaction_logger.addHandler(interaction_handler)
interaction_logger.propagate = False # Don't send interaction logs to root/console

# Use the interaction logger for general player logging
logger = interaction_logger
logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO)) # Use level from config

class LLMPlayer:
    """Handles interaction with the LLM via OpenRouter, maintaining conversation history."""

    def __init__(self):
        """Initializes the LLM player with conversation history."""
        if not config.LLM_API_KEY:
            raise ValueError("LLM_API_KEY not found in config. Please check .env file.")

        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.LLM_API_KEY,
            # Add required headers for OpenRouter if needed (sometimes helps)
             default_headers={
                 "HTTP-Referer": "http://localhost", # Placeholder, replace if you have a specific URL
                 "X-Title": "LLM vs Human Game" # Placeholder title
             }
        )
        self.model = config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.name = f"LLM ({self.model.split('/')[-1]})" # Simple name

        # Store system prompt separately
        self.system_prompt = f"""You are {self.name} in a {config.NUM_ROUNDS}-round game.

Game Rules:
- Choose a number between {config.MIN_CHOICE} and {config.MAX_CHOICE}
- Your base score each round is the number you choose
- BONUS RULE: YOU get +{config.BONUS_POINTS} points when YOUR_CHOICE = OPPONENT_CHOICE - 1
- If opponent chooses {config.MIN_CHOICE}, you cannot get bonus by choosing {config.MIN_CHOICE - 1}
- Maximize your total score over {config.NUM_ROUNDS} rounds

Memory Instructions:
- Take into account the history of all previous rounds (provided in the conversation) when making your choice to maximize your total score

Output Format:
- Analyze the game situation in 1 sentence. Use the analysis to inform your choice.
- End with "My choice is: [number]" where [number] is between {config.MIN_CHOICE} and {config.MAX_CHOICE}"""

        # Stores user/assistant message dictionaries
        self.conversation_history = []
        self.first_round = True

        logger.info(f"LLMPlayer initialized: {self.name}, Temp: {self.temperature}")
        logger.debug(f"System Prompt:\n{self.system_prompt}") # Log system prompt to main log if DEBUG


    def _format_round_prompt(self, game_state) -> str:
        """Formats the user prompt string for the current round."""
        current_round = game_state['round']
        llm_score = game_state['llm_score']
        human_score = game_state['human_score']
        history = game_state['history'] # Full history from GameManager

        if self.first_round:
            prompt = f"Round {current_round}/{config.NUM_ROUNDS}\n"
            prompt += f"Current scores - You: {llm_score}, Opponent: {human_score}\n\n"
            prompt += "This is the first round. What is your choice?"
            self.first_round = False
            return prompt

        # Subsequent rounds: Format based on the *last* round's results
        if not history: # Should not happen after first round, but safety check
             return "What is your choice for this round?"

        last_round_data = history[-1]
        round_num, human_choice, llm_choice, human_score_change, llm_score_change = last_round_data

        prompt = f"Round {current_round}/{config.NUM_ROUNDS}\n"
        prompt += f"Current scores - You: {llm_score}, Opponent: {human_score}\n\n"
        prompt += f"Last round (Round {round_num}) results:\n"
        prompt += f"- Opponent (Human) chose {human_choice}, You chose {llm_choice}\n"

        # Explain score changes for the LLM based on last round
        # Base score explanation
        prompt += f"- Your base score was {llm_choice}. Opponent base score was {human_choice}.\n"
        # Bonus explanation for LLM
        if llm_choice == human_choice - 1: # LLM got bonus
             prompt += f"- Bonus: You got +{config.BONUS_POINTS} bonus points (Your choice {llm_choice} == Opponent choice {human_choice} - 1).\n"
             prompt += f"- Your total score change was +{llm_score_change}.\n"
             prompt += f"- Opponent total score change was +{human_score_change} (no bonus).\n"
        elif human_choice == llm_choice - 1: # Human got bonus
             prompt += f"- Bonus: Opponent got +{config.BONUS_POINTS} bonus points (Opponent choice {human_choice} == Your choice {llm_choice} - 1).\n"
             prompt += f"- Your total score change was +{llm_score_change} (no bonus).\n"
             prompt += f"- Opponent total score change was +{human_score_change}.\n"
        else: # No bonus
             prompt += f"- Bonus: Neither player received a bonus.\n"
             prompt += f"- Your total score change was +{llm_score_change}.\n"
             prompt += f"- Opponent total score change was +{human_score_change}.\n"

        prompt += "\nBased on the full game history and the last round, what is your choice for this round?"
        return prompt

    def _parse_choice(self, response_content: str) -> int:
        """Parses the LLM's response to extract the numerical choice."""
        if not response_content:
            logger.warning(f"{self.name} response was empty. Defaulting to random choice.")
            return random.choice(config.CHOICES)

        logger.debug(f"Attempting to parse choice from: '{response_content}'")

        # Primary Target: "My choice is: [number]"
        match = re.search(r"My choice is:\s*(\d+)", response_content, re.IGNORECASE)
        if match:
            try:
                choice = int(match.group(1))
                if choice in config.CHOICES:
                    logger.info(f"{self.name} parsed choice: {choice} (from 'My choice is: ...')")
                    return choice
                else:
                    logger.warning(f"{self.name} extracted choice {choice} is outside allowed range {config.CHOICES}. Proceeding to fallbacks.")
            except ValueError:
                 logger.warning(f"{self.name} could not convert matched choice '{match.group(1)}' to int. Proceeding to fallbacks.")

        # Fallback 1: Look for any number within the valid range in the last line
        last_line = response_content.strip().split('\n')[-1]
        numbers_in_last_line = re.findall(r'\d+', last_line)
        valid_numbers = [int(n) for n in numbers_in_last_line if int(n) in config.CHOICES]
        if valid_numbers:
            choice = valid_numbers[-1] # Take the last valid number in the last line
            logger.info(f"{self.name} parsed choice: {choice} (fallback: valid number in last line)")
            return choice

        # Fallback 2: Random choice
        logger.warning(f"{self.name} could not parse choice reliably from response: '{response_content}'. Defaulting to random choice.")
        return random.choice(config.CHOICES)


    def get_llm_choice(self, game_state):
        """Gets the LLM's choice for the current round using conversation history."""

        current_round = game_state['round']
        logger.info(f"--- LLM Turn: Round {current_round} ---") # Log separator to interaction log

        # 1. Format the user prompt
        user_prompt_content = self._format_round_prompt(game_state)
        logger.info(f"Formatted User Prompt for Round {current_round}:\n{user_prompt_content}") # Log full prompt

        # 2. Add user prompt to history & Log to memory
        user_message = {"role": "user", "content": user_prompt_content}
        self.conversation_history.append(user_message)

        # 3. Construct the message list: System Prompt + Full Conversation History
        messages_to_send = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        logger.debug(f"Sending {len(messages_to_send)} messages to API (1 system + {len(self.conversation_history)} history).")
        # Log memory being sent (optional, can be verbose)
        # logger.debug("--- Sending to API ---")
        # for i, msg in enumerate(messages_to_send):
        #     logger.debug(f"  Message {i} ({msg['role']}): {msg['content']}") # Use main logger if uncommented
        # logger.debug("--- End API Send ---")

        try:
            # 4. Call the API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages_to_send,
                temperature=self.temperature,
                max_tokens=150 # Increased token limit for analysis + choice
            )
            response_content = completion.choices[0].message.content.strip()
            logger.info(f"{self.name} Raw Response (Round {current_round}): {response_content}")

            # 5. Add LLM response to history & Log to memory
            assistant_message = {"role": "assistant", "content": response_content}
            self.conversation_history.append(assistant_message)

            # 6. Parse the choice from the response
            llm_choice = self._parse_choice(response_content)
            return llm_choice

        except Exception as e:
            logger.error(f"Error during LLM API call for {self.name}: {e}", exc_info=True)
            # Default strategy in case of API error
            default_choice = random.choice(config.CHOICES) # Random choice on error
            logger.warning(f"API error for {self.name}. Defaulting LLM choice to {default_choice}")
            # Add a placeholder assistant message on error? Maybe not, let history reflect the failure.
            return default_choice

# Keep this clean, no old test code 