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
pygame.display.set_caption("Tank Attack")

# Set custom game icon
icon = pygame.image.load("User.png")
pygame.display.set_icon(icon)

background_img = pygame.image.load("Background.png").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
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
coin_image = pygame.transform.scale(pygame.image.load("Coin.png").convert_alpha(), (60, 60))

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
        self.rect.x -= 1
        if self.airborne:
            self.timer += 1
            self.rect.y = self.base_y + int(10 * math.sin(self.timer * 0.1))
        if self.rect.right < 0:
            self.kill()

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        if kind == 'coin':
            self.image = coin_image
        else:
            self.image = pygame.image.load("Health_Pack.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))
        self.kind = kind
        self.timer = 0
        self.base_y = y

    def update(self):
        self.rect.x -= 1
        if self.kind == 'coin':
            self.timer += 1
            self.rect.y = self.base_y + int(5 * math.sin(self.timer * 0.2))
        if self.rect.right < 0:
            self.kill()

def show_start_screen():
    screen.fill((0, 0, 0))
    title_font = pygame.font.SysFont(None, 72)
    title = title_font.render("Tank Attack", True, YELLOW)
    instr1 = font.render("Use LEFT and RIGHT arrows to move", True, WHITE)
    instr2 = font.render("Press SPACE to jump", True, WHITE)
    instr3 = font.render("Press Z to shoot", True, WHITE)
    instr4 = font.render("Press ENTER or S to start", True, WHITE)

    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    screen.blit(instr1, (WIDTH//2 - instr1.get_width()//2, 220))
    screen.blit(instr2, (WIDTH//2 - instr2.get_width()//2, 260))
    screen.blit(instr3, (WIDTH//2 - instr3.get_width()//2, 300))
    screen.blit(instr4, (WIDTH//2 - instr4.get_width()//2, 360))
    pygame.display.update(pygame.Rect(0, 0, WIDTH, HEIGHT))

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_s:
                    waiting = False

def run_game():
    show_start_screen()

    player = Player()
    player_group = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()

    level = 1
    background_x = 0
    standard_enemies_cleared = False
    mini_boss_spawned = False
    mega_boss_spawned = False
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        screen.blit(background_img, (background_x, 0))
        screen.blit(background_img, (background_x + background_img.get_width(), 0))
        background_x -= 1
        if background_x <= -background_img.get_width():
            background_x = 0

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                bullets.add(player.shoot())

        elapsed = pygame.time.get_ticks() - start_time

        if not standard_enemies_cleared and elapsed < 15000:
            if random.randint(1, 60) == 1:
                enemies.add(Enemy(WIDTH, HEIGHT - 80))
        elif not standard_enemies_cleared and elapsed >= 15000 and len(enemies) == 0:
            standard_enemies_cleared = True
            start_time = pygame.time.get_ticks()

        elif standard_enemies_cleared and not mini_boss_spawned:
            if len(enemies) == 0:
                enemies.add(Enemy(WIDTH, HEIGHT - 150, image=mini_boss_image, health=188))
                mini_boss_spawned = True

        elif mini_boss_spawned and not mega_boss_spawned and level % 3 == 0:
            if len(enemies) == 0:
                enemies.add(Enemy(WIDTH + 100, HEIGHT - 150, image=mega_boss_image, health=450))
                mega_boss_spawned = True

        elif mini_boss_spawned and ((level % 3 != 0 and not any(e.health > 0 for e in enemies)) or (level % 3 == 0 and mega_boss_spawned and not any(e.health > 0 for e in enemies))):
            if level >= 1:
                pygame.time.delay(350)
                screen.fill((0, 0, 0))
                level_font = pygame.font.SysFont(None, 72)
                level_text = level_font.render(f"Level {level + 1}", True, YELLOW)
                screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))
                pygame.display.update()
                pygame.time.delay(1000)
            level += 1
            start_time = pygame.time.get_ticks()
            standard_enemies_cleared = False
            mini_boss_spawned = False
            mega_boss_spawned = False

        if pygame.time.get_ticks() % 320 == 0:
            collectibles.add(Collectible(WIDTH, HEIGHT - 60, 'coin'))

        if pygame.time.get_ticks() % 800 == 0:
            collectibles.add(Collectible(WIDTH, HEIGHT - 60, 'health'))
            collectibles.add(Collectible(WIDTH, HEIGHT - 60, 'coin'))

        bullets.update()
        player.update(keys)
        enemies.update()
        collectibles.update()

        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hits:
                enemy.health -= 25
                bullet.kill()
                if enemy.health <= 0:
                    enemy.kill()
                    player.score += 10

        if pygame.sprite.spritecollide(player, enemies, False):
            hit_sound.play()
            player.health -= 1
            if player.health <= 0:
                player.lives -= 1
                player.health = 100
                if player.lives <= 0:
                    while True:
                        screen.fill((0, 0, 0))
                        game_over_text = font.render("GAME OVER", True, RED)
                        restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
                        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 30))
                        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
                        pygame.display.flip()

                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    return run_game()
                                elif event.key == pygame.K_q:
                                    pygame.quit()
                                    sys.exit()

        for item in pygame.sprite.spritecollide(player, collectibles, True):
            if item.kind == 'health':
                player.health = min(player.health + 30, 100)
            elif item.kind == 'life':
                player.lives += 1
            elif item.kind == 'coin':
                player.score += 5
                player.coins += 1

        player_group.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)
        collectibles.draw(screen)

        screen.blit(font.render(f"Score: {player.score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Coins: {player.coins}", True, WHITE), (10, 40))
        screen.blit(font.render(f"Health: {player.health}", True, WHITE), (10, 70))
        screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (10, 100))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 130))

        pygame.display.flip()
        clock.tick(60)

run_game()
pygame.quit()
