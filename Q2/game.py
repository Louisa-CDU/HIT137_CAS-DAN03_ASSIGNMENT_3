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

def show_instructions():
    font = pygame.font.SysFont(None, 25)
    showing = True

    while showing:
        screen.fill((0, 0, 0))
        text = font.render("Press ENTER to start. Arrows to move, SPACE = jump, Z = shoot, SHIFT = run", True, WHITE)
        screen.blit(text, (50, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    showing = False


def game_over_menu():
    while True:
        screen.fill((0, 0, 0))
        msg = font.render("¡GAME OVER - R key to start again or Q to quit.", True, WHITE)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: #start the game if the player presses R key
                    main()  
                elif event.key == pygame.K_q: #quit the game if the player presses Q key
                    pygame.quit()
                    exit()

def victory_menu():
    while True:
        screen.fill((0, 0, 0))
        msg = font.render("¡VICTORY, R key to start again or Q to quit.", True, YELLOW)
        screen.blit(msg, msg.get_rect(center =(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  #start the game if the player presses R key
                    main() 
                if event.key == pygame.K_q: #quit the game if the player presses Q key
                    pygame.quit()
                    exit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
         # Load the player image from file 
        self.base_image = pygame.image.load("girl.png").convert_alpha()     
        self.base_image = pygame.transform.scale(self.base_image, (100, 100))
        self.run_image = self.base_image # Image used when the player is running
        self.image = self.base_image   
        self.rect = self.image.get_rect(midbottom= (100, HEIGHT - 50)) # Set the initial position
        # player status information 
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

        # If shift is held, increase movement speed (running)   
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:    
            speed = 8
            self.image = self.run_image

        if keys[pygame.K_LEFT]: # Move left or right depending on key pressed
            dx = -speed
        if keys[pygame.K_RIGHT]:
            dx = speed

        self.vel_y += GRAVITY # Apply gravity to vertical velocity
        self.rect.y += self.vel_y

        if self.rect.bottom >= HEIGHT: # Check if the player is on the ground
            if not self.on_ground:     
                self.on_ground = True
            self.rect.bottom = HEIGHT
            self.vel_y = 0
        else:
            self.on_ground = False

        # Jumping logic: only allow jump if on the ground
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y= -20
            jump_sound.play()       

        self.rect.x += dx # Apply horizontal movement

    def shoot(self):  
        shoot_sound.play()

         # Calculate the vertical position where the projectile will be fired from,
         # approximately at the middle height of the character   
        gun_y = self.rect.top + self.rect.height // 2.5
        return Projectile(self.rect.centerx + 30, int(gun_y))

class Projectile(pygame.sprite.Sprite):                        
    def __init__(self, x, y):
        super().__init__()
        
        self.image = pygame.Surface((20, 5)) # Create the projectile as rectangular surface
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed =50
 
    def update(self):
        self.rect.x += self.speed # Move the projectile horizontally to the right
        # If the projectile moves off the right edge of the screen, remove it
        if self.rect.left > WIDTH: 
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, airborne=False):
        super().__init__()  # Load and scale the enemy image       
        self.image = pygame.image.load("zombie_girl.png").convert_alpha()
         # Set the enemy's position on the screen
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(topleft =(x, y))
        self.health = 50
        self.airborne = airborne # Indicates whether the enemy moves
        self.base_y = y
        self.timer = 0       

    def update(self): # Move enemy left across the screen
        self.rect.x -= enemy_speed 
        if self.airborne:       
            self.timer += 1
            self.rect.y = self.base_y + int(10 * math.sin(self.timer * 0.1))
        if self.rect.right < 0:    
            self.kill()

class Collectible(pygame.sprite.Sprite): # Create the collectibles
    def __init__(self, x, y, kind):     
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW if kind == 'coin' else GREEN)
        self.rect = self.image.get_rect(center= (x, y))
        self.kind = kind         
        self.timer = 0
        self.base_y = y     
     
    def update(self): 
        self.rect.x -= collectible_speed
        if self.kind == 'coin':
            self.timer += 1
            self.rect.y= self.base_y + int(5 * math.sin(self.timer * 0.2))
        if self.rect.right < 0:
            self.kill()

show_instructions()
def main():
    global enemy_speed, collectible_speed
    # Create the player character
    player = Player()

    # Group to manage the player (used for updating and drawing)
    player_group = pygame.sprite.Group(player)

    # Group to hold all projectiles (e.g., bullets)
    projectiles = pygame.sprite.Group()

    # Group to hold all enemies     
    enemies = pygame.sprite.Group()

    # Group to hold all collectibles
    collectibles = pygame.sprite.Group()

    # Group to hold enemy fireballs or similar projectiles
    fireballs = pygame.sprite.Group()     
    # spreed controls (scroll enemies and collectibles)
    scroll_speed = 2
    enemy_speed = 2     
    collectible_speed = 2

    #These variables help manage level progression and control how long
    #to show messages like “Level 1” or “Level Up!” on the screen.

    start_time = pygame.time.get_ticks()
    level = 1
    level_message_time = 0
    level_message_duration = 3000

    background_x = 0
    running = True

    #The main while running: is the main game loop. It ensures the 
    #game keeps updating and displaying as long as the game is active.
    while running:

        # creates a smooth, endlessly scrolling background by 
        # drawing two copies of the same image side-by-side and moving 
        # them to the left continuously. When one image scrolls off-screen, 
        # the position resets to repeat the cycle seamlessly
        screen.blit(background_img, (background_x, 0))
        screen.blit(background_img, (background_x + background_img.get_width(), 0))
        background_x -= scroll_speed         
        if background_x <= -background_img.get_width():
            background_x = 0

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            #Checks if the user clicked the close button on the window.
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z: # shoot key 
                    projectiles.add(player.shoot())

        elapsed_time = pygame.time.get_ticks() - start_time

        # As time passes and the player progresses, the game level increases
        # (up to level 3), and the game speeds up to increase difficulty.
        if elapsed_time > 10000 * level and level < 3:
            level += 1
            level_message_time = pygame.time.get_ticks()
            scroll_speed *= 1.7
            enemy_speed *= 1.7
            collectible_speed *= 1.7
        
        # Every frame, there is a small chance (2%) to spawn a grounded enemy
        # at a fixed vertical position on the right side of the screen, but 
        # only during the first 39 seconds of gameplay.
        if random.randint(1, 100) <= 2:
            y_pos = HEIGHT-80
            airborne = False       
            if elapsed_time < 39000:
                enemies.add(Enemy(WIDTH, y_pos, airborne))

        # After 30 seconds without a boss present, a big boss enemy spawns at 
        # the right edge of the screen with more health and a bigger sprite.
        if elapsed_time >= 30000 and not any(enemy.health > 100 for enemy in enemies):
            y_pos = HEIGHT - 150
            airborne = False
            boss = Enemy(WIDTH, y_pos, airborne)
            boss.image = pygame.image.load("big_zombie.png").convert_alpha()
            boss.image = pygame.transform.scale(boss.image, (200, 200))
            boss.rect = boss.image.get_rect(midbottom=(WIDTH, HEIGHT))
            boss.health = 200
            enemies.add(boss)         

        # Health or life collectibles spawn less frequently (~every 12 seconds).
        if pygame.time.get_ticks() % 12000 < 20:
            kind = random.choice(['health','life'])
            y_pos = random.choice([HEIGHT - 60, HEIGHT - 150, HEIGHT -200])
            collectibles.add(Collectible(WIDTH, y_pos, kind))

        # Coins spawn more frequently (~every 8 seconds).    
        if pygame.time.get_ticks() % 8000 < 20:
            y_pos = random.choice([HEIGHT - 60, HEIGHT - 150, HEIGHT -200])
            collectibles.add(Collectible(WIDTH, y_pos, 'coin'))


        # After 30 seconds, strong enemies occasionally shoot
        # green fireballs moving leftwards toward the player.
        if elapsed_time > 30000:
            for enemy in enemies:
                if enemy.health > 100 and random.randint(1, 60) == 1:
                    fireball = Projectile(enemy.rect.left, enemy.rect.centery)
                    fireball.image = pygame.Surface((15, 15))
                    fireball.image.fill(GREEN)
                    fireball.rect = fireball.image.get_rect(center=(enemy.rect.left, enemy.rect.centery))
                    fireball.speed = -6
                    fireballs.add(fireball)

        # This block calls the update() method on all the main game 
        # sprite groups and the player each frame, so their positions, 
        # states, and animations are processed continuously during the 
        # game loop
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
        
        #Boss enemies slowly move left until they reach x=115, then they stop.
        for projectile in projectiles:
            hit_list = pygame.sprite.spritecollide(projectile, enemies, False)
            for enemy in hit_list:
                enemy.health -= 25            
                projectile.kill()
                if enemy.health <= 0:      
                    enemy.kill()
                    player.score += 10

        #If there is a collision, it plays a hit sound 
        # and reduces the player's health by 1.
        if pygame.sprite.spritecollide(player, enemies, False):
            hit_sound.play()
            player.health -= 1
            if player.health <= 0:
                player.lives -= 1            
                player.health = 100

        #The code handles the player collecting items: it increases health,
        #  adds extra lives, or updates score and coin count depending on 
        # the type of collectible.
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

        # It shows the player’s current score, coins, health, lives, and level on the screen.
        screen.blit(font.render(f"Score: {player.score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Coins: {player.coins}", True, WHITE), (10,40))
        screen.blit(font.render(f"Health: {player.health}",True, WHITE), (10, 70))
        screen.blit( font.render(f"Lives: {player.lives}", True, WHITE), (10, 100))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 130))

        # Player takes damage from fireballs, losing health 
        # and possibly a life when health reaches zero.
        for fireball in pygame.sprite.spritecollide(player, fireballs, True):
            hit_sound.play()
            player.health -= 10
            if player.health <= 0:
                player.lives -= 1
                player.health = 100

        # Displays a countdown timer showing the remaining seconds on screen.
        time_left = max(0, 40000 - elapsed_time)
        seconds = time_left // 1000
        big_font = pygame.font.SysFont(None,72)
        timer_text = big_font.render(f"{seconds}", True, WHITE)
        text_rect = timer_text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(timer_text, text_rect)

        # This code displays a level-up message ("Nivel {level}") on the screen 
        # for a short duration after the player advances to a new level.
        if 0 < pygame.time.get_ticks() - level_message_time < level_message_duration:
            level_font = pygame.font.SysFont(None, 64)
            level_msg = level_font.render(f"Nivel {level}", True, YELLOW)
            level_rect = level_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            level_font = pygame.font.SysFont(None, 72)
            screen.blit(level_msg, level_rect)        

        pygame.display.flip()
        clock.tick(60) # 60 frames per second for consistent timing 

        # checks if the player has no lives left
        # If true, it calls the game_over_menu()
        if player.lives <= 0:
            game_over_menu()      
            running = False

        # This code checks if the elapsed game time is 40 seconds or more
        # If so, it calls the `victory_menu()` function to display the victory 
        # screen and sets `running = False` to stop the main game loop
        if elapsed_time >= 40000:
            victory_menu()
            running = False

main()
pygame.quit()     
