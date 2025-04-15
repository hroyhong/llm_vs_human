import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Game Rules ---
NUM_ROUNDS = 10
CHOICES = [1, 2, 3, 4, 5]
MIN_CHOICE = CHOICES[0]
MAX_CHOICE = CHOICES[-1]
BONUS_POINTS = 10

# --- LLM Settings ---
# LLM_API_KEY is loaded from .env
LLM_API_KEY = os.getenv("LLM_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
# Default model - can be overridden if needed
# Examples: "anthropic/claude-3-haiku-20240307", "openai/gpt-4o", "google/gemini-flash-1.5"
LLM_MODEL = "openai/gpt-4.1" # Using a free/fast model for now
LLM_TEMPERATURE = 0.7 # Controls randomness (0.0 = deterministic, 1.0 = more random)

# --- Logging & Data Output ---
LOG_DIRECTORY = "logs"
LOG_LEVEL = "DEBUG" # Changed back to DEBUG to see memory logs

# Ensure log directory exists
os.makedirs(LOG_DIRECTORY, exist_ok=True)

LLM_INTERACTION_LOG_FILE = os.path.join(LOG_DIRECTORY, "llm_interactions.log")
# LLM_MEMORY_LOG_FILE_TEMPLATE = os.path.join(LOG_DIRECTORY, "llm_memory_{timestamp}.log") # Removed memory log file
GAME_DATA_CSV_FILE_TEMPLATE = os.path.join(LOG_DIRECTORY, "game_data_{timestamp}.csv") # Use timestamp for unique files

# Optional detailed game log (not currently used)
# GAME_LOG_FILE = os.path.join(LOG_DIRECTORY, "game_log.txt")
# ENABLE_DETAILED_GAME_LOG = False

# --- Pygame UI Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_NAME = None # Use default pygame font
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 28
FONT_SIZE_SMALL = 20

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
BLUE = (100, 100, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BUTTON_COLOR = (0, 150, 200)
BUTTON_HOVER_COLOR = (0, 200, 255)
BUTTON_TEXT_COLOR = WHITE

# UI Layout
PADDING = 20
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
HISTORY_AREA_HEIGHT = 200
STATUS_AREA_HEIGHT = 50

# --- (Optional) Pygame UI Settings (We'll use these later) ---
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600
# FONT_SIZE = 24
# COLORS = {
#     "white": (255, 255, 255),
#     "black": (0, 0, 0),
#     "blue": (0, 0, 255),
#     "red": (255, 0, 0),
#     "gray": (200, 200, 200),
# } 