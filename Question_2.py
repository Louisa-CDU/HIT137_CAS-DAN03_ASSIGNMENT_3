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

# Clock
clock = pygame.time.Clock()
FPS = 60

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
        # Movement left/right
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Jump
        if keys_pressed[pygame.K_SPACE] and self.on_ground():
            self.vel_y = -self.jump_power

        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Floor collision
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
        pass  # Static for now

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

# --- Sprite Groups ---
player_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
collectible_group = pygame.sprite.Group()

# Create player
tank = Tank()
player_group.add(tank)

# Spawn enemies
enemy_group.add(EnemyTank(500, HEIGHT - 80))
enemy_group.add(EnemyTank(700, HEIGHT - 80))

# Spawn collectibles
collectible_group.add(Collectible(400, HEIGHT - 70, 'health'))
collectible_group.add(Collectible(600, HEIGHT - 70, 'life'))

# --- Main Game Loop ---
run = True
while run:
    clock.tick(FPS)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Keys
    keys_pressed = pygame.key.get_pressed()

    # Update
    player_group.update(keys_pressed)
    projectile_group.update()
    enemy_group.update()

    # Shooting
    if keys_pressed[pygame.K_f]:  # 'f' key to fire
        bullet = tank.shoot()
        projectile_group.add(bullet)

    # Bullet Collision
    for bullet in projectile_group:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemy_group, False)
        for enemy in hit_enemies:
            enemy.health -= 25
            bullet.kill()
            if enemy.health <= 0:
                enemy.kill()

    # Collectible pickup
    pickups = pygame.sprite.spritecollide(tank, collectible_group, True)
    for item in pickups:
        if item.kind == 'health':
            tank.health = min(100, tank.health + 30)
        elif item.kind == 'life':
            tank.lives += 1

    # Drawing
    screen.fill(WHITE)
    player_group.draw(screen)
    projectile_group.draw(screen)
    enemy_group.draw(screen)
    collectible_group.draw(screen)

    # Health bar
    pygame.draw.rect(screen, RED, (10, 10, 100, 10))
    pygame.draw.rect(screen, GREEN, (10, 10, tank.health, 10))

    # Update screen
    pygame.display.flip()

pygame.quit()
