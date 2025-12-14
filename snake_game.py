"""
Snake Game - Fullscreen version using pygame

To run: python snake.py
Requires: pip install pygame

Controls:
- Arrow keys or WASD to move
- F11 to toggle fullscreen
- ESC to quit
- R to restart after game over
- Q to quit after game over
- Close window to exit
"""

import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple


# Game constants
GRID_SIZE = 20
FPS = 10

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)


class GameState(Enum):
    INSTRUCTIONS = 1
    PLAYING = 2
    GAME_OVER = 3


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Snake:
    """Represents the snake in the game"""

    def __init__(self, start_x: int, start_y: int, grid_w: int, grid_h: int):
        self.body = [(start_x, start_y)]
        self.direction = Direction.RIGHT
        self.grow_pending = False
        self.grid_w = grid_w
        self.grid_h = grid_h

    def move(self) -> None:
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)

        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def change_direction(self, new_direction: Direction) -> None:
        # Prevent moving in opposite direction
        if (self.direction == Direction.UP and new_direction == Direction.DOWN) or \
           (self.direction == Direction.DOWN and new_direction == Direction.UP) or \
           (self.direction == Direction.LEFT and new_direction == Direction.RIGHT) or \
           (self.direction == Direction.RIGHT and new_direction == Direction.LEFT):
            return
        self.direction = new_direction

    def grow(self) -> None:
        self.grow_pending = True

    def check_collision(self) -> bool:
        head_x, head_y = self.body[0]

        # Wall collision (based on fullscreen grid size)
        if head_x < 0 or head_x >= self.grid_w or head_y < 0 or head_y >= self.grid_h:
            return True

        # Self collision
        if self.body[0] in self.body[1:]:
            return True

        return False

    def get_positions(self) -> List[Tuple[int, int]]:
        return self.body.copy()


class Food:
    """Represents the food in the game"""

    def __init__(self, grid_w: int, grid_h: int):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.position = self._generate_position()

    def _generate_position(self) -> Tuple[int, int]:
        x = random.randint(0, self.grid_w - 1)
        y = random.randint(0, self.grid_h - 1)
        return (x, y)

    def respawn(self, snake_positions: List[Tuple[int, int]]) -> None:
        while True:
            self.position = self._generate_position()
            if self.position not in snake_positions:
                break

    def get_position(self) -> Tuple[int, int]:
        return self.position


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()

        # --- FULLSCREEN SETUP ---
        self.fullscreen = True
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.screen.get_size()

        # Make sure grid fits cleanly (no partial tiles).
        self.GRID_W = self.WINDOW_WIDTH // GRID_SIZE
        self.GRID_H = self.WINDOW_HEIGHT // GRID_SIZE

        # Optionally crop drawable area to full tiles
        self.DRAW_W = self.GRID_W * GRID_SIZE
        self.DRAW_H = self.GRID_H * GRID_SIZE
        # Center the playable area if you want (usually ends up 0,0 on many screens)
        self.OFFSET_X = (self.WINDOW_WIDTH - self.DRAW_W) // 2
        self.OFFSET_Y = (self.WINDOW_HEIGHT - self.DRAW_H) // 2

        pygame.display.set_caption("Snake Game (Fullscreen)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)

        self.state = GameState.INSTRUCTIONS
        self.score = 0
        self.snake = None
        self.food = None

        self._reset_game()

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        # (0,0) means "use desktop resolution" in fullscreen; in windowed it gives a default res.
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), flags)
        else:
            # pick a reasonable windowed size that fits the grid nicely
            self.screen = pygame.display.set_mode((800, 600), flags)

        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.screen.get_size()
        self.GRID_W = self.WINDOW_WIDTH // GRID_SIZE
        self.GRID_H = self.WINDOW_HEIGHT // GRID_SIZE
        self.DRAW_W = self.GRID_W * GRID_SIZE
        self.DRAW_H = self.GRID_H * GRID_SIZE
        self.OFFSET_X = (self.WINDOW_WIDTH - self.DRAW_W) // 2
        self.OFFSET_Y = (self.WINDOW_HEIGHT - self.DRAW_H) // 2

        # Recreate entities so they respect the new grid size
        self._reset_game()

    def _reset_game(self) -> None:
        start_x = self.GRID_W // 2
        start_y = self.GRID_H // 2
        self.snake = Snake(start_x, start_y, self.GRID_W, self.GRID_H)
        self.food = Food(self.GRID_W, self.GRID_H)
        self.score = 0
        self.state = GameState.PLAYING

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                # Global keys
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                    return

                if self.state == GameState.INSTRUCTIONS:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING

                elif self.state == GameState.PLAYING:
                    self._handle_game_input(event.key)

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self._reset_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def _handle_game_input(self, key: int) -> None:
        if key == pygame.K_UP or key == pygame.K_w:
            self.snake.change_direction(Direction.UP)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.snake.change_direction(Direction.DOWN)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.snake.change_direction(Direction.LEFT)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.snake.change_direction(Direction.RIGHT)

    def _update_game(self) -> None:
        if self.state != GameState.PLAYING:
            return

        self.snake.move()

        if self.snake.check_collision():
            self.state = GameState.GAME_OVER
            return

        if self.snake.body[0] == self.food.get_position():
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.get_positions())

    def _draw(self) -> None:
        self.screen.fill(BLACK)

        if self.state == GameState.INSTRUCTIONS:
            self._draw_instructions()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_instructions(self) -> None:
        title = self.font.render("Snake Game", True, WHITE)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        instructions = [
            "Arrow keys or WASD to move",
            "Eat red food to grow and score",
            "Avoid walls and your own body",
            "",
            "F11: Toggle fullscreen   ESC: Quit",
            "",
            "Press SPACE to start"
        ]

        y_offset = 200
        for line in instructions:
            if line:
                text = self.small_font.render(line, True, WHITE)
                rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, rect)
            y_offset += 34

    def _draw_game(self) -> None:
        # Draw snake (with offset so it stays centered if screen doesn't divide by grid perfectly)
        for (gx, gy) in self.snake.body:
            x = self.OFFSET_X + gx * GRID_SIZE
            y = self.OFFSET_Y + gy * GRID_SIZE
            pygame.draw.rect(self.screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE))

        # Draw food
        fx, fy = self.food.get_position()
        food_x = self.OFFSET_X + fx * GRID_SIZE
        food_y = self.OFFSET_Y + fy * GRID_SIZE
        pygame.draw.rect(self.screen, RED, (food_x, food_y, GRID_SIZE, GRID_SIZE))

        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (12, 12))

        # Bottom hint
        hint = self.small_font.render("F11 toggle fullscreen — ESC quit", True, GRAY)
        self.screen.blit(hint, (12, self.WINDOW_HEIGHT - 36))

    def _draw_game_over(self) -> None:
        game_over_text = self.font.render("Game Over", True, WHITE)
        self.screen.blit(
            game_over_text,
            game_over_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 80))
        )

        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(
            score_text,
            score_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 20))
        )

        restart_text = self.small_font.render("Press R to restart or Q to quit (ESC always quits)", True, WHITE)
        self.screen.blit(
            restart_text,
            restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 40))
        )

    def run(self) -> None:
        while True:
            self._handle_events()
            self._update_game()
            self._draw()
            self.clock.tick(FPS)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
