# Auto-install required libraries if missing
import subprocess
import sys

required_modules = ["pygame", "random", "math"]
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

import pygame
import random
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Attack")

try:
    background_img = pygame.image.load("bg.jpg").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except pygame.error:
    print("Failed to load background image.")
    pygame.quit()
    sys.exit()

background_x = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load sounds with basic file handling
try:
    hit_sound = pygame.mixer.Sound("hit.wav")
    jump_sound = pygame.mixer.Sound("jump.wav")
    shoot_sound = pygame.mixer.Sound("shoot.wav")
except pygame.error:
    print("Failed to load sound files.")
    pygame.quit()
    sys.exit()

# Colours
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

GRAVITY = 1

def show_start_screen():
    """Display the initial start screen with controls and title."""
    screen.fill((0, 0, 0))
    title_font = pygame.font.SysFont(None, 72)
    screen.blit(title_font.render("Zombie Attack", True, YELLOW), (WIDTH//2 - 180, 100))
    for i, text in enumerate(["Use LEFT and RIGHT arrows to move", "Press SPACE to jump", "Press Z to shoot", "Press ENTER or S to start"]):
        screen.blit(font.render(text, True, WHITE), (WIDTH//2 - 180, 220 + i * 40))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_s]:
                    waiting = False

def game_over_menu():
    """Display the game over menu with restart/quit options."""
    while True:
        screen.fill((0, 0, 0))
        msg = font.render("GAME OVER - Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: main()
                elif event.key == pygame.K_q: pygame.quit(); exit()

def victory_menu():
    """Display the victory menu with restart/quit options."""
    while True:
        screen.fill((0, 0, 0))
        msg = font.render("VICTORY - Press R to Restart or Q to Quit", True, YELLOW)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: main()
                if event.key == pygame.K_q: pygame.quit(); exit()

class Player(pygame.sprite.Sprite):
    """Handles the player character: movement, jumping, shooting, and status."""
    def __init__(self):
        super().__init__()
        try:
            self.base_image = pygame.image.load("girl.png").convert_alpha()
        except pygame.error:
            print("Failed to load player image.")
            pygame.quit(); sys.exit()
        self.base_image = pygame.transform.scale(self.base_image, (100, 100))
        self.image = self.base_image
        self.rect = self.image.get_rect(midbottom=(100, HEIGHT - 50))
        self.vel_y = 0
        self.health = 100
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.on_ground = False

    def update(self, keys):
        dx = 0
        speed = 8 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 5
        if keys[pygame.K_LEFT]: dx = -speed
        if keys[pygame.K_RIGHT]: dx = speed
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_ground = self.rect.bottom >= HEIGHT
        if self.on_ground:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -20
            jump_sound.play()
        self.rect.x += dx
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

    def shoot(self):
        shoot_sound.play()
        return Projectile(self.rect.centerx + 30, int(self.rect.top + self.rect.height / 2.5))

class Projectile(pygame.sprite.Sprite):
    """Represents projectiles shot by the player."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 50

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    """Enemy class for standard and boss enemies."""
    def __init__(self, x, y, is_boss=False):
        super().__init__()
        img_file = "big_zombie.png" if is_boss else "zombie_girl.png"
        try:
            self.image = pygame.image.load(img_file).convert_alpha()
        except pygame.error:
            print(f"Failed to load {img_file}")
            pygame.quit(); sys.exit()
        scale = (200, 200) if is_boss else (80, 80)
        self.image = pygame.transform.scale(self.image, scale)
        if is_boss:
            self.rect = self.image.get_rect(midbottom=(x, HEIGHT))
        else:
            self.rect = self.image.get_rect(topleft=(x, y))

        self.health = 100 if is_boss else 50

    def update(self):
        self.rect.x -= enemy_speed
        if self.rect.right < 0:
            self.kill()

class Collectible(pygame.sprite.Sprite):
    """Handles coins and health/life pickups."""
    def __init__(self, x, y, kind):
        super().__init__()
        file = "Coin.png" if kind == 'coin' else "Health.png"
        try:
            self.image = pygame.image.load(file).convert_alpha()
        except pygame.error:
            print(f"Failed to load collectible: {file}")
            pygame.quit(); sys.exit()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.kind = kind
        self.base_y = y
        self.timer = 0

    def update(self):
        self.rect.x -= collectible_speed
        if self.kind == 'coin':
            self.timer += 1
            self.rect.y = self.base_y + int(5 * math.sin(self.timer * 0.2))
        if self.rect.right < 0:
            self.kill()

def spawn_regular_enemy(enemies):
    if random.randint(1, 100) <= 2:
        enemies.add(Enemy(WIDTH, HEIGHT - 80))

def spawn_boss(enemies, elapsed_time, last_spawn):
    if elapsed_time - last_spawn >= 20000:
        boss = Enemy(WIDTH, HEIGHT - 150, is_boss=True)
        enemies.add(boss)
        return elapsed_time
    return last_spawn

def spawn_collectibles(collectibles):
    if pygame.time.get_ticks() % 12000 < 20:
        y = random.choice([HEIGHT - 60, HEIGHT - 150, HEIGHT - 200])
        collectibles.add(Collectible(WIDTH, y, 'health'))
    if pygame.time.get_ticks() % 8000 < 20:
        y = random.choice([HEIGHT - 60, HEIGHT - 150, HEIGHT - 200])
        collectibles.add(Collectible(WIDTH, y, 'coin'))

show_start_screen()

def main():
    global enemy_speed, collectible_speed
    player = Player()
    player_group = pygame.sprite.Group(player)
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    fireballs = pygame.sprite.Group()
    scroll_speed = 2
    enemy_speed = 2
    collectible_speed = 2
    start_time = pygame.time.get_ticks()
    level = 1
    level_message_time = 0
    level_message_duration = 3000
    background_x = 0
    last_boss_spawn_time = 0
    running = True

    while running:
        screen.blit(background_img, (background_x, 0))
        screen.blit(background_img, (background_x + background_img.get_width(), 0))
        background_x = (background_x - scroll_speed) % -background_img.get_width()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                projectiles.add(player.shoot())

        elapsed = pygame.time.get_ticks() - start_time

        if elapsed > 10000 * level and level < 3:
            level += 1
            level_message_time = pygame.time.get_ticks()
            scroll_speed *= 1.7
            enemy_speed *= 1.7
            collectible_speed *= 1.7

        spawn_regular_enemy(enemies)
        last_boss_spawn_time = spawn_boss(enemies, elapsed, last_boss_spawn_time)
        spawn_collectibles(collectibles)

        player.update(keys)
        projectiles.update()
        enemies.update()
        collectibles.update()
        fireballs.update()

        for projectile in projectiles:
            for enemy in pygame.sprite.spritecollide(projectile, enemies, False):
                enemy.health -= 25
                projectile.kill()
                if enemy.health <= 0:
                    enemy.kill()
                    player.score += 10

        if pygame.sprite.spritecollide(player, enemies, False):
            hit_sound.play()
            player.health -= 1
            if player.health <= 0:
                player.lives -= 1
                player.health = 100

        for item in pygame.sprite.spritecollide(player, collectibles, True):
            if item.kind == 'coin':
                player.score += 5
                player.coins += 1
            elif item.kind in ['health', 'life']:
                if player.health < 100:
                    player.health = min(player.health + 30, 100)
                else:
                    player.lives += 1

        player_group.draw(screen)
        projectiles.draw(screen)
        fireballs.draw(screen)
        enemies.draw(screen)
        collectibles.draw(screen)

        for fireball in pygame.sprite.spritecollide(player, fireballs, True):
            hit_sound.play()
            player.health -= 10
            if player.health <= 0:
                player.lives -= 1
                player.health = 100

        for label, value, ypos in [("Score", player.score, 10), ("Coins", player.coins, 40), ("Health", player.health, 70), ("Lives", player.lives, 100), ("Level", level, 130)]:
            screen.blit(font.render(f"{label}: {value}", True, WHITE), (10, ypos))

        time_left = max(0, 100000 - elapsed)
        screen.blit(pygame.font.SysFont(None, 72).render(f"{time_left // 1000}", True, WHITE), (WIDTH // 2 - 20, 50))

        if 0 < pygame.time.get_ticks() - level_message_time < level_message_duration:
            msg = pygame.font.SysFont(None, 72).render(f"Level {level}", True, YELLOW)
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))

        pygame.display.flip()
        clock.tick(60)

        if player.lives <= 0:
            game_over_menu()
            break
        if elapsed >= 100000:
            victory_menu()
            break

main()
pygame.quit()
