
import pygame
import sys
import random

pygame.init()

# Windowed mode setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HIT137 Final Game")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

font = pygame.font.SysFont("comicsans", 30)
clock = pygame.time.Clock()
FPS = 60

score = 0
health = 100
level = 1
game_over = False

player = pygame.Rect(100, HEIGHT - 100, 50, 50)
player_vel = 5
jumping = False
jump_count = 10

projectiles = []
projectile_vel = 8

enemy = pygame.Rect(WIDTH - 100, HEIGHT - 100, 50, 50)
enemy_dir = -1

collectibles = [pygame.Rect(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 150), 20, 20) for _ in range(3)]

def draw_health_bar(health_val):
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 2 * health_val, 20))

def draw_window():
    screen.fill(WHITE)
    draw_health_bar(health)
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 40))
    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(level_text, (10, 70))
    pygame.draw.rect(screen, BLUE, player)
    pygame.draw.rect(screen, RED, enemy)
    for bullet in projectiles:
        pygame.draw.rect(screen, BLACK, bullet)
    for c in collectibles:
        pygame.draw.rect(screen, YELLOW, c)
    pygame.display.update()

running = True
while running:
    clock.tick(FPS)
    if game_over:
        screen.fill(WHITE)
        game_over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2))
        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            score = 0
            health = 100
            level = 1
            player.x, player.y = 100, HEIGHT - 100
            enemy.x = WIDTH - 100
            collectibles = [pygame.Rect(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 150), 20, 20) for _ in range(3)]
            projectiles.clear()
            game_over = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_vel
    if keys[pygame.K_RIGHT]:
        player.x += player_vel
    if not jumping and keys[pygame.K_SPACE]:
        jumping = True
    if keys[pygame.K_f]:
        if len(projectiles) < 5:
            bullet = pygame.Rect(player.centerx, player.y, 10, 5)
            projectiles.append(bullet)

    if jumping:
        if jump_count >= -10:
            neg = 1 if jump_count > 0 else -1
            player.y -= (jump_count ** 2) * 0.5 * neg
            jump_count -= 1
        else:
            jumping = False
            jump_count = 10

    # Clamp player within screen bounds
    player.x = max(0, min(player.x, WIDTH - player.width))
    player.y = max(0, min(player.y, HEIGHT - player.height))

    for bullet in projectiles[:]:
        bullet.x += projectile_vel
        if bullet.x > WIDTH:
            projectiles.remove(bullet)

    enemy.x += enemy_dir * 2
    if enemy.left <= WIDTH // 2 or enemy.right >= WIDTH:
        enemy_dir *= -1

    for bullet in projectiles[:]:
        if bullet.colliderect(enemy):
            score += 10
            projectiles.remove(bullet)
            enemy.x = WIDTH - 100
            if score % 50 == 0:
                level += 1
                enemy.width += 10

    if player.colliderect(enemy):
        health -= 1
        if health <= 0:
            game_over = True

    for c in collectibles[:]:
        if player.colliderect(c):
            health = min(100, health + 10)
            collectibles.remove(c)

    if player.x > WIDTH:
        level += 1
        player.x = 0
        enemy.x = WIDTH - 100
        collectibles = [pygame.Rect(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 150), 20, 20) for _ in range(3)]

    draw_window()

pygame.quit()
sys.exit()
