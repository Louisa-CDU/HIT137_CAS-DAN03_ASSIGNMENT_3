import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
DARK_GREEN = (34, 139, 34)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Font
font = pygame.font.SysFont('Arial', 24)

# Background music
try:
    pygame.mixer.music.load('1812-overture-finale.wav')
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Warning: Background music file not found.")

# Sound effects
try:
    shoot_sound = pygame.mixer.Sound('tank-fire.wav')
except pygame.error:
    print("Warning: Shooting sound file not found.")
    shoot_sound = None

try:
    pickup_sound = pygame.mixer.Sound('item-pickup.wav')
except pygame.error:
    print("Warning: Pickup sound file not found.")
    pickup_sound = None

# Create a scrolling background
background = pygame.Surface((1600, HEIGHT))
background.fill(BLUE)
pygame.draw.ellipse(background, DARK_GREEN, (0, HEIGHT-150, 400, 300))
pygame.draw.ellipse(background, DARK_GREEN, (300, HEIGHT-100, 500, 200))
pygame.draw.ellipse(background, DARK_GREEN, (800, HEIGHT-120, 600, 250))
pygame.draw.ellipse(background, WHITE, (100, 100, 150, 80))
pygame.draw.ellipse(background, WHITE, (600, 80, 120, 60))
pygame.draw.ellipse(background, WHITE, (1100, 130, 180, 90))

# --- Classes ---

class Tank(pygame.sprite.Sprite):
    """Represents the player's tank."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 100
        self._speed = 5
        self._jump_power = 15
        self._gravity = 0.8
        self._vel_y = 0
        self._health = 100
        self._lives = 3

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self._speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self._speed
        if keys_pressed[pygame.K_SPACE] and self.on_ground():
            self._vel_y = -self._jump_power
        self._vel_y += self._gravity
        self.rect.y += self._vel_y
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self._vel_y = 0

    def shoot(self):
        if shoot_sound:
            shoot_sound.play()
        return Projectile(self.rect.right, self.rect.centery)

    def on_ground(self):
        return self.rect.bottom >= HEIGHT - 50

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = max(0, min(100, value))

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        self._lives = max(0, value)

class Projectile(pygame.sprite.Sprite):
    """Represents a projectile fired by the player."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > 1600:
            self.kill()

class EnemyTank(pygame.sprite.Sprite):
    """Represents a basic enemy tank."""
    def __init__(self, x, y, health=50):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(x=x, y=y)
        self.health = health
        self.direction = random.choice([-1, 1])
        self.speed = 2

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left <= 0 or self.rect.right >= 1600:
            self.direction *= -1

class BossTank(EnemyTank):
    """Represents a boss tank with more health and size."""
    def __init__(self, x, y):
        super().__init__(x, y, health=200)
        self.image = pygame.Surface((100, 60))
        self.image.fill((255, 0, 255))
        self.speed = 1

class Collectible(pygame.sprite.Sprite):
    """Represents a collectible item (health or life)."""
    def __init__(self, x, y, kind='health'):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0) if kind == 'health' else (255, 255, 0))
        self.rect = self.image.get_rect(x=x, y=y)
        self.kind = kind

# --- Utility Functions ---

def fade_to_black():
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)

def main():
    result = game_loop()
    pygame.mixer.music.fadeout(2000)
    fade_to_black()
    game_over_screen(result)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()
