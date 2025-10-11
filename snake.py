"""
Classic Snake Game using Pygame

Run Instructions:
1. Install pygame: pip install pygame
2. Run: python snake.py
3. Use arrow keys (or WASD) to control the snake
4. Eat the red dot to grow and score points
5. Avoid hitting the edges or your own body!
"""

import pygame
import random
import sys

# Configuration constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BLOCK_SIZE = 20
FPS = 10

# Colors (RGB)
COLOR_BACKGROUND = (10, 10, 10)  # Near-black
COLOR_SNAKE = (255, 255, 255)  # Pure white
COLOR_FOOD = (255, 0, 0)  # Bright red
COLOR_TEXT = (200, 200, 200)  # Light gray for text

# Direction vectors
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)


class Snake:
    """Represents the snake with its body segments and current direction."""
    
    def __init__(self):
        """Initialize snake at the center of the screen."""
        center_x = (WINDOW_WIDTH // 2) // BLOCK_SIZE * BLOCK_SIZE
        center_y = (WINDOW_HEIGHT // 2) // BLOCK_SIZE * BLOCK_SIZE
        # Body is a list of (x, y) tuples, head is first element
        self.body = [(center_x, center_y), (center_x - BLOCK_SIZE, center_y), 
                     (center_x - 2 * BLOCK_SIZE, center_y)]
        self.direction = DIR_RIGHT
        self.grow_pending = False
    
    def move(self):
        """Move the snake one block in the current direction."""
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0] * BLOCK_SIZE, 
                    head_y + self.direction[1] * BLOCK_SIZE)
        
        # Add new head
        self.body.insert(0, new_head)
        
        # Remove tail unless we're growing
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False
    
    def change_direction(self, new_direction):
        """Change direction, but prevent 180-degree turns."""
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction
    
    def grow(self):
        """Mark that the snake should grow on next move."""
        self.grow_pending = True
    
    def check_collision(self):
        """Check if snake hits walls or itself. Returns True if collision."""
        head_x, head_y = self.body[0]
        
        # Check wall collision
        if (head_x < 0 or head_x >= WINDOW_WIDTH or 
            head_y < 0 or head_y >= WINDOW_HEIGHT):
            return True
        
        # Check self-collision (head with any body segment except head)
        if self.body[0] in self.body[1:]:
            return True
        
        return False
    
    def get_occupied_cells(self):
        """Return set of all cells occupied by snake."""
        return set(self.body)


def spawn_food(snake):
    """Spawn food at a random grid position not occupied by snake."""
    occupied = snake.get_occupied_cells()
    
    # Calculate all possible grid positions
    grid_width = WINDOW_WIDTH // BLOCK_SIZE
    grid_height = WINDOW_HEIGHT // BLOCK_SIZE
    
    while True:
        x = random.randint(0, grid_width - 1) * BLOCK_SIZE
        y = random.randint(0, grid_height - 1) * BLOCK_SIZE
        if (x, y) not in occupied:
            return (x, y)


def draw_game(screen, snake, food, score, game_over):
    """Draw all game elements on the screen."""
    screen.fill(COLOR_BACKGROUND)
    
    if not game_over:
        # Draw snake
        for segment in snake.body:
            rect = pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, COLOR_SNAKE, rect)
        
        # Draw food
        food_rect = pygame.Rect(food[0], food[1], BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, COLOR_FOOD, food_rect)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, COLOR_TEXT)
        screen.blit(score_text, (10, 10))
        
        # Draw instructions
        small_font = pygame.font.Font(None, 24)
        instruction_text = small_font.render("Arrow keys to move - avoid hitting edges", True, COLOR_TEXT)
        screen.blit(instruction_text, (10, WINDOW_HEIGHT - 30))
    else:
        # Draw game over screen
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        game_over_text = font_large.render("GAME OVER", True, COLOR_FOOD)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        screen.blit(game_over_text, game_over_rect)
        
        score_text = font_medium.render(f"Final Score: {score}", True, COLOR_TEXT)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        restart_text = font_small.render("Press R to restart or Q to quit", True, COLOR_TEXT)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()


def handle_input(snake):
    """Process keyboard input for controlling the snake."""
    keys = pygame.key.get_pressed()
    
    # Arrow keys
    if keys[pygame.K_UP]:
        snake.change_direction(DIR_UP)
    elif keys[pygame.K_DOWN]:
        snake.change_direction(DIR_DOWN)
    elif keys[pygame.K_LEFT]:
        snake.change_direction(DIR_LEFT)
    elif keys[pygame.K_RIGHT]:
        snake.change_direction(DIR_RIGHT)
    
    # WASD keys (optional)
    elif keys[pygame.K_w]:
        snake.change_direction(DIR_UP)
    elif keys[pygame.K_s]:
        snake.change_direction(DIR_DOWN)
    elif keys[pygame.K_a]:
        snake.change_direction(DIR_LEFT)
    elif keys[pygame.K_d]:
        snake.change_direction(DIR_RIGHT)


def main():
    """Main game loop."""
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    
    # Game state variables
    snake = Snake()
    food = spawn_food(snake)
    score = 0
    game_over = False
    running = True
    
    # Main game loop
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # Restart game
                        snake = Snake()
                        food = spawn_food(snake)
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_q:
                        running = False
        
        if not game_over:
            # Handle input
            handle_input(snake)
            
            # Move snake
            snake.move()
            
            # Check for food collision
            if snake.body[0] == food:
                snake.grow()
                score += 1
                food = spawn_food(snake)
            
            # Check for game over conditions
            if snake.check_collision():
                game_over = True
        
        # Draw everything
        draw_game(screen, snake, food, score, game_over)
        
        # Control frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
