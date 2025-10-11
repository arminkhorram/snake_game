"""
Snake — a simple grid-based game implemented with Pygame.

Prerequisites:
    pip install pygame

Run:
    python3 snake.py

Controls:
    Arrow keys or WASD to move
    Q or Esc to quit
    R to restart (on game over screen)
"""
from __future__ import annotations

import random
import sys
from typing import List, Tuple, Set, Optional

import pygame

# ---------------------------
# Configurable constants
# ---------------------------
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BLOCK_SIZE = 20  # size of each grid block in pixels
FPS = 12  # target frames per second

# Colors (R, G, B)
COLOR_BG = (8, 8, 10)  # near-black background
COLOR_SNAKE = (255, 255, 255)  # pure white snake
COLOR_FOOD = (220, 20, 60)  # bright contrasting (crimson)
COLOR_TEXT = (210, 210, 210)  # light gray for text

# Derived grid metrics
GRID_COLS = WINDOW_WIDTH // BLOCK_SIZE
GRID_ROWS = WINDOW_HEIGHT // BLOCK_SIZE


def grid_align(value: int) -> int:
    """Align a pixel value to the nearest lower multiple of BLOCK_SIZE."""
    return (value // BLOCK_SIZE) * BLOCK_SIZE


def get_initial_snake() -> List[Tuple[int, int]]:
    """Return a starting snake of length 3 centered horizontally."""
    start_x = grid_align(WINDOW_WIDTH // 2)
    start_y = grid_align(WINDOW_HEIGHT // 2)
    return [
        (start_x, start_y),
        (start_x - BLOCK_SIZE, start_y),
        (start_x - 2 * BLOCK_SIZE, start_y),
    ]


def choose_food_position(snake_positions: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    """Choose a random grid cell not occupied by the snake.

    Returns None if no free cells remain (snake fills the grid).
    """
    all_positions = [
        (x, y)
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE)
        for x in range(0, WINDOW_WIDTH, BLOCK_SIZE)
    ]
    available = [pos for pos in all_positions if pos not in snake_positions]
    if not available:
        return None
    return random.choice(available)


def draw_block(surface: pygame.Surface, color: Tuple[int, int, int], pos: Tuple[int, int]) -> None:
    rect = pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surface, color, rect)


def draw_snake(surface: pygame.Surface, snake: List[Tuple[int, int]]) -> None:
    for segment in snake:
        draw_block(surface, COLOR_SNAKE, segment)


def draw_food(surface: pygame.Surface, food_pos: Tuple[int, int]) -> None:
    draw_block(surface, COLOR_FOOD, food_pos)


def render_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    topleft: Tuple[int, int],
) -> None:
    img = font.render(text, True, color)
    surface.blit(img, topleft)


def is_opposite_dir(curr: Tuple[int, int], new: Tuple[int, int]) -> bool:
    return (curr[0] == -new[0] and curr[1] == new[1]) or (curr[1] == -new[1] and curr[0] == new[0])


def play_game(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font_small: pygame.font.Font,
) -> Optional[int]:
    """Run one game session until collision or user quits.

    Returns the final score on game over, or None if the user quits.
    """
    snake = get_initial_snake()
    direction = (1, 0)  # moving right initially (dx, dy) in grid units
    pending_direction = direction

    snake_set: Set[Tuple[int, int]] = set(snake)
    food = choose_food_position(snake_set)
    if food is None:
        food = (0, 0)  # fallback; practically won't happen at start

    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return None
                # Arrow keys and WASD mapping
                if event.key in (pygame.K_UP, pygame.K_w):
                    new_dir = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    new_dir = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    new_dir = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    new_dir = (1, 0)
                else:
                    new_dir = pending_direction

                # Prevent reversing directly into itself when length > 1
                if not is_opposite_dir(direction, new_dir) or len(snake) == 1:
                    pending_direction = new_dir

        # Advance snake by one block on the grid
        direction = pending_direction
        head_x, head_y = snake[0]
        new_head = (head_x + direction[0] * BLOCK_SIZE, head_y + direction[1] * BLOCK_SIZE)

        # Check wall collisions
        if (
            new_head[0] < 0
            or new_head[0] >= WINDOW_WIDTH
            or new_head[1] < 0
            or new_head[1] >= WINDOW_HEIGHT
        ):
            return score

        ate_food = new_head == food

        # Build new body (drop tail if not eating)
        if ate_food:
            new_snake = [new_head] + snake
        else:
            new_snake = [new_head] + snake[:-1]

        # Self collision: if head overlaps any body segment
        if new_head in new_snake[1:]:
            return score

        # Commit the move
        snake = new_snake
        snake_set = set(snake)

        if ate_food:
            score += 1
            food = choose_food_position(snake_set)
            if food is None:
                # Filled the grid — treat as win/end
                return score

        # Draw everything
        screen.fill(COLOR_BG)
        draw_food(screen, food)
        draw_snake(screen, snake)

        # UI: score and a short instruction line
        render_text(screen, f"Score: {score}", font_small, COLOR_TEXT, (10, 6))
        render_text(
            screen,
            "Arrow keys/WASD to move — avoid hitting edges",
            font_small,
            COLOR_TEXT,
            (10, 28),
        )

        pygame.display.flip()
        clock.tick(FPS)

    # Should not reach here under normal flow
    return None


def game_over_screen(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font_small: pygame.font.Font,
    font_large: pygame.font.Font,
    score: int,
) -> str:
    """Display a game over screen and wait for R (restart) or Q/Esc (quit).

    Returns 'restart' or 'quit'.
    """
    # Static render of the screen
    screen.fill(COLOR_BG)

    game_over_text = "Game Over"
    msg_text = "Press R to restart or Q to quit"
    score_text = f"Score: {score}"

    # Centered text positions
    go_img = font_large.render(game_over_text, True, COLOR_TEXT)
    msg_img = font_small.render(msg_text, True, COLOR_TEXT)
    score_img = font_small.render(score_text, True, COLOR_TEXT)

    go_rect = go_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
    score_rect = score_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    msg_rect = msg_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 36))

    screen.blit(go_img, go_rect)
    screen.blit(score_img, score_rect)
    screen.blit(msg_img, msg_rect)
    pygame.display.flip()

    # Event loop for restart/quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return "quit"
                if event.key == pygame.K_r:
                    return "restart"
        clock.tick(30)


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake")
        clock = pygame.time.Clock()

        # Fonts
        font_small = pygame.font.SysFont(None, 22)
        font_medium = pygame.font.SysFont(None, 28)
        font_large = pygame.font.SysFont(None, 48)

        # Main loop across sessions
        while True:
            result = play_game(screen, clock, font_small)
            if result is None:
                break  # user quit during play

            action = game_over_screen(screen, clock, font_small, font_large, result)
            if action == "quit":
                break
            # else: restart automatically loops
    finally:
        pygame.quit()
        # Avoid raising SystemExit in some embeddings/environments; exit cleanly
        try:
            sys.exit(0)
        except SystemExit:
            pass


if __name__ == "__main__":
    main()
