#!/usr/bin/env python3
"""
Raspberry Pi Flappy Bird Game
A simple Flappy Bird clone using pygame and GPIO touch sensor control.
Optimized for Raspberry Pi with proper GPIO handling and smooth gameplay.

Hardware Requirements:
- Raspberry Pi (any model with GPIO)
- Touch sensor or button connected to GPIO 2 (with pull-up resistor)
- Optional: Speaker/headphones for sound effects

Author: Claude AI Assistant
License: MIT
"""

import pygame
import random
import sys
import os
import time
from typing import List, Tuple, Optional

# GPIO handling with fallback for non-Pi systems
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not available. Using keyboard controls instead.")

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
SKY_BLUE = (135, 206, 235)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 100, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Physics constants
GRAVITY = 0.8  # Increased for more noticeable falling
JUMP_STRENGTH = -8 # More negative for stronger jump
BIRD_SIZE = 30
PIPE_WIDTH = 80
PIPE_GAP = 200
PIPE_SPEED = 3

# GPIO configuration
GPIO_PIN = 2
DEBOUNCE_TIME = 0.2  # Seconds


class Bird:
    """Represents the player-controlled bird."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = float(y)  # Use float for smoother movement
        self.velocity = 0.0  # Use float for velocity
        self.size = BIRD_SIZE
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
    
    def jump(self):
        """Make the bird jump upward."""
        self.velocity = float(JUMP_STRENGTH)  # Ensure float type
    
    def update(self):
        """Update bird position with gravity."""
        # Apply gravity (positive value makes bird fall down)
        self.velocity += GRAVITY
        
        # Update vertical position
        self.y += self.velocity
        
        # Limit maximum fall speed to prevent going through pipes
        if self.velocity > 10:
            self.velocity = 10
        
        # Update collision rectangle
        self.rect.x = self.x - self.size // 2
        self.rect.y = self.y - self.size // 2
    
    def draw(self, screen: pygame.Surface):
        """Draw the bird on the screen."""
        # Draw bird as a circle
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.size // 2)
        # Add a simple eye
        eye_x = int(self.x + self.size // 4)
        eye_y = int(self.y - self.size // 6)
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 4)
        pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle for the bird."""
        return self.rect


class Pipe:
    """Represents a pipe obstacle with a gap."""
    
    def __init__(self, x: int, gap_y: int):
        self.x = x
        self.gap_y = gap_y
        self.width = PIPE_WIDTH
        self.gap_height = PIPE_GAP
        self.passed = False
        
        # Create rectangles for collision detection
        self.top_rect = pygame.Rect(x, 0, self.width, gap_y - self.gap_height // 2)
        self.bottom_rect = pygame.Rect(x, gap_y + self.gap_height // 2, self.width, 
                                     SCREEN_HEIGHT - (gap_y + self.gap_height // 2))
    
    def update(self):
        """Move pipe to the left."""
        self.x -= PIPE_SPEED
        # Update collision rectangles
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, screen: pygame.Surface):
        """Draw the pipe on the screen."""
        # Draw top pipe
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, DARK_GREEN, self.top_rect, 3)
        
        # Draw bottom pipe
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        pygame.draw.rect(screen, DARK_GREEN, self.bottom_rect, 3)
        
        # Draw pipe caps (decorative)
        cap_height = 30
        cap_width = self.width + 10
        
        # Top cap
        top_cap = pygame.Rect(self.x - 5, self.top_rect.height - cap_height, 
                             cap_width, cap_height)
        pygame.draw.rect(screen, GREEN, top_cap)
        pygame.draw.rect(screen, DARK_GREEN, top_cap, 3)
        
        # Bottom cap
        bottom_cap = pygame.Rect(self.x - 5, self.bottom_rect.y, cap_width, cap_height)
        pygame.draw.rect(screen, GREEN, bottom_cap)
        pygame.draw.rect(screen, DARK_GREEN, bottom_cap, 3)
    
    def collides_with(self, bird_rect: pygame.Rect) -> bool:
        """Check if bird collides with this pipe."""
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(self.bottom_rect)
    
    def is_off_screen(self) -> bool:
        """Check if pipe is completely off the left side of screen."""
        return self.x + self.width < 0


class SoundManager:
    """Handles game sound effects."""
    
    def __init__(self):
        self.sounds_enabled = True
        self.sounds = {}
        
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._create_sounds()
        except pygame.error:
            print("Warning: Sound system not available.")
            self.sounds_enabled = False
    
    def _create_sounds(self):
        """Create simple sound effects programmatically."""
        try:
            # Create jump sound (short beep)
            duration = 0.1
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = []
            for i in range(frames):
                time_val = float(i) / sample_rate
                wave = int(4096 * 0.3 * 
                          (pygame.math.cos(time_val * 880 * 2 * pygame.math.pi) +
                           pygame.math.cos(time_val * 1760 * 2 * pygame.math.pi)) / 2)
                arr.append([wave, wave])
            
            self.sounds['jump'] = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            
            # Create score sound (higher pitch)
            arr = []
            for i in range(frames):
                time_val = float(i) / sample_rate
                wave = int(4096 * 0.2 * pygame.math.cos(time_val * 1320 * 2 * pygame.math.pi))
                arr.append([wave, wave])
            
            self.sounds['score'] = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            
            # Create collision sound (lower, harsh)
            duration = 0.3
            frames = int(duration * sample_rate)
            arr = []
            for i in range(frames):
                time_val = float(i) / sample_rate
                wave = int(4096 * 0.1 * pygame.math.cos(time_val * 200 * 2 * pygame.math.pi) * 
                          (1 - time_val / duration))
                arr.append([wave, wave])
            
            self.sounds['collision'] = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            
        except Exception as e:
            print(f"Warning: Could not create sounds: {e}")
            self.sounds_enabled = False
    
    def play(self, sound_name: str):
        """Play a sound effect."""
        if self.sounds_enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # Ignore sound errors during gameplay


class GPIOManager:
    """Handles GPIO input for touch sensor."""
    
    def __init__(self):
        self.gpio_available = GPIO_AVAILABLE
        self.last_press_time = 0
        
        if self.gpio_available:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                print(f"GPIO initialized. Touch sensor on pin {GPIO_PIN}")
            except Exception as e:
                print(f"Warning: GPIO setup failed: {e}")
                self.gpio_available = False
        else:
            print("Using keyboard controls: SPACE or UP arrow to jump")
    
    def is_pressed(self) -> bool:
        """Check if touch sensor is pressed (with debouncing)."""
        current_time = time.time()
        
        if self.gpio_available:
            try:
                # GPIO.LOW means button is pressed (active LOW with pull-up)
                if GPIO.input(GPIO_PIN) == GPIO.LOW:
                    if current_time - self.last_press_time > DEBOUNCE_TIME:
                        self.last_press_time = current_time
                        return True
            except Exception as e:
                print(f"GPIO read error: {e}")
                return False
        
        return False
    
    def cleanup(self):
        """Clean up GPIO resources."""
        if self.gpio_available:
            try:
                GPIO.cleanup()
            except:
                pass


class Game:
    """Main game class that handles the game loop and logic."""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Raspberry Pi Flappy Bird")
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.sound_manager = SoundManager()
        self.gpio_manager = GPIOManager()
        
        # Game state
        self.reset_game()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        print("Game initialized successfully!")
        print("Controls: Touch sensor on GPIO 2 (or SPACE/UP arrow key)")
    
    def reset_game(self):
        """Reset game state for new game."""
        self.bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.pipes: List[Pipe] = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        
        # Create initial pipes
        self.pipe_timer = 0
        self.pipe_interval = 120  # Frames between pipes
    
    def handle_input(self) -> bool:
        """Handle all input events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key in [pygame.K_SPACE, pygame.K_UP]:
                    self.handle_jump()
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        
        # Check GPIO input
        if self.gpio_manager.is_pressed():
            self.handle_jump()
        
        return True
    
    def handle_jump(self):
        """Handle jump input."""
        if not self.game_over:
            if not self.game_started:
                self.game_started = True
            
            self.bird.jump()
            self.sound_manager.play('jump')
    
    def update_pipes(self):
        """Update pipe positions and create new pipes."""
        if not self.game_started or self.game_over:
            return
        
        # Update existing pipes
        for pipe in self.pipes[:]:  # Use slice copy to avoid modification during iteration
            pipe.update()
            
            # Check if pipe is passed for scoring
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                self.sound_manager.play('score')
            
            # Remove off-screen pipes
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
        
        # Create new pipes
        self.pipe_timer += 1
        if self.pipe_timer >= self.pipe_interval:
            self.pipe_timer = 0
            gap_y = random.randint(PIPE_GAP // 2 + 50, SCREEN_HEIGHT - PIPE_GAP // 2 - 50)
            self.pipes.append(Pipe(SCREEN_WIDTH, gap_y))
    
    def check_collisions(self):
        """Check for collisions and game over conditions."""
        if not self.game_started or self.game_over:
            return
        
        bird_rect = self.bird.get_rect()
        
# Check screen boundaries
        if self.bird.y <= 0:
            self.bird.y = 0
            self.bird.velocity = 0  # stop it from going higher
        elif self.bird.y >= SCREEN_HEIGHT:
            self.end_game()
            return

        # Check pipe collisions
        for pipe in self.pipes:
            if pipe.collides_with(bird_rect):
                self.end_game()
                return
    
    def end_game(self):
        """End the current game."""
        self.game_over = True
        self.sound_manager.play('collision')
    
    def update(self):
        """Update all game objects."""
        if self.game_started and not self.game_over:
            self.bird.update()
        
        self.update_pipes()
        self.check_collisions()
    
    def draw_background(self):
        """Draw the game background."""
        # Sky blue background
        self.screen.fill(SKY_BLUE)
        
        # Draw simple clouds
        cloud_y = 80
        for x in range(-50, SCREEN_WIDTH + 100, 200):
            pygame.draw.circle(self.screen, WHITE, (x, cloud_y), 30, 0)
            pygame.draw.circle(self.screen, WHITE, (x + 25, cloud_y), 35, 0)
            pygame.draw.circle(self.screen, WHITE, (x + 50, cloud_y), 30, 0)
        
        # Draw ground
        ground_height = 50
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - ground_height, SCREEN_WIDTH, ground_height)
        pygame.draw.rect(self.screen, GREEN, ground_rect)
        pygame.draw.rect(self.screen, DARK_GREEN, ground_rect, 3)
    
    def draw_ui(self):
        """Draw user interface elements."""
        # Draw score
        score_text = self.font_large.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, 10)
        
        # Add background for better readability
        bg_rect = score_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, BLACK, bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
        self.screen.blit(score_text, score_rect)
        
        if not self.game_started:
            # Start screen
            title_text = self.font_large.render("Flappy Bird - Pi Edition", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            
            instruction_text = self.font_medium.render("Touch sensor or press SPACE to start!", True, WHITE)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            
            # Draw backgrounds
            title_bg = title_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, BLACK, title_bg)
            pygame.draw.rect(self.screen, WHITE, title_bg, 3)
            
            instruction_bg = instruction_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, BLACK, instruction_bg)
            pygame.draw.rect(self.screen, WHITE, instruction_bg, 3)
            
            self.screen.blit(title_text, title_rect)
            self.screen.blit(instruction_text, instruction_rect)
            
        elif self.game_over:
            # Game over screen
            game_over_text = self.font_large.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            restart_text = self.font_medium.render("Press R to restart or ESC to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            
            # Draw backgrounds
            for text, rect in [(game_over_text, game_over_rect), 
                             (final_score_text, final_score_rect),
                             (restart_text, restart_rect)]:
                bg = rect.inflate(40, 20)
                pygame.draw.rect(self.screen, BLACK, bg)
                pygame.draw.rect(self.screen, WHITE, bg, 3)
                self.screen.blit(text, rect)
    
    def draw(self):
        """Draw everything on the screen."""
        self.draw_background()
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        print("Starting game loop...")
        running = True
        
        try:
            while running:
                running = self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(FPS)
                
        except KeyboardInterrupt:
            print("\nGame interrupted by user")
        except Exception as e:
            print(f"Game error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up...")
        self.gpio_manager.cleanup()
        pygame.quit()


def main():
    """Main function to start the game."""
    print("=" * 50)
    print("Raspberry Pi Flappy Bird Game")
    print("=" * 50)
    print("Hardware: Touch sensor on GPIO 2")
    print("Keyboard: SPACE or UP arrow to jump")
    print("ESC to quit, R to restart after game over")
    print("=" * 50)
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Failed to start game: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
