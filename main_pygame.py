import time
import pygame # Import pygame
import sys # For sys.exit

import config
from game_manager import GameManager
from llm_player import LLMPlayer

# Get the root logger configured in llm_player
import logging # Keep import for logger usage
logger = logging.getLogger()

# import pygame # Keep pygame imports commented out for now

# Configure logging (redundant if llm_player already configured it, but safe)
# logging.basicConfig(
#     level=getattr(logging, config.LOG_LEVEL, logging.INFO),
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler(config.LLM_INTERACTION_LOG_FILE), # Log to file
#         logging.StreamHandler() # Also print logs to console
#     ]
# )

# --- Pygame Setup ---
pygame.init()
pygame.font.init() # Initialize font module

screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Human vs LLM Game")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_LARGE)
font_medium = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_MEDIUM)
font_small = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_SMALL)

# --- Helper Functions for Drawing ---

def draw_text(surface, text, font, color, x, y, align="topleft"):
    """Draws text on a surface with specified alignment."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    # Set the position based on alignment using Rect attributes
    if align == "center":
        text_rect.center = (x, y)
    elif align == "topright":
        text_rect.topright = (x, y)
    elif align == "midright":
        text_rect.midright = (x, y)
    elif align == "midleft":
        text_rect.midleft = (x, y)
    elif align == "midtop":
        text_rect.midtop = (x, y)
    # Add more alignments as needed (e.g., bottomleft, bottomright, midbottom)
    else: # Default to topleft
        text_rect.topleft = (x, y)

    surface.blit(text_surface, text_rect)
    return text_rect

class Button:
    """Simple Button class for Pygame."""
    def __init__(self, x, y, width, height, text='', color=config.BUTTON_COLOR, hover_color=config.BUTTON_HOVER_COLOR, text_color=config.BUTTON_TEXT_COLOR, font=font_medium):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        if self.text:
            draw_text(surface, self.text, self.font, self.text_color, self.rect.centerx, self.rect.centery, align="center")

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1: # Left click
                return True # Clicked
        return False

# --- UI Drawing Functions ---

def draw_scores(surface, human_score, llm_score, llm_name):
    draw_text(surface, f"You: {human_score}", font_large, config.BLUE, config.PADDING, config.PADDING, align="topleft")
    score_text = f"{llm_name}: {llm_score}"
    draw_text(surface, score_text, font_large, config.RED,
              config.SCREEN_WIDTH - config.PADDING, config.PADDING, align="topright")

def draw_round_info(surface, round_num):
    draw_text(surface, f"Round: {round_num}/{config.NUM_ROUNDS}", font_medium, config.BLACK,
              config.SCREEN_WIDTH // 2, config.PADDING + config.FONT_SIZE_LARGE // 2, align="center")

def draw_status(surface, status_text):
    status_rect = pygame.Rect(0, config.SCREEN_HEIGHT - config.STATUS_AREA_HEIGHT, config.SCREEN_WIDTH, config.STATUS_AREA_HEIGHT)
    pygame.draw.rect(surface, config.LIGHT_GRAY, status_rect)
    draw_text(surface, status_text, font_medium, config.BLACK, status_rect.centerx, status_rect.centery, align="center")

def draw_buttons(surface, buttons):
    for button in buttons.values():
        button.draw(surface)

def draw_history(surface, history):
    history_rect = pygame.Rect(config.PADDING, config.SCREEN_HEIGHT - config.STATUS_AREA_HEIGHT - config.HISTORY_AREA_HEIGHT - config.PADDING,
                              config.SCREEN_WIDTH - 2 * config.PADDING, config.HISTORY_AREA_HEIGHT)
    pygame.draw.rect(surface, config.WHITE, history_rect) # White background for history
    pygame.draw.rect(surface, config.GRAY, history_rect, 2) # Border

    draw_text(surface, "Last Round Result:", font_medium, config.BLACK, history_rect.left + 10, history_rect.top + 10, align="topleft")

    if history:
        last_round_num, last_human, last_llm, last_h_change, last_l_change = history[-1]
        result_text = f"R{last_round_num}: You chose {last_human} (+{last_h_change}), LLM chose {last_llm} (+{last_l_change})"
        draw_text(surface, result_text, font_small, config.BLACK, history_rect.left + 10, history_rect.top + 10 + config.FONT_SIZE_MEDIUM + 5, align="topleft")
    else:
         draw_text(surface, "N/A (First Round)", font_small, config.GRAY, history_rect.left + 10, history_rect.top + 10 + config.FONT_SIZE_MEDIUM + 5, align="topleft")


# --- Main Game Function (Pygame) ---

def run_pygame_game():
    logger.info("Starting new game (Pygame Mode)...")
    game_manager = GameManager()
    llm_player = LLMPlayer()

    # Create choice buttons
    buttons = {}
    button_y = config.SCREEN_HEIGHT - config.STATUS_AREA_HEIGHT - config.HISTORY_AREA_HEIGHT - config.PADDING - config.BUTTON_HEIGHT - config.PADDING
    total_button_width = len(config.CHOICES) * config.BUTTON_WIDTH + (len(config.CHOICES) - 1) * config.PADDING
    start_x = (config.SCREEN_WIDTH - total_button_width) // 2

    for i, choice in enumerate(config.CHOICES):
        button_x = start_x + i * (config.BUTTON_WIDTH + config.PADDING)
        buttons[choice] = Button(button_x, button_y, config.BUTTON_WIDTH, config.BUTTON_HEIGHT, text=str(choice))

    status = "Your Turn! Choose a number."
    human_choice = None
    llm_choice = None
    waiting_for_llm = False
    last_round_result_display = None # To show results briefly
    round_start_time = time.time()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        clicked_button = None

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not waiting_for_llm and not game_manager.is_game_over():
                    for choice, button in buttons.items():
                        if button.handle_event(event):
                            clicked_button = choice
                            break

            # Update button hover state
            if not waiting_for_llm and not game_manager.is_game_over():
                 for button in buttons.values():
                     button.handle_event(event)

        # --- Game Logic Update ---
        if clicked_button is not None and not waiting_for_llm:
            human_choice = clicked_button
            logger.info(f"Human chose: {human_choice}")
            status = f"You chose {human_choice}. Waiting for {llm_player.name}..."
            waiting_for_llm = True
            # TODO: Trigger LLM choice in a non-blocking way if possible, or just accept the pause
            game_state = game_manager.get_game_state()
            llm_choice = llm_player.get_llm_choice(game_state)
            logger.info(f"LLM choice received: {llm_choice}")

            # Play the round
            round_result = game_manager.play_round(human_choice, llm_choice)
            last_round_result_display = round_result # Store result for display
            waiting_for_llm = False
            human_choice = None
            llm_choice = None
            round_start_time = time.time()

            if game_manager.is_game_over():
                final_scores = game_manager.get_final_scores()
                winner = "You" if final_scores['human'] > final_scores['llm'] else llm_player.name if final_scores['llm'] > final_scores['human'] else "Tie"
                status = f"Game Over! Final Score - You: {final_scores['human']} | {llm_player.name}: {final_scores['llm']} ({winner} wins!)"
                logger.info(status)
            else:
                 status = "Your Turn! Choose a number."

        # --- Drawing --- (Order matters: background -> elements)
        screen.fill(config.LIGHT_GRAY) # Background

        draw_scores(screen, game_manager.human_score, game_manager.llm_score, llm_player.name)
        draw_round_info(screen, game_manager.round if not game_manager.is_game_over() else config.NUM_ROUNDS)
        draw_buttons(screen, buttons)
        draw_history(screen, game_manager.history) # Draw history box + last round
        draw_status(screen, status)

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Limiting ---
        clock.tick(60) # Limit to 60 FPS

    pygame.quit()
    logger.info("Pygame game finished.")
    if game_manager.csv_filename:
        print(f"Game data saved to: {game_manager.csv_filename}")
    print(f"LLM interactions logged to: {config.LLM_INTERACTION_LOG_FILE}")

# --- Terminal Game Function (Keep for reference/fallback) ---
# (run_terminal_game function code is here, unchanged)
# ...

if __name__ == "__main__":
    # run_terminal_game() # Run terminal version
    run_pygame_game() # Run Pygame version 