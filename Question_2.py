import pygame
import random

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
pygame.mixer.music.load('1812-overture-finale.wav')
pygame.mixer.music.play(-1)

# Sounds
shoot_sound = pygame.mixer.Sound('tank-fire.wav')
pickup_sound = pygame.mixer.Sound('item-pickup.wav')

# Background
background = pygame.Surface((1600, HEIGHT))
background.fill(BLUE)

# Draw Hills
pygame.draw.ellipse(background, DARK_GREEN, (0, HEIGHT-150, 400, 300))
pygame.draw.ellipse(background, DARK_GREEN, (300, HEIGHT-100, 500, 200))
pygame.draw.ellipse(background, DARK_GREEN, (800, HEIGHT-120, 600, 250))

# Draw Clouds
pygame.draw.ellipse(background, WHITE, (100, 100, 150, 80))
pygame.draw.ellipse(background, WHITE, (600, 80, 120, 60))
pygame.draw.ellipse(background, WHITE, (1100, 130, 180, 90))

# --- Classes ---

# (rest of the script remains the same)

# --- Start the Game ---
result = game_loop()
pygame.mixer.music.fadeout(2000)  # Fade out music over 2 seconds

# Fade to black after game over
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill(BLACK)
for alpha in range(0, 255, 5):
    fade_surface.set_alpha(alpha)
    screen.blit(fade_surface, (0, 0))
    pygame.display.update()
    pygame.time.delay(30)

game_over_screen(result)
