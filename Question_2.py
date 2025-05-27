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
import os

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load Background
background_img = pygame.image.load("Background.png").convert()
background_img = pygame.transform.scale(background_img, (2400, HEIGHT))

# Load Sprites with .convert_alpha()
player_img = pygame.transform.scale(pygame.image.load("User.png").convert_alpha(), (80, 80))
enemy_imgs = [
    pygame.transform.scale(pygame.image.load("Enemy 1.png").convert_alpha(), (70, 70)),
    pygame.transform.scale(pygame.image.load("Enemy 2.png").convert_alpha(), (70, 70))
]
mini_boss_img = pygame.transform.scale(pygame.image.load("Mini Boss.png").convert_alpha(), (100, 100))
boss_img = pygame.transform.scale(pygame.image.load("Boss Tank.png").convert_alpha(), (130, 130))
health_pack_img = pygame.transform.scale(pygame.image.load("Health Pack.png").convert_alpha(), (40, 40))

# Placeholder heart icon
heart_img = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.polygon(heart_img, (255, 0, 0), [(15, 5), (25, 5), (30, 15), (15, 30), (0, 15), (5, 5)])

# Load Sounds
shoot_sound = pygame.mixer.Sound("tank-fire.wav")
hit_sound = pygame.mixer.Sound("hit.wav")
pickup_sound = pygame.mixer.Sound("item-pickup.wav")

try:
    pygame.mixer.music.load("1812-overture-finale.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error:
    print("Background music file not found.")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game Variables
scroll_x = 0
WORLD_WIDTH = 2400
victory_round = 5

score = 0
round_num = 1
total_kills = 0
kills_this_round = 0
volume_on = True
mini_boss_spawned = False
boss_spawned = False

power_ups = pygame.sprite.Group()
power_effects = {"speed": 0, "shield": 0, "damage": 0}

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(midbottom=(100, HEIGHT - 50))
        self.speed = 5
        self.health = 100
        self.lives = 3
        self.direction = 1

    def update(self, keys):
        global scroll_x
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 1
        if self.rect.x > WIDTH // 2 and scroll_x > -(WORLD_WIDTH - WIDTH):
            self.rect.x = WIDTH // 2
            scroll_x -= self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

    def shoot(self):
        x = self.rect.centerx + (self.direction * 40)
        y = self.rect.centery
        bullet = Bullet(x - scroll_x, y, self.direction)
        shoot_sound.play()
        return bullet

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10 * direction

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > WORLD_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, x, y, health=50, kind="regular"):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.health = health
        self.kind = kind

    def update(self):
        pass

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = health_pack_img
        self.rect = self.image.get_rect(center=(x, y))

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((30, 30))
        color = {"speed": (0,255,255), "shield": (255,255,0), "damage": (255,0,255)}[kind]
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

# Groups
player = Player()
player_group = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

# Spawn Functions
def spawn_enemies(round_num):
    global kills_this_round, mini_boss_spawned, boss_spawned
    kills_this_round = 0
    mini_boss_spawned = False
    boss_spawned = False
    enemies.empty()
    bullets.empty()
    collectibles.empty()
    base_x = WIDTH + 200
    for i in range(5 + round_num):
        x = base_x + i * 150
        enemy = Enemy(enemy_imgs[i % 2], x, HEIGHT - 50, 50, "regular")
        enemies.add(enemy)

def spawn_mini_boss():
    mini = Enemy(mini_boss_img, WIDTH * 2, HEIGHT - 50, 120, "mini_boss")
    enemies.add(mini)

def spawn_boss():
    boss = Enemy(boss_img, WIDTH * 2 + 200, HEIGHT - 50, 200, "boss")
    enemies.add(boss)

def show_start_screen():
    screen.fill(BLACK)
    lines = [
        "Tank Battle Game",
        "Use LEFT and RIGHT arrows to move",
        "Press SPACE to shoot",
        "Press M to mute/unmute music",
        "Press P to pause the game",
        "Press ENTER to start"
    ]
    for i, line in enumerate(lines):
        txt = font.render(line, True, WHITE)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 100 + i * 40))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: return

def pause_menu():
    screen.blit(font.render("Paused - Press R to Resume or Q to Quit", True, WHITE), (WIDTH//2 - 200, HEIGHT//2))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return
                if event.key == pygame.K_q: pygame.quit(); exit()

# Main Game Loop
def main():
    global score, round_num, total_kills, kills_this_round, volume_on, mini_boss_spawned, boss_spawned, scroll_x
    show_start_screen()
    running = True
    spawn_enemies(round_num)

    while running:
        clock.tick(60)
        screen.blit(background_img, (scroll_x, 0), area=pygame.Rect(-scroll_x, 0, WIDTH, HEIGHT))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: bullets.add(player.shoot())
                if event.key == pygame.K_m:
                    volume_on = not volume_on
                    pygame.mixer.music.set_volume(0.5 if volume_on else 0.0)
                if event.key == pygame.K_p: pause_menu()

        player.update(keys)
        bullets.update(); enemies.update(); collectibles.update(); power_ups.update()

        for group in [player_group, bullets, enemies, collectibles, power_ups]:
            for sprite in group:
                screen.blit(sprite.image, sprite.rect.move(scroll_x, 0))

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Round: {round_num}", True, WHITE), (10, 40))
        for i in range(player.lives): screen.blit(heart_img, (WIDTH - 35 * (i+1), 10))
        pygame.draw.rect(screen, (255, 0, 0), (10, 70, 100, 10))
        pygame.draw.rect(screen, (0, 255, 0), (10, 70, player.health, 10))

        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hits:
                dmg = 50 if power_effects["damage"] > 0 else 25
                enemy.health -= dmg
                bullet.kill(); hit_sound.play()
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 100; kills_this_round += 1

        for key in power_effects:
            if power_effects[key] > 0: power_effects[key] -= 1
        player.speed = 8 if power_effects["speed"] > 0 else 5

        if random.randint(0, 300) == 1:
            collectibles.add(Collectible(player.rect.x - scroll_x + random.randint(200, 600), HEIGHT - 60))
        if random.randint(0, 400) == 1:
            kind = random.choice(["speed", "damage", "shield"])
            power_ups.add(PowerUp(player.rect.x - scroll_x + random.randint(150, 500), HEIGHT - 80, kind))

        for p in pygame.sprite.spritecollide(player, power_ups, True): power_effects[p.kind] = 300
        for c in pygame.sprite.spritecollide(player, collectibles, True):
            player.health = min(100, player.health + 30); pickup_sound.play()

        for e in enemies:
            if e.kind in ["mini_boss", "boss"]:
                max_hp = 200 if e.kind == "boss" else 120
                pygame.draw.rect(screen, (255,0,0), (e.rect.x + scroll_x, e.rect.y - 10, 100, 5))
                pygame.draw.rect(screen, (0,255,0), (e.rect.x + scroll_x, e.rect.y - 10, 100 * (e.health / max_hp), 5))

        if not any(e.kind == "regular" for e in enemies) and not mini_boss_spawned:
            spawn_mini_boss(); mini_boss_spawned = True
        if mini_boss_spawned and not any(e.kind == "mini_boss" for e in enemies) and not boss_spawned:
            spawn_boss(); boss_spawned = True

        if not enemies:
            round_num += 1
            scroll_x = 0; player.rect.x = 100
            if round_num > victory_round:
                screen.fill(BLACK)
                screen.blit(font.render("VICTORY! Press R to Restart", True, WHITE), (WIDTH//2 - 160, HEIGHT//2))
                pygame.display.flip()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            round_num = 1; score = 0; player.health = 100
                            player.lives = 3; scroll_x = 0; player.rect.x = 100
                            spawn_enemies(round_num)
                            break
            else:
                spawn_enemies(round_num)

        if player.health <= 0:
            player.lives -= 1; player.health = 100
            if player.lives == 0:
                screen.blit(font.render("GAME OVER - Press R to Restart", True, WHITE), (WIDTH//2 - 160, HEIGHT//2))
                pygame.display.flip()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            round_num = 1; score = 0; player.health = 100
                            player.lives = 3; scroll_x = 0; player.rect.x = 100
                            spawn_enemies(round_num)
                            break

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
