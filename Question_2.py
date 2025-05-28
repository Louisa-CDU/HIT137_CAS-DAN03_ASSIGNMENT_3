# Auto-install required libraries if missing
import subprocess
import sys

required_modules = ["pygame", "random"]
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
pygame.display.set_caption("Tank Battle")
background_img = pygame.image.load("Background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
background_x = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load sounds
hit_sound = pygame.mixer.Sound("hit.wav")
jump_sound = pygame.mixer.Sound("jump.wav")
shoot_sound = pygame.mixer.Sound("tank-fire.wav")
pickup_sound = pygame.mixer.Sound("item-pickup.wav")

try:
    pygame.mixer.music.load("1812-overture-finale.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Background music file not found.")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

GRAVITY = 1

# Load enemy images
enemy_images = [
    pygame.transform.scale(pygame.image.load("Enemy_1.png").convert_alpha(), (80, 80)),
    pygame.transform.scale(pygame.image.load("Enemy_2.png").convert_alpha(), (80, 80))
]
mini_boss_image = pygame.transform.scale(pygame.image.load("Mini_Boss.png").convert_alpha(), (150, 150))
mega_boss_image = pygame.transform.scale(pygame.image.load("Mega_Boss.png").convert_alpha(), (180, 180))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_image = pygame.image.load("User.png").convert_alpha()
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
        speed = 2.5
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed = 4
        if keys[pygame.K_LEFT]:
            dx = -speed
        if keys[pygame.K_RIGHT]:
            dx = speed

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -20
            jump_sound.play()

        self.rect.x += dx

    def shoot(self):
        shoot_sound.play()
        y = self.rect.top + self.rect.height // 2.5
        return Bullet(self.rect.centerx + 30, int(y))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, airborne=False, image=None, health=50):
        super().__init__()
        self.image = image or random.choice(enemy_images)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = health
        self.airborne = airborne
        self.base_y = y
        self.timer = 0

    def update(self):
        self.rect.x -= enemy_speed
        if self.airborne:
            self.timer += 1
            self.rect.y = self.base_y + int(10 * math.sin(self.timer * 0.1))
        if self.rect.right < 0:
            self.kill()

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.image = pygame.image.load("Health_Pack.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))
        self.kind = kind
        self.timer = 0
        self.base_y = y

    def update(self):
        self.rect.x -= collectible_speed
        if self.kind == 'coin':
            self.timer += 1
            self.rect.y = self.base_y + int(5 * math.sin(self.timer * 0.2))
        if self.rect.right < 0:
            self.kill()

# Game setup
player = Player()
player_group = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()
missiles = pygame.sprite.Group()

scroll_speed = 1
enemy_speed = 1
collectible_speed = 1

start_time = pygame.time.get_ticks()
level = 1
level_message_time = 0
level_message_duration = 3000
mega_boss_spawned = False
next_enemy_spawn_time = 0
next_health_spawn_time = 0

running = True
while running:
    screen.blit(background_img, (background_x, 0))
    screen.blit(background_img, (background_x + background_img.get_width(), 0))
    background_x -= scroll_speed
    if background_x <= -background_img.get_width():
        background_x = 0

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            bullets.add(player.shoot())

    elapsed_time = pygame.time.get_ticks() - start_time
    if elapsed_time > 10000 * level:
        level += 1
        level_message_time = pygame.time.get_ticks()
        scroll_speed += 1
        enemy_speed += 1
        collectible_speed += 1

    # Spawn a single enemy at a time
    if pygame.time.get_ticks() > next_enemy_spawn_time and len(enemies) < 1:
        y_pos = HEIGHT - 80
        enemies.add(Enemy(WIDTH, y_pos))
        next_enemy_spawn_time = pygame.time.get_ticks() + 4000  # 1 every 4 seconds

    # Spawn Mini Boss
    if elapsed_time >= 29900 and not any(e.health > 100 for e in enemies) and not mega_boss_spawned:
        mini_boss = Enemy(WIDTH, HEIGHT - 150, image=mini_boss_image, health=200)
        mini_boss.rect = mini_boss.image.get_rect(midbottom=(WIDTH, HEIGHT))
        enemies.add(mini_boss)

    # Spawn Mega Boss at every 3rd level if Mini Boss defeated
    if level % 3 == 0 and not any(e.health > 100 for e in enemies) and not mega_boss_spawned:
        mega_boss = Enemy(WIDTH + 100, HEIGHT - 180, image=mega_boss_image, health=300)
        mega_boss.rect = mega_boss.image.get_rect(midbottom=(WIDTH + 100, HEIGHT))
        enemies.add(mega_boss)
        mega_boss_spawned = True

    if mega_boss_spawned and not any(e.health > 100 for e in enemies):
        mega_boss_spawned = False

    # Health pack frequency reduced
    if pygame.time.get_ticks() > next_health_spawn_time:
        if random.random() < 0.5:
            kind = random.choice(['health', 'life'])
            y_pos = random.choice([HEIGHT - 60, HEIGHT - 150])
            collectibles.add(Collectible(WIDTH, y_pos, kind))
        next_health_spawn_time = pygame.time.get_ticks() + 24000

    # Coins appear regularly
    if pygame.time.get_ticks() % 1800 < 20:
        collectibles.add(Collectible(WIDTH, HEIGHT - 60, 'coin'))

    # Update groups
    bullets.update()
    player.update(keys)
    enemies.update()
    collectibles.update()

    # Bullet collision with enemies
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, enemies, False)
        for enemy in hits:
            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                enemy.kill()
                player.score += 10

    # Player collision with enemies
    if pygame.sprite.spritecollide(player, enemies, False):
        hit_sound.play()
        player.health -= 1
        if player.health <= 0:
            player.lives -= 1
            player.health = 100

    # Player collision with collectibles
    for item in pygame.sprite.spritecollide(player, collectibles, True):
        if item.kind == 'health':
            player.health = min(player.health + 30, 100)
        elif item.kind == 'life':
            player.lives += 1
        elif item.kind == 'coin':
            player.score += 5
            player.coins += 1

    # Draw everything
    player_group.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)
    collectibles.draw(screen)

    screen.blit(font.render(f"Score: {player.score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Coins: {player.coins}", True, WHITE), (10, 40))
    screen.blit(font.render(f"Health: {player.health}", True, WHITE), (10, 70))
    screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (10, 100))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 130))

    if 0 < pygame.time.get_ticks() - level_message_time < level_message_duration:
        msg = font.render(f"Level {level}", True, YELLOW)
        rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(msg, rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
