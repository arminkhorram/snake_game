#!/usr/bin/env python3
"""
Snake Game - A classic implementation using pygame

To run: python snake.py
Requires: pip install pygame

Controls:
- Arrow keys or WASD to move
- R to restart after game over
- Q to quit after game over
- Close window to exit

Gameplay:
- Eat red food to grow and increase score
- Avoid hitting walls or your own body
- Snake moves continuously in the current direction
"""

import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple, Optional


# Game constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
GRID_SIZE = 20
FPS = 10

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Game states
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
    
    def __init__(self, start_x: int, start_y: int):
        self.body = [(start_x, start_y)]
        self.direction = Direction.RIGHT
        self.grow_pending = False
    
    def move(self) -> None:
        """Move the snake in the current direction"""
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        self.body.insert(0, new_head)
        
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False
    
    def change_direction(self, new_direction: Direction) -> None:
        """Change snake direction (prevents moving into itself)"""
        # Prevent moving in opposite direction
        if (self.direction == Direction.UP and new_direction == Direction.DOWN) or \
           (self.direction == Direction.DOWN and new_direction == Direction.UP) or \
           (self.direction == Direction.LEFT and new_direction == Direction.RIGHT) or \
           (self.direction == Direction.RIGHT and new_direction == Direction.LEFT):
            return
        
        self.direction = new_direction
    
    def grow(self) -> None:
        """Mark snake to grow on next move"""
        self.grow_pending = True
    
    def check_collision(self) -> bool:
        """Check if snake collided with walls or itself"""
        head_x, head_y = self.body[0]
        
        # Check wall collision
        if (head_x < 0 or head_x >= WINDOW_WIDTH // GRID_SIZE or
            head_y < 0 or head_y >= WINDOW_HEIGHT // GRID_SIZE):
            return True
        
        # Check self collision
        if self.body[0] in self.body[1:]:
            return True
        
        return False
    
    def get_positions(self) -> List[Tuple[int, int]]:
        """Get all snake body positions"""
        return self.body.copy()


class Food:
    """Represents the food in the game"""
    
    def __init__(self):
        self.position = self._generate_position()
    
    def _generate_position(self) -> Tuple[int, int]:
        """Generate a random position for food"""
        x = random.randint(0, WINDOW_WIDTH // GRID_SIZE - 1)
        y = random.randint(0, WINDOW_HEIGHT // GRID_SIZE - 1)
        return (x, y)
    
    def respawn(self, snake_positions: List[Tuple[int, int]]) -> None:
        """Respawn food at a position not occupied by snake"""
        while True:
            self.position = self._generate_position()
            if self.position not in snake_positions:
                break
    
    def get_position(self) -> Tuple[int, int]:
        """Get current food position"""
        return self.position


class Game:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.state = GameState.INSTRUCTIONS
        self.score = 0
        self.snake = None
        self.food = None
        
        self._reset_game()
    
    def _reset_game(self) -> None:
        """Reset game to initial state"""
        start_x = WINDOW_WIDTH // GRID_SIZE // 2
        start_y = WINDOW_HEIGHT // GRID_SIZE // 2
        self.snake = Snake(start_x, start_y)
        self.food = Food()
        self.score = 0
        self.state = GameState.PLAYING
    
    def _handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
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
        """Handle input during gameplay"""
        if key == pygame.K_UP or key == pygame.K_w:
            self.snake.change_direction(Direction.UP)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.snake.change_direction(Direction.DOWN)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.snake.change_direction(Direction.LEFT)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.snake.change_direction(Direction.RIGHT)
    
    def _update_game(self) -> None:
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        # Move snake
        self.snake.move()
        
        # Check collisions
        if self.snake.check_collision():
            self.state = GameState.GAME_OVER
            return
        
        # Check food collision
        if self.snake.body[0] == self.food.get_position():
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.get_positions())
    
    def _draw(self) -> None:
        """Draw everything on screen"""
        self.screen.fill(BLACK)
        
        if self.state == GameState.INSTRUCTIONS:
            self._draw_instructions()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        
        pygame.display.flip()
    
    def _draw_instructions(self) -> None:
        """Draw instructions screen"""
        title = self.font.render("Snake Game", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "Arrow keys or WASD to move",
            "Eat red food to grow and score",
            "Avoid walls and your own body",
            "",
            "Press SPACE to start"
        ]
        
        y_offset = 150
        for instruction in instructions:
            if instruction:  # Skip empty lines
                text = self.small_font.render(instruction, True, WHITE)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 30
    
    def _draw_game(self) -> None:
        """Draw game elements"""
        # Draw snake
        for segment in self.snake.body:
            x = segment[0] * GRID_SIZE
            y = segment[1] * GRID_SIZE
            pygame.draw.rect(self.screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE))
        
        # Draw food
        food_x = self.food.get_position()[0] * GRID_SIZE
        food_y = self.food.get_position()[1] * GRID_SIZE
        pygame.draw.rect(self.screen, RED, (food_x, food_y, GRID_SIZE, GRID_SIZE))
        
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw instructions
        instructions = self.small_font.render("Arrow keys to move — avoid hitting edges", True, GRAY)
        self.screen.blit(instructions, (10, WINDOW_HEIGHT - 30))
    
    def _draw_game_over(self) -> None:
        """Draw game over screen"""
        # Draw game over text
        game_over_text = self.font.render("Game Over", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw final score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart instructions
        restart_text = self.small_font.render("Press R to restart or Q to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self) -> None:
        """Main game loop"""
        while True:
            self._handle_events()
            self._update_game()
            self._draw()
            self.clock.tick(FPS)


def main():
    """Entry point of the program"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()