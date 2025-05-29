import pygame 
import random
import math

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background_img = pygame.image.load("bg.jpg").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
background_x = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load sounds
hit_sound = pygame.mixer.Sound("hit.wav")
jump_sound = pygame.mixer.Sound("jump.wav")
shoot_sound = pygame.mixer.Sound("shoot.wav")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

GRAVITY = 1

def game_over_menu():
    while True:
        screen.fill((0, 0, 0))
        msg = font.render("¡GAME OVER - R key to start again.", True, WHITE)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: #start the game If the player presses R key
                    main()  
                    
                    pygame.quit()
                    exit()

def victory_menu():
    while True:
        screen.fill((0, 0, 0))
        msg = font.render("¡VICTORY, pres Q to finish.", True, YELLOW)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_image = pygame.image.load("girl.png").convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (100, 100))
        self.run_image = self.base_image
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
        speed = 5
        self.image = self.base_image
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed = 8
            self.image = self.run_image
        if keys[pygame.K_LEFT]:
            dx = -speed
        if keys[pygame.K_RIGHT]:
            dx = speed

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom >= HEIGHT:
            if not self.on_ground:
                self.on_ground = True
            self.rect.bottom = HEIGHT
            self.vel_y = 0
        else:
            self.on_ground = False

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -20
            jump_sound.play()

        self.rect.x += dx

    def shoot(self):
        shoot_sound.play()
        gun_y = self.rect.top + self.rect.height // 2.5
        return Projectile(self.rect.centerx + 30, int(gun_y))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, airborne=False):
        super().__init__()
        self.image = pygame.image.load("zombie_girl.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 50
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
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW if kind == 'coin' else GREEN)
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    projectiles.add(player.shoot())

        elapsed_time = pygame.time.get_ticks() - start_time

        if elapsed_time > 10000 * level and level < 3:
            level += 1
            level_message_time = pygame.time.get_ticks()
            scroll_speed *= 1.7
            enemy_speed *= 1.7
            collectible_speed *= 1.7

        if random.randint(1, 100) <= 2:
            y_pos = HEIGHT - 80
            airborne = False
            if elapsed_time < 39000:
                enemies.add(Enemy(WIDTH, y_pos, airborne))

        if elapsed_time >= 30000 and not any(enemy.health > 100 for enemy in enemies):
            y_pos = HEIGHT - 150
            airborne = False
            boss = Enemy(WIDTH, y_pos, airborne)
            boss.image = pygame.image.load("big_zombie.png").convert_alpha()
            boss.image = pygame.transform.scale(boss.image, (150, 150))
            boss.rect = boss.image.get_rect(midbottom=(WIDTH, HEIGHT))
            boss.health = 200
            enemies.add(boss)

        if pygame.time.get_ticks() % 3000 < 20:
            kind = random.choice(['health', 'life'])
            y_pos = random.choice([HEIGHT - 60, HEIGHT - 150, HEIGHT - 200])
            collectibles.add(Collectible(WIDTH, y_pos, kind))

        if pygame.time.get_ticks() % 1800 < 20:
            y_pos = random.choice([HEIGHT - 60, HEIGHT - 150, HEIGHT - 200])
            collectibles.add(Collectible(WIDTH, y_pos, 'coin'))

        if elapsed_time > 30000:
            for enemy in enemies:
                if enemy.health > 100 and random.randint(1, 60) == 1:
                    fireball = Projectile(enemy.rect.left, enemy.rect.centery)
                    fireball.image = pygame.Surface((15, 15))
                    fireball.image.fill(GREEN)
                    fireball.rect = fireball.image.get_rect(center=(enemy.rect.left, enemy.rect.centery))
                    fireball.speed = -6
                    fireballs.add(fireball)

        fireballs.update()
        player.update(keys)
        projectiles.update()
        enemies.update()
        collectibles.update()

        for enemy in enemies:
            if enemy.health > 100 and enemy.rect.left > 115:
                enemy.rect.x -= 2
            elif enemy.health > 100:
                enemy.rect.x = 115

        for projectile in projectiles:
            hit_list = pygame.sprite.spritecollide(projectile, enemies, False)
            for enemy in hit_list:
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
            if item.kind == 'health':
                player.health = min(player.health + 30, 100)
            elif item.kind == 'life':
                player.lives += 1
            elif item.kind == 'coin':
                player.score += 5
                player.coins += 1

        player_group.draw(screen)
        projectiles.draw(screen)
        fireballs.draw(screen)
        enemies.draw(screen)
        collectibles.draw(screen)

        screen.blit(font.render(f"Score: {player.score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Coins: {player.coins}", True, WHITE), (10, 40))
        screen.blit(font.render(f"Health: {player.health}", True, WHITE), (10, 70))
        screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (10, 100))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 130))

        for fireball in pygame.sprite.spritecollide(player, fireballs, True):
            hit_sound.play()
            player.health -= 10
            if player.health <= 0:
                player.lives -= 1
                player.health = 100

        time_left = max(0, 40000 - elapsed_time)
        seconds = time_left // 1000
        big_font = pygame.font.SysFont(None, 72)
        timer_text = big_font.render(f"{seconds}", True, WHITE)
        text_rect = timer_text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(timer_text, text_rect)

        if 0 < pygame.time.get_ticks() - level_message_time < level_message_duration:
            level_font = pygame.font.SysFont(None, 64)
            level_msg = level_font.render(f"Nivel {level}", True, YELLOW)
            level_rect = level_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            level_font = pygame.font.SysFont(None, 72)
            screen.blit(level_msg, level_rect)

        pygame.display.flip()
        clock.tick(60)

        if player.lives <= 0:
            game_over_menu()
            running = False

        if elapsed_time >= 40000:
            victory_menu()
            running = False

main()
pygame.quit()
