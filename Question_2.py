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

# Clock
clock = pygame.time.Clock()
FPS = 60

# Font
font = pygame.font.SysFont('Arial', 24)

# --- Classes ---

class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 100
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        self.vel_y = 0
        self.health = 100
        self.lives = 3

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_SPACE] and self.on_ground():
            self.vel_y = -self.jump_power
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0

    def on_ground(self):
        return self.rect.bottom >= HEIGHT - 50

    def shoot(self):
        bullet = Projectile(self.rect.right, self.rect.centery)
        return bullet

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > WIDTH:
            self.kill()

class EnemyTank(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 50

    def update(self):
        pass

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, kind='health'):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        if kind == 'health':
            self.image.fill((0, 255, 0))
        elif kind == 'life':
            self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.kind = kind

class LevelManager:
    def __init__(self):
        self.level = 1

    def load_level(self):
        enemy_group.empty()
        collectible_group.empty()
        if self.level == 1:
            enemy_group.add(EnemyTank(500, HEIGHT - 80))
            enemy_group.add(EnemyTank(700, HEIGHT - 80))
            collectible_group.add(Collectible(400, HEIGHT - 70, 'health'))
            collectible_group.add(Collectible(600, HEIGHT - 70, 'life'))
        elif self.level == 2:
            for i in range(3):
                enemy_group.add(EnemyTank(400 + i * 150, HEIGHT - 80))
            collectible_group.add(Collectible(500, HEIGHT - 70, 'health'))
        elif self.level == 3:
            for i in range(4):
                enemy_group.add(EnemyTank(300 + i * 120, HEIGHT - 80))
            collectible_group.add(Collectible(550, HEIGHT - 70, 'life'))

    def next_level(self):
        self.level += 1
        if self.level > 3:
            return False
        else:
            self.load_level()
            return True

class ScoreManager:
    def __init__(self):
        self.score = 0

    def add_points(self, points):
        self.score += points

# --- Sprite Groups ---
player_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
collectible_group = pygame.sprite.Group()

# Create player
tank = Tank()
player_group.add(tank)

# Managers
level_manager = LevelManager()
score_manager = ScoreManager()
level_manager.load_level()

# --- Main Game Loop ---
def game_loop():
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys_pressed = pygame.key.get_pressed()

        player_group.update(keys_pressed)
        projectile_group.update()
        enemy_group.update()

        if keys_pressed[pygame.K_f]:
            bullet = tank.shoot()
            projectile_group.add(bullet)

        for bullet in projectile_group:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemy_group, False)
            for enemy in hit_enemies:
                enemy.health -= 25
                bullet.kill()
                if enemy.health <= 0:
                    enemy.kill()
                    score_manager.add_points(100)

        pickups = pygame.sprite.spritecollide(tank, collectible_group, True)
        for item in pickups:
            if item.kind == 'health':
                tank.health = min(100, tank.health + 30)
                score_manager.add_points(50)
            elif item.kind == 'life':
                tank.lives += 1
                score_manager.add_points(100)

        if not enemy_group:
            if not level_manager.next_level():
                return 'won'

        if tank.health <= 0:
            tank.lives -= 1
            tank.health = 100
            if tank.lives <= 0:
                return 'lost'

        screen.fill(WHITE)
        player_group.draw(screen)
        projectile_group.draw(screen)
        enemy_group.draw(screen)
        collectible_group.draw(screen)

        pygame.draw.rect(screen, RED, (10, 10, 100, 10))
        pygame.draw.rect(screen, GREEN, (10, 10, tank.health, 10))

        score_text = font.render(f"Score: {score_manager.score}", True, BLACK)
        level_text = font.render(f"Level: {level_manager.level}", True, BLACK)
        lives_text = font.render(f"Lives: {tank.lives}", True, BLACK)
        screen.blit(score_text, (10, 30))
        screen.blit(level_text, (10, 60))
        screen.blit(lives_text, (10, 90))

        pygame.display.flip()

# --- Game Over Screen ---
def game_over_screen(result):
    screen.fill(WHITE)
    if result == 'won':
        text = font.render("You Won! Press R to Restart or Q to Quit", True, BLACK)
    else:
        text = font.render("Game Over! Press R to Restart or Q to Quit", True, BLACK)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

# --- Restart Game ---
def restart_game():
    global tank, player_group, projectile_group, enemy_group, collectible_group, level_manager, score_manager
    tank = Tank()
    player_group = pygame.sprite.Group()
    player_group.add(tank)
    projectile_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    collectible_group = pygame.sprite.Group()
    level_manager = LevelManager()
    score_manager = ScoreManager()
    level_manager.load_level()
    result = game_loop()
    game_over_screen(result)

# --- Start the Game ---
result = game_loop()
game_over_screen(result)
