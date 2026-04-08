import pygame 
from sys import exit 
from random import randint

# CLASSES

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load("graphics/player.png").convert_alpha()
        self.image = pygame.transform.scale(img, (140, 80))
        self.rect = self.image.get_rect(midleft = (0, 280))

        self.speed = 5
        self.last_hit_time = -2000

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < 600:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed
    
    def update(self):
        self.player_input()
    
    def draw(self, surface, current_time):
        # Blink effect when hit
        if current_time - self.last_hit_time < 1000:
            if (current_time // 100) % 2 == 0:
                surface.blit(self.image, self.rect)
        else:
            surface.blit(self.image, self.rect)

# Coin Class
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load("graphics/coin.png").convert_alpha()
        self.image = pygame.transform.scale(img, (48, 16))
        y = randint(80, 540)
        self.rect = self.image.get_rect(midleft=(820, y))

    def reset_position(self):
        self.rect.midleft = (820, randint(80, 540))

    def update(self):
        self.rect.x -= obstacle_speed

        if self.rect.right < 0:
            self.kill()

# Seaweed Class
class Seaweed(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load("graphics/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(img, (80, 96))
        self.rect = self.image.get_rect(midbottom = (800, randint(560, 580)))

    def update(self):
        self.rect.x -= obstacle_speed
        if self.rect.right < 0:
            self.kill()

# Octopus Class
class Octopus(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img = pygame.image.load("graphics/enemy2.png").convert_alpha()
        self.image = pygame.transform.scale(img, (100, 80))
        self.rect = self.image.get_rect(midbottom = (800, randint(100, 430)))
        self.direction = 1   

    def update(self):
        self.rect.x -= obstacle_speed
        self.rect.y += 2 * self.direction   

        if self.rect.top < 100:
            self.rect.top = 100
            self.direction = 1
        elif self.rect.bottom > 450:
            self.rect.bottom = 450
            self.direction = -1

        if self.rect.right < 0:
            self.kill()

# FUNCTIONS
def display_score():
    current_time = (pygame.time.get_ticks() - start_time) // 1000
    surf = font_small.render(f'Time: {current_time}s', False, (f'White'))
    screen.blit(surf, (250, 10))

def display_coin_score():
    surf = font_small.render(f'Score: {coins}', True, "White")
    screen.blit(surf, (10, 10)) 

def display_lives():
    surf = font_small.render(f'Lives: {lives}', True, "White")
    screen.blit(surf, (130, 10))

def blit_center(surf, y):
    rect = surf.get_rect(center=(400, y)) 
    screen.blit(surf, rect)

def blit_center_lines(lines, start_y, line_gap=34):
    for i, surf in enumerate(lines):
        blit_center(surf, start_y + i * line_gap)
    
# PYGAME SETUP
pygame.init()
screen = pygame.display.set_mode((800, 600)) 
pygame.display.set_caption("Sub Rush - The Golden Quest") 
clock = pygame.time.Clock() 

font  = pygame.font.Font(None, 36)
font_big = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 28)

background = pygame.image.load("graphics/background.png").convert()  
background = pygame.transform.scale(background, (800, 600)) 

text = font_big.render("SUB RUSH:", True, "Gold")
text2 = font.render("The Golden Quest", True, "White")
text3 = font.render("Collect coins and reach 100 points as fast as you can.", True, "White")
text4 = font.render("Watch out for seaweed and octopuses!", True, "White")
text5 = font_small.render("Use the arrow keys to move. Press SPACE to start.", True, "White")

player = Player()

# SPRITE GROUPS
seaweed_group = pygame.sprite.Group()
octopus_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# GAME VARIABLES
state = "MENU"
start_time = 0
lives = 5
coins = 0
obstacle_speed = 5
recent_wins = [] # 5 most recent win times (only when the program is running)

# TIMERS
obstacle_timer = pygame.USEREVENT + 1
coin_timer = pygame.USEREVENT + 2
pygame.time.set_timer(obstacle_timer, 1000)
pygame.time.set_timer(coin_timer, 700)

# SOUNDS
game_music = pygame.mixer.Sound("audio/music.mp3")
coin_sound = pygame.mixer.Sound("audio/coin.flac")
hit_sound = pygame.mixer.Sound("audio/hit.wav")
game_over_sound = pygame.mixer.Sound("audio/game_over.wav")
you_won_sound = pygame.mixer.Sound("audio/win.wav")

# MAIN GAME LOOP
while True:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if state == "MENU" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            state = "GAME"
            start_time = pygame.time.get_ticks()
            lives = 5
            coins = 0
            seaweed_group.empty()
            octopus_group.empty()
            coin_group.empty()
            player.rect.midleft = (0, 280)
            game_music.play(loops = -1)

        elif state == "GAME OVER" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            state = "MENU"

        elif state == "YOU WON" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            state = "MENU"

        if event.type == coin_timer and state == "GAME":
            new_coin = Coin()

            # Ensure coin does not spawn on obstacles
            for _ in range(10):
                collides_with_seaweed = pygame.sprite.spritecollideany(new_coin, seaweed_group)
                collides_with_octopus = pygame.sprite.spritecollideany(new_coin, octopus_group)

                if not collides_with_seaweed and not collides_with_octopus:
                    break
                new_coin.reset_position()
 
            coin_group.add(new_coin)

        if event.type == obstacle_timer and state == "GAME":
            spawn_chance = 0.5 if coins < 50 else 0.8
            if randint(1, 100) <= spawn_chance * 100:
                seaweed_group.add(Seaweed())
            if randint(1, 100) <= spawn_chance * 100:
                octopus_group.add(Octopus())
             
    screen.blit(background,(0,0))  

    if state == "MENU":
        blit_center(text, 130)
        blit_center(text2, 185)
        blit_center(text3, 250)
        blit_center(text4, 285)
        blit_center(text5, 330)

        screen.blit(pygame.transform.scale(player.image, (235, 140)), (500, 360))

    elif state == "GAME":
        current_time = pygame.time.get_ticks()

        # Difficulty increase
        obstacle_speed = 8 if coins >= 50 else 5

        # Updates
        player.update()
        seaweed_group.update()
        octopus_group.update()
        coin_group.update()

        # Drawing
        player.draw(screen, current_time)
        seaweed_group.draw(screen)
        octopus_group.draw(screen)
        coin_group.draw(screen)

        # Collisions
        if pygame.sprite.spritecollide(player, seaweed_group, False) or \
           pygame.sprite.spritecollide(player, octopus_group, False):
        
           if current_time - player.last_hit_time > 2000:
               lives -= 1
               hit_sound.play()
               player.last_hit_time = current_time

               if lives <= 0:
                   final_time = (current_time - start_time) // 1000
                   game_over_sound.play() 
                   state = "GAME OVER"
  
        coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
        if coins_collected:
            coins += len(coins_collected)
            coin_sound.play()

        if coins >= 100:
            you_won_sound.play()
            final_time = (current_time - start_time) // 1000

            recent_wins.append(final_time)
            recent_wins = recent_wins[-5:]

            state = "YOU WON"

        display_score()
        display_coin_score()
        display_lives()

    elif state == "GAME OVER":
        game_music.stop()

        blit_center(font_big.render("GAME OVER", True, "Gold"), 160)
        blit_center(font.render(f"Score: {coins}", True, "White"), 230)
        blit_center(font.render(f"Time: {final_time}s", True, "White"), 270)
        blit_center(font_small.render("Press SPACE to return to menu", True, "White"), 340)

    elif state == "YOU WON":
        game_music.stop()

        blit_center(font_big.render("YOU WON!", True, "Gold"), 150)
        blit_center(font.render(f"Time: {final_time}s", True, "White"), 215)
        blit_center(font_small.render("Last 5 win times (this session):", True, "White"), 280)

        # Display recent win times
        y = 315
        for t in reversed(recent_wins):
            line = font_small.render(f"- {t}s", True, "White")
            blit_center(line, y)
            y += 28

        blit_center(font_small.render("Press SPACE to return to menu", True, "White"), 555)

    pygame.display.flip() 
    clock.tick(60) 
