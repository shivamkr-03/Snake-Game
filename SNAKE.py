import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 12  # Reduced from 20 to 12
GRID_WIDTH, GRID_HEIGHT = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (231, 76, 60)
DARK_WHITE = (240, 240, 240)

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Modern Snake")
clock = pygame.time.Clock()

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.position = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = self.direction
        self.growth_pending = 3  # Start with a snake of length 4
        self.score = 0
        self.game_over = False
        self.speed = 8  # Moves per second
        self.move_timer = 0
    
    def update(self, dt):
        # Update the move timer
        self.move_timer += dt
        move_delay = 1000 // self.speed
        
        # Only move when enough time has passed
        if self.move_timer >= move_delay:
            self.move_timer = 0
            
            # Update direction
            self.direction = self.next_direction
            
            # Get the current head position
            head_x, head_y = self.position[0]
            
            # Calculate new head position
            dx, dy = self.direction
            new_head = (head_x + dx, head_y + dy)
            
            # Check for wall collision
            new_x, new_y = new_head
            if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                # Wrap around the screen
                new_x = (new_x + GRID_WIDTH) % GRID_WIDTH
                new_y = (new_y + GRID_HEIGHT) % GRID_HEIGHT
                new_head = (new_x, new_y)
            
            # Check for self collision
            if new_head in self.position[:-1]:
                self.game_over = True
                return
            
            # Add the new head
            self.position.insert(0, new_head)
            
            # Remove the tail or grow
            if self.growth_pending > 0:
                self.growth_pending -= 1
            else:
                self.position.pop()
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction
    
    def check_food_collision(self, food_position):
        return self.position[0] == food_position
    
    def grow(self, amount=1):
        self.growth_pending += amount
        self.score += 10
        
        # Increase speed every 5 food items, up to a maximum speed
        if self.score % 50 == 0:
            self.speed = min(15, self.speed + 1)
    
    def draw(self, surface):
        # Draw each segment as a circle
        for i, (x, y) in enumerate(self.position):
            # Convert grid coordinates to pixel coordinates
            center_x = x * GRID_SIZE + GRID_SIZE // 2
            center_y = y * GRID_SIZE + GRID_SIZE // 2
            
            # Draw circle with larger radius to reduce gaps
            radius = GRID_SIZE // 2 - 1  # Increased from -2 to -1
            color = DARK_WHITE if i == 0 else WHITE  # Head is slightly different color
            pygame.draw.circle(surface, color, (center_x, center_y), radius)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()
    
    def spawn(self, avoid_positions=None):
        if avoid_positions is None:
            avoid_positions = []
        
        # Find all available grid positions
        available = [
            (x, y) 
            for x in range(GRID_WIDTH) 
            for y in range(GRID_HEIGHT)
            if (x, y) not in avoid_positions
        ]
        
        if available:
            self.position = random.choice(available)
        else:
            # If no positions available, just pick a random spot
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
    
    def draw(self, surface):
        # Convert grid coordinates to pixel coordinates
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2
        
        # Draw circle with larger radius to match snake segments
        radius = GRID_SIZE // 2 - 1  # Increased from -2 to -1 
        pygame.draw.circle(surface, RED, (center_x, center_y), radius)

# Load fonts globally - using modern minimalist fonts
try:
    # Try to load custom fonts
    FONT_TITLE = pygame.font.Font(None, 60)  # Default pygame font at large size
    FONT_MEDIUM = pygame.font.Font(None, 32)  # Default pygame font
except:
    # Fallback to system fonts
    FONT_TITLE = pygame.font.SysFont('consolas', 56)  # Monospaced font for retro-modern feel
    FONT_MEDIUM = pygame.font.SysFont('consolas', 28)  # Keeping consistent font family

def draw_game_over(surface, score):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Draw game over text with clean, minimalist style
    game_over_text = FONT_TITLE.render('GAME OVER', True, WHITE)
    surface.blit(
        game_over_text, 
        (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60)
    )
    
    # Draw score with consistent style
    score_text = FONT_MEDIUM.render(f'Final Score: {score}', True, WHITE)
    surface.blit(
        score_text, 
        (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2)
    )
    
    # Draw restart text
    restart_text = FONT_MEDIUM.render('Press SPACE to restart', True, WHITE)
    surface.blit(
        restart_text, 
        (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50)
    )

def draw_pause_screen(surface):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))
    
    # Draw paused text with clean style
    paused_text = FONT_TITLE.render('PAUSED', True, WHITE)
    surface.blit(
        paused_text, 
        (WIDTH // 2 - paused_text.get_width() // 2, HEIGHT // 2 - 35)
    )
    
    # Draw resume text
    resume_text = FONT_MEDIUM.render('Press any key to resume', True, WHITE)
    surface.blit(
        resume_text, 
        (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 35)
    )

def main():
    snake = Snake()
    food = Food()
    game_over = False
    paused = False
    
    # Game loop
    while True:
        # Get time since last frame in milliseconds
        dt = clock.tick(FPS)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle key events
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        # Restart the game
                        snake.reset()
                        food.spawn(snake.position)
                        game_over = False
                elif paused:
                    # Any key press resumes the game
                    paused = False
                else:
                    # Check for pause key (Escape)
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                    # Change direction based on arrow keys
                    elif event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
        
        # Update game state (only if not paused and not game over)
        if not game_over and not paused:
            # Update snake
            snake.update(dt)
            game_over = snake.game_over
            
            # Check for food collision
            if snake.check_food_collision(food.position):
                snake.grow()
                food.spawn(snake.position)
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw game elements
        food.draw(screen)
        snake.draw(screen)
        
        # Draw game over screen if game is over
        if game_over:
            draw_game_over(screen, snake.score)
        # Draw pause screen if paused
        elif paused:
            draw_pause_screen(screen)
        
        # Update display
        pygame.display.flip()

if __name__ == "__main__":
    main()