#author Ari
#8.23.25
# v 1.0

import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (148, 0, 211)
PINK = (255, 20, 147)
GOLD = (255, 215, 0)
Dark_Green = (22, 122, 61)

# Rainbow colors for snake segments
RAINBOW_COLORS = [
    (255, 0, 0),    # Red
    (255, 127, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (75, 0, 130),   # Indigo
    (148, 0, 211),  # Violet
]

class Butterfly:
    def __init__(self):
        self.x = random.randint(50, WINDOW_SIZE - 50)
        self.y = random.randint(50, WINDOW_SIZE - 50)
        self.angle = 0
        self.wing_beat = 0
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)

    def update(self):
        # Smooth floating movement
        self.angle += 0.05
        self.wing_beat += 0.3

        # Move butterfly
        self.x += self.dx + math.sin(self.angle) * 0.5
        self.y += self.dy + math.cos(self.angle) * 0.3

        # Bounce off walls
        if self.x <= 20 or self.x >= WINDOW_SIZE - 20:
            self.dx *= -1
        if self.y <= 20 or self.y >= WINDOW_SIZE - 20:
            self.dy *= -1

        # Keep in bounds
        self.x = max(20, min(WINDOW_SIZE - 20, self.x))
        self.y = max(20, min(WINDOW_SIZE - 20, self.y))

    def draw(self, screen):
        # Wing beat animation
        wing_size = 12 + 4 * math.sin(self.wing_beat)

        # Body
        pygame.draw.ellipse(screen, BLACK, (self.x - 2, self.y - 8, 4, 16))

        # Wings with gradient effect
        wing_colors = [(PURPLE, PINK), (PINK, GOLD)]

        for i, (color1, color2) in enumerate(wing_colors):
            # Upper wings
            wing_offset = (-1) ** i * wing_size
            upper_wing = [
                (self.x + wing_offset, self.y - 5),
                (self.x + wing_offset * 1.5, self.y - 12),
                (self.x + wing_offset * 0.7, self.y - 2)
            ]
            pygame.draw.polygon(screen, color1, upper_wing)

            # Lower wings
            lower_wing = [
                (self.x + wing_offset * 0.8, self.y + 2),
                (self.x + wing_offset * 1.2, self.y + 8),
                (self.x + wing_offset * 0.5, self.y + 5)
            ]
            pygame.draw.polygon(screen, color2, lower_wing)

        # Antennae
        pygame.draw.line(screen, BLACK, (self.x - 1, self.y - 8),
                        (self.x - 3, self.y - 12), 1)
        pygame.draw.line(screen, BLACK, (self.x + 1, self.y - 8),
                        (self.x + 3, self.y - 12), 1)

class Snake:
    def __init__(self):
        self.positions = [(GRID_COUNT//2, GRID_COUNT//2)]
        self.direction = (1, 0)
        self.grow = False

    def move(self):
        head = self.positions[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_COUNT or
            new_head[1] < 0 or new_head[1] >= GRID_COUNT):
            return False

        # Check self collision
        if new_head in self.positions:
            return False

        self.positions.insert(0, new_head)

        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False

        return True

    def change_direction(self, new_direction):
        # Prevent reversing into self
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def eat_food(self):
        self.grow = True

    def draw(self, screen):
        for i, pos in enumerate(self.positions):
            # Use rainbow colors, cycling through them
            color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]

            # brightness variation
            brightness = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01 + i)
            color = tuple(int(c * brightness) for c in color)

            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE,
                             GRID_SIZE - 1, GRID_SIZE - 1)
            pygame.draw.rect(screen, color, rect, border_radius=3)

class Food:
    def __init__(self, snake_positions):
        self.respawn(snake_positions)

    def respawn(self, snake_positions):
        while True:
            self.position = (random.randint(0, GRID_COUNT-1),
                           random.randint(0, GRID_COUNT-1))
            if self.position not in snake_positions:
                break

    def draw(self, screen):
        # Pulsing food effect
        pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.008)
        size = int(GRID_SIZE * pulse)
        offset = (GRID_SIZE - size) // 2

        rect = pygame.Rect(self.position[0] * GRID_SIZE + offset,
                          self.position[1] * GRID_SIZE + offset,
                          size, size)
        pygame.draw.ellipse(screen, RED, rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Rainbow Snake - Butterfly Hatching")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.huge_font = pygame.font.Font(None, 96)

        # Load sounds (create simple beep sounds programmatically)
        self.create_sounds()

        # Load and play background music
        self.load_background_music()

        self.reset_game()

    def create_sounds(self):
        """Create simple sound effects programmatically"""
        try:
            # Create a simple eating sound (ascending notes)
            sample_rate = 22050
            duration = 0.2
            t = []
            for i in range(int(sample_rate * duration)):
                frequency = 440 * (1 + i / sample_rate)
                wave = 4096 * math.sin(2 * math.pi * frequency * i / sample_rate)
                t.append(int(wave))

            sound_array = pygame.array.array('h', t)
            self.eat_sound = pygame.sndarray.make_sound(sound_array)
            self.eat_sound.set_volume(0.3)

        except:
            # Fallback Sound
            self.eat_sound = None

    def load_background_music(self):
        """Load and start background music"""
        try:
            # load music file
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

        except pygame.error:
            # If no music file found,
            print("No background_music.mp3 found. Add your MP3 file to enable music!")
    def play_eat_sound(self):
        """Play the eating sound effect"""
        if self.eat_sound:
            self.eat_sound.play()

    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()

    def pause_music(self):
        """Pause/unpause background music"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        """Play the eating sound effect"""
        if self.eat_sound:
            self.eat_sound.play()

    def reset_game(self):
        self.snake = Snake()
        self.food = Food(self.snake.positions)
        self.butterfly = None
        self.score = 0
        self.game_over = False
        self.game_state = "welcome"  # welcome, playing, hatched, game_over
        self.hatched = False
        self.hatch_time = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "welcome":
                    if event.key == pygame.K_SPACE:
                        self.game_state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        return False
                elif self.game_state == "hatched":
                    if event.key == pygame.K_SPACE:
                        self.game_state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        return False
                elif self.game_state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                elif self.game_state == "playing":
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.snake.change_direction((0, -1))
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, 1))
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.snake.change_direction((1, 0))
                    elif event.key == pygame.K_m:
                        self.pause_music()  # Toggle music with M key
        return True

    def update(self):
        if self.game_state == "playing" and not self.game_over:
            if not self.snake.move():
                self.game_over = True
                self.game_state = "game_over"
                return

            # Check food collision
            if self.snake.positions[0] == self.food.position:
                self.snake.eat_food()
                self.score += 10
                self.play_eat_sound()  # Play sound when eating
                self.food.respawn(self.snake.positions)

                # Check if butterfly should hatch
                if self.score >= 200 and not self.hatched:
                    self.hatched = True
                    self.game_state = "hatched"
                    self.hatch_time = pygame.time.get_ticks()
                    self.butterfly = Butterfly()

            # Update butterfly if it exists
            if self.butterfly:
                self.butterfly.update()

        # Handle hatched screen timing
        if self.game_state == "hatched":
            if pygame.time.get_ticks() - self.hatch_time > 3000:  # 3 seconds
                self.game_state = "playing"

    def draw(self):
        self.screen.fill(Dark_Green)

        if self.game_state == "welcome":
            # Welcome Screen
            title_text = self.big_font.render("Hungry Hungry Caterpillar", True, WHITE)
            subtitle_text = self.font.render("Reach 200 points to hatch a butterfly!", True, GOLD)
            controls_text1 = self.font.render("Controls: WASD or Arrow Keys", True, WHITE)
            start_text = self.font.render("Press SPACE to start", True, GREEN)
            quit_text = self.font.render("Press ESC to quit", True, WHITE)

            #rainbow snake preview
            for i in range(7):
                color = RAINBOW_COLORS[i]
                brightness = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01 + i)
                color = tuple(int(c * brightness) for c in color)

                x = WINDOW_SIZE//2 - 140 + i * 40
                y = WINDOW_SIZE//2 - 80
                rect = pygame.Rect(x, y, 35, 35)
                pygame.draw.rect(self.screen, color, rect, border_radius=5)

            # Center text
            title_rect = title_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 150))
            subtitle_rect = subtitle_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 30))
            controls_rect1 = controls_text1.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 40))
            start_rect = start_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 100))
            quit_rect = quit_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 140))

            self.screen.blit(title_text, title_rect)
            self.screen.blit(subtitle_text, subtitle_rect)
            self.screen.blit(controls_text1, controls_rect1)
            self.screen.blit(start_text, start_rect)
            self.screen.blit(quit_text, quit_rect)

        elif self.game_state == "hatched":
            # Hatching celebration screen
            # Animated background
            for i in range(20):
                color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
                brightness = 0.3 + 0.3 * math.sin(pygame.time.get_ticks() * 0.02 + i)
                color = tuple(int(c * brightness) for c in color)

                size = 30 + 20 * math.sin(pygame.time.get_ticks() * 0.015 + i * 0.5)
                x = (i * 50 + pygame.time.get_ticks() * 0.1) % (WINDOW_SIZE + 100) - 50
                y = 100 + 50 * math.sin(i * 0.8)

                pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))

            # Main text
            hatch_text = self.huge_font.render("YOU HAVE", True, GOLD)
            hatch_text2 = self.huge_font.render("HATCHED!", True, PURPLE)
            score_text = self.big_font.render(f"Score: {self.score}", True, WHITE)
            continue_text = self.font.render("Press SPACE to continue playing", True, WHITE)

            # Butterfly animation in center
            if self.butterfly:
                temp_butterfly = Butterfly()
                temp_butterfly.x = WINDOW_SIZE // 2
                temp_butterfly.y = WINDOW_SIZE // 2 + 50
                temp_butterfly.wing_beat = pygame.time.get_ticks() * 0.02
                temp_butterfly.draw(self.screen)

            # Center text
            hatch_rect = hatch_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 120))
            hatch_rect2 = hatch_text2.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 60))
            score_rect = score_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 120))
            continue_rect = continue_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 170))

            self.screen.blit(hatch_text, hatch_rect)
            self.screen.blit(hatch_text2, hatch_rect2)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(continue_text, continue_rect)

        elif self.game_state == "playing":
            self.snake.draw(self.screen)
            self.food.draw(self.screen)

            # Draw butterfly if hatched
            if self.butterfly:
                self.butterfly.draw(self.screen)

            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            # Show progress to hatching
            if not self.hatched:
                progress_text = self.font.render(f"Hatch at: {200 - self.score} points left", True, GOLD)
                self.screen.blit(progress_text, (10, 50))
            else:
                hatched_text = self.font.render("🦋 Butterfly Hatched! 🦋", True, PURPLE)
                self.screen.blit(hatched_text, (10, 50))

        elif self.game_state == "game_over":
            # Game Over Screen
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)

            if self.hatched:
                achievement_text = self.font.render("🦋 You hatched a butterfly! 🦋", True, GOLD)
            else:
                achievement_text = self.font.render(f"Reach 200 points to hatch! ({self.score}/200)", True, WHITE)

            restart_text = self.font.render("Press SPACE to restart", True, WHITE)
            quit_text = self.font.render("Press ESC to quit", True, WHITE)

            # Center the text
            go_rect = game_over_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 80))
            score_rect = score_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 30))
            achievement_rect = achievement_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 10))
            restart_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 50))
            quit_rect = quit_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 90))

            self.screen.blit(game_over_text, go_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(achievement_text, achievement_rect)
            self.screen.blit(restart_text, restart_rect)
            self.screen.blit(quit_text, quit_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
