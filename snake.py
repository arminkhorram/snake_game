"""
Snake Game - A classic Snake implementation using Pygame

Instructions:
- Use arrow keys or WASD to move the snake
- Eat red food to grow and increase your score
- Avoid hitting the edges or your own body
- Press R to restart after game over, Q to quit

Requirements:
    pip install pygame

Run with: python snake.py
"""

import pygame
import random
import sys
from enum import Enum

# Game constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
GRID_SIZE = 20
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Grid dimensions
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2

class Snake:
    """Represents the snake with movement and collision detection"""
    
    def __init__(self):
        # Start in the center of the grid
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y)]
        self.direction = Direction.RIGHT
        self.grow_next_move = False
    
    def move(self):
        """Move the snake in the current direction"""
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Remove tail if not growing
        if not self.grow_next_move:
            self.body.pop()
        else:
            self.grow_next_move = False
    
    def change_direction(self, new_direction):
        """Change direction if not opposite to current direction"""
        current_dx, current_dy = self.direction.value
        new_dx, new_dy = new_direction.value
        
        # Don't allow reversing into self
        if (current_dx + new_dx) == 0 and (current_dy + new_dy) == 0:
            return
        
        self.direction = new_direction
    
    def check_wall_collision(self):
        """Check if snake hit the wall"""
        head_x, head_y = self.body[0]
        return (head_x < 0 or head_x >= GRID_WIDTH or 
                head_y < 0 or head_y >= GRID_HEIGHT)
    
    def check_self_collision(self):
        """Check if snake hit itself"""
        head = self.body[0]
        return head in self.body[1:]
    
    def grow(self):
        """Mark snake to grow on next move"""
        self.grow_next_move = True
    
    def get_positions(self):
        """Get all positions occupied by the snake"""
        return self.body.copy()

class Food:
    """Represents the food item that spawns randomly"""
    
    def __init__(self):
        self.position = (0, 0)
        self.spawn()
    
    def spawn(self, snake_positions=None):
        """Spawn food at random position not occupied by snake"""
        if snake_positions is None:
            snake_positions = []
        
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_positions:
                self.position = (x, y)
                break

class Game:
    """Main game class managing game state and rendering"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state"""
        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.get_positions())
        self.score = 0
        self.state = GameState.PLAYING
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAYING:
                    # Movement controls
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction(Direction.RIGHT)
                
                elif self.state == GameState.GAME_OVER:
                    # Game over controls
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
        
        return True
    
    def update(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        # Move snake
        self.snake.move()
        
        # Check collisions
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self.state = GameState.GAME_OVER
            return
        
        # Check food collision
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.get_positions())
    
    def draw_grid_rect(self, surface, color, grid_x, grid_y):
        """Draw a rectangle at grid coordinates"""
        pixel_x = grid_x * GRID_SIZE
        pixel_y = grid_y * GRID_SIZE
        rect = pygame.Rect(pixel_x, pixel_y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, color, rect)
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(BLACK)
        
        if self.state == GameState.PLAYING:
            # Draw snake
            for segment in self.snake.body:
                self.draw_grid_rect(self.screen, WHITE, segment[0], segment[1])
            
            # Draw food
            self.draw_grid_rect(self.screen, RED, self.food.position[0], self.food.position[1])
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Draw instructions
            instruction_text = self.small_font.render("Arrow keys/WASD to move — avoid hitting edges", True, WHITE)
            self.screen.blit(instruction_text, (10, WINDOW_HEIGHT - 30))
        
        elif self.state == GameState.GAME_OVER:
            # Draw final snake and food (dimmed)
            for segment in self.snake.body:
                self.draw_grid_rect(self.screen, (128, 128, 128), segment[0], segment[1])
            self.draw_grid_rect(self.screen, (128, 0, 0), self.food.position[0], self.food.position[1])
            
            # Draw game over screen
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = self.small_font.render("Press R to restart or Q to quit", True, WHITE)
            
            # Center the text
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game
            self.update()
            
            # Render
            self.render()
            
            # Control frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()