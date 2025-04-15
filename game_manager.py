import logging
import csv
import datetime
import config

# Get the root logger configured in llm_player
logger = logging.getLogger()

class GameManager:
    """Manages the game state, rules, scoring, and history."""
    def __init__(self):
        self.human_score = 0
        self.llm_score = 0
        self.round = 1
        # History stores tuples: (round, human_choice, llm_choice, human_score_change, llm_score_change)
        self.history = []
        self.csv_filename = None # Initialize
        self._setup_csv_logger()
        logger.info("GameManager initialized.") # Use root logger for general info

    def _setup_csv_logger(self):
        """Sets up the CSV file for logging game data."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = config.GAME_DATA_CSV_FILE_TEMPLATE.format(timestamp=timestamp)
        try:
            with open(self.csv_filename, 'w', newline='') as csvfile:
                fieldnames = ['Round', 'Human_Choice', 'LLM_Choice', 
                              'Human_Base_Score', 'LLM_Base_Score',
                              'Human_Bonus', 'LLM_Bonus',
                              'Human_Round_Score', 'LLM_Round_Score',
                              'Human_Total_Score', 'LLM_Total_Score']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            logger.info(f"CSV game data log initialized: {self.csv_filename}")
        except IOError as e:
            logger.error(f"Failed to create CSV log file {self.csv_filename}: {e}")
            self.csv_filename = None # Disable CSV logging if creation failed

    def get_game_state(self):
        """Returns the current state needed by the LLM player."""
        return {
            "round": self.round,
            "human_score": self.human_score,
            "llm_score": self.llm_score,
            "history": self.history # Send full history for now, LLM prompt trims it
        }

    def play_round(self, human_choice, llm_choice):
        """Calculates scores for the round, updates totals, and records history."""
        if self.is_game_over():
            logger.warning("Attempted to play round after game over.")
            return None

        human_score_change = 0
        llm_score_change = 0
        human_bonus = 0
        llm_bonus = 0

        # Base scores
        human_base = human_choice
        llm_base = llm_choice
        human_score_change += human_base
        llm_score_change += llm_base

        # Bonus points
        if human_choice == llm_choice - 1:
            human_bonus = config.BONUS_POINTS
            human_score_change += human_bonus
            logger.info(f"Round {self.round}: Human gets bonus ({config.BONUS_POINTS} pts)!")
        elif llm_choice == human_choice - 1:
            llm_bonus = config.BONUS_POINTS
            llm_score_change += llm_bonus
            logger.info(f"Round {self.round}: LLM gets bonus ({config.BONUS_POINTS} pts)!")

        # Update total scores
        self.human_score += human_score_change
        self.llm_score += llm_score_change

        # Record history
        round_data = (
            self.round,
            human_choice,
            llm_choice,
            human_score_change,
            llm_score_change
        )
        self.history.append(round_data)

        # Log to CSV
        if self.csv_filename:
            try:
                with open(self.csv_filename, 'a', newline='') as csvfile:
                    fieldnames = ['Round', 'Human_Choice', 'LLM_Choice', 
                                  'Human_Base_Score', 'LLM_Base_Score',
                                  'Human_Bonus', 'LLM_Bonus',
                                  'Human_Round_Score', 'LLM_Round_Score',
                                  'Human_Total_Score', 'LLM_Total_Score']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({
                        'Round': self.round,
                        'Human_Choice': human_choice,
                        'LLM_Choice': llm_choice,
                        'Human_Base_Score': human_base,
                        'LLM_Base_Score': llm_base,
                        'Human_Bonus': human_bonus,
                        'LLM_Bonus': llm_bonus,
                        'Human_Round_Score': human_score_change,
                        'LLM_Round_Score': llm_score_change,
                        'Human_Total_Score': self.human_score,
                        'LLM_Total_Score': self.llm_score
                    })
            except IOError as e:
                logger.error(f"Failed to write to CSV log file {self.csv_filename}: {e}")

        # Log details
        logger.info(f"Round {self.round} completed: Human chose {human_choice}, LLM chose {llm_choice}. Score Change: Human +{human_score_change}, LLM +{llm_score_change}")
        logger.info(f"Current Scores: Human {self.human_score}, LLM {self.llm_score}")

        # Prepare for next round
        self.round += 1

        return round_data # Return the results of this round

    def is_game_over(self):
        """Checks if the game has reached the maximum number of rounds."""
        return self.round > config.NUM_ROUNDS

    def get_final_scores(self):
        """Returns the final scores."""
        return {"human": self.human_score, "llm": self.llm_score} 