import pygame
import math
import random
import os
from enemy import Enemy
import button

pygame.init()

# Window size
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 790

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Castle Defense")

clock = pygame.time.Clock()
FPS = 60

# Define game variables
level = 1
level_difficulty = 0
target_difficulty = 1000
difficulty_multiplier = 1.1
game_over = False
next_level = False
enemy_timer = 1000
last_enemy = pygame.time.get_ticks()
enemies_alive = 0
high_score = 0
max_towers = 3
tower_cost = 5000
tower_positions = [
    [SCREEN_WIDTH - 600, SCREEN_HEIGHT - 300],
    [SCREEN_WIDTH - 700, SCREEN_HEIGHT - 300],
    [SCREEN_WIDTH - 800, SCREEN_HEIGHT - 300],
]

# load high score file
if os.path.exists("score.txt"):
    with open("score.txt", "r") as file:
        high_score = int(file.read())

# Define colors
WHITE = (255, 255, 255)
GRAY = (77, 77, 77)

# define font
font_50 = pygame.font.SysFont("Futura", 50)
font_100 = pygame.font.SysFont("Futura", 100)

# Load images
bg = pygame.image.load("img/bg.png").convert_alpha()

# Castle
castle_img_100 = pygame.image.load("img/castle/castle_100.png").convert_alpha()
castle_img_50 = pygame.image.load("img/castle/castle_50.png").convert_alpha()
castle_img_25 = pygame.image.load("img/castle/castle_25.png").convert_alpha()

# Towers
tower_img_100 = pygame.image.load("img/tower/tower_100.png").convert_alpha()
tower_img_50 = pygame.image.load("img/tower/tower_50.png").convert_alpha()
tower_img_25 = pygame.image.load("img/tower/tower_25.png").convert_alpha()

# Bullet image
bullet_img = pygame.image.load("img/bullet.png").convert_alpha()
b_w = bullet_img.get_width()
b_h = bullet_img.get_height()
bullet_img = pygame.transform.scale(bullet_img, (int(b_w * 0.09), int(b_h * 0.09)))

# Load enemy images
enemy_animations = []
enemy_types = ["knight", "goblin", "purple_goblin", "red_goblin"]
enemy_health = [75, 100, 125, 150]

animation_types = ["walk", "attack", "death"]  # corresponding with folder names
for enemy in enemy_types:
    # load animation
    animation_list = []
    for animation in animation_types:
        # reset temporary list
        temp_list = []
        # define number of frames
        num_of_frames = 20
        for i in range(num_of_frames):
            img = pygame.image.load(f"img/enemies/{enemy}/{animation}/{i}.png").convert_alpha()
            enemy_width = img.get_width()
            enemy_height = img.get_height()
            img = pygame.transform.scale(img, (int(enemy_width * 0.3), int(enemy_height * 0.3)))
            temp_list.append(img)  # going to store all of the images from the folder
        animation_list.append(temp_list)
    enemy_animations.append(animation_list)

# Button images
# Repair image
repair_img = pygame.image.load("img/repair.png").convert_alpha()
# Armor image
armor_img = pygame.image.load("img/armor.png").convert_alpha()


# function for outputting text into the screen
def draw_text(text, font, font_color, x, y):
    img = font.render(text, True, font_color)
    screen.blit(img, (x, y))


# function for displaying status
def show_info():
    draw_text("Money: " + str(castle.money), font_50, GRAY, 10, 10)
    draw_text("Score: " + str(castle.score), font_50, GRAY, 1100, 10)
    draw_text("High Score: " + str(high_score), font_50, GRAY, 1100, 50)
    draw_text("Level: " + str(level), font_50, GRAY, SCREEN_WIDTH // 2 - 100, 10)
    draw_text("Health: " + str(castle.health) + " | " + str(castle.max_health), font_50, GRAY, SCREEN_WIDTH // 2 - 200,
              50)
    draw_text("1000", font_50, WHITE, 1000, 170)
    draw_text("2500", font_50, WHITE, 1115, 170)
    draw_text(str(tower_cost), font_50, WHITE, 1240, 170)


class Castle():
    def __init__(self, image100, image50, image25, x, y, scale):
        self.health = 1000
        self.max_health = self.health
        self.fired = False
        self.money = 0
        self.score = 0

        width = image100.get_width()
        height = image100.get_height()

        self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
        self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
        self.image25 = pygame.transform.scale(image25, (int(width * scale), int(height * scale)))

        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y

    def shoot(self):
        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self.rect.midleft[0]
        y_dist = -(pos[1] - self.rect.midleft[1])
        self.angle = math.degrees(math.atan2(y_dist, x_dist))
        # get mouseclick
        if pygame.mouse.get_pressed()[0] and self.fired == False and pos[1] > 450:
            self.fired = True
            bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
            bullet_group.add(bullet)
        # reset mouseclick
        if not pygame.mouse.get_pressed()[0]:
            self.fired = False

    def draw(self):
        # check which image to use based on current health
        if self.health <= 250:
            self.image = self.image25
        elif self.health <= 500:
            self.image = self.image50
        else:
            self.image = self.image100
        screen.blit(self.image, self.rect)

    def repair(self):
        if self.money >= 1000 and self.health < self.max_health:
            self.health += 500
            self.money -= 1000
            if castle.health > castle.max_health:
                castle.health = castle.max_health

    def armor(self):
        if self.money >= 2500:
            self.max_health += 250
            self.money -= 2500


class Tower(pygame.sprite.Sprite):
    def __init__(self, image100, image50, image25, x, y, scale):
        pygame.sprite.Sprite.__init__(self)

        self.angle = 0
        self.last_shot = pygame.time.get_ticks()
        self.target_acquired = False

        width = image100.get_width()
        height = image100.get_height()

        self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
        self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
        self.image25 = pygame.transform.scale(image25, (int(width * scale), int(height * scale)))

        self.image = self.image100
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, enemy_group):
        self.target_acquired = False
        for e in enemy_group:
            if e.alive:
                target_x, target_y = e.rect.midbottom
                self.target_acquired = True
                break  # so the target stays the same, not shooting at the next target in line

        if self.target_acquired:
            x_dist = target_x - self.rect.midleft[0]
            y_dist = -(target_y - self.rect.midleft[1])
            self.angle = math.degrees(math.atan2(y_dist, x_dist))

            shot_cooldown = 1000
            # fire bullets
            if pygame.time.get_ticks() - self.last_shot > shot_cooldown:
                self.last_shot = pygame.time.get_ticks()  # resets the timer so the tower does not keep firing non-stop
                bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
                bullet_group.add(bullet)

        # check which image to use based on current health
        if castle.health <= 250:
            self.image = self.image25
        elif castle.health <= 500:
            self.image = self.image50
        else:
            self.image = self.image100
        screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = math.radians(angle)  # convert input angle into radians
        self.speed = 10
        # calculate the horizontal and vertical speeds based on the angle
        self.dx = math.cos(self.angle) * self.speed
        self.dy = -(math.sin(self.angle) * self.speed)

    def update(self):
        # check if bullet has gone off the screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

        # move bullet
        self.rect.x += self.dx
        self.rect.y += self.dy


class Crosshair():
    def __init__(self, scale):
        image = pygame.image.load("img/crosshair.png").convert_alpha()
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()

        # hide mouse
        pygame.mouse.set_visible(False)

    def draw(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.center = (mouse_x, mouse_y)
        screen.blit(self.image, self.rect)


# Create castle
castle = Castle(castle_img_100, castle_img_50, castle_img_25, SCREEN_WIDTH - 500, SCREEN_HEIGHT - 400, 0.35)

# Create crosshair
crosshair = Crosshair(0.025)

# Create buttons
repair_button = button.Button(SCREEN_WIDTH - 400, 100, repair_img, 0.7)
armor_button = button.Button(SCREEN_WIDTH - 270, 100, armor_img, 0.6)
tower_button = button.Button(SCREEN_WIDTH - 140, 100, tower_img_100, 0.15)

# Create groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()

# Game loop
run = True
while run:

    clock.tick(FPS)
    if game_over == False:
        screen.blit(bg, (0, 0))

        # Draw castle
        castle.draw()
        castle.shoot()
        # Draw towers
        tower_group.draw(screen)
        tower_group.update(enemy_group)

        # Draw crosshair
        crosshair.draw()

        # Draw bullets
        bullet_group.update()
        bullet_group.draw(screen)

        # Draw enemies
        enemy_group.update(screen, castle, bullet_group)

        # Show details
        show_info()

        # Draw buttons
        if repair_button.draw(screen):
            castle.repair()
        if armor_button.draw(screen):
            castle.armor()
        if tower_button.draw(screen):
            # check if there is enough money and build a tower
            if castle.money >= tower_cost and len(tower_group) < max_towers:
                tower = Tower(tower_img_100, tower_img_50, tower_img_25,
                              tower_positions[len(tower_group)][0],
                              tower_positions[len(tower_group)][1], 0.3)
                tower_group.add(tower)
                # subtract money
                castle.money -= tower_cost

        # Create enemies
        # Check if max number of enemies has been reached
        if level_difficulty < target_difficulty:
            if pygame.time.get_ticks() - last_enemy > enemy_timer:  # 1 sec has passed and another enemy can be created
                e = random.randint(0, len(enemy_types) - 1)
                enemy = Enemy(enemy_health[e], enemy_animations[e], -100, SCREEN_HEIGHT - 120, 1)
                enemy_group.add(enemy)
                # reset enemy timer
                last_enemy = pygame.time.get_ticks()
                # increase level difficulty by enemy health
                level_difficulty += enemy_health[e]

        # check if all the enemies have been spawned
        if level_difficulty >= target_difficulty:
            # check how many are still alive
            enemies_alive = 0
            for e in enemy_group:
                if e.alive:
                    enemies_alive += 1
            # if there are none alive, the level is complete
            if enemies_alive == 0 and next_level is False:
                next_level = True
                level_reset_time = pygame.time.get_ticks()

        # move onto the next level and increase difficulty
        if next_level:
            draw_text("LEVEL COMPLETE!", font_100, WHITE, 300, 300)
            # update high score
            if castle.score > high_score:
                high_score = castle.score
                with open("score.txt", "w") as file:
                    file.write(str(high_score))

            if pygame.time.get_ticks() - level_reset_time > 2000:
                next_level = False
                level += 1
                last_enemy = pygame.time.get_ticks()
                target_difficulty *= difficulty_multiplier
                level_difficulty = 0
                enemy_group.empty()

        # check game over
        if castle.health <= 0:
            game_over = True
    else:
        draw_text("GAME OVER!", font_100, WHITE, 200, 200)
        draw_text("Press 'SPACE' to play again", font_50, WHITE, 200, 400)
        pygame.mouse.set_visible(True)
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            # reset variables so you can play again
            game_over = False
            level = 1
            target_difficulty = 1000
            level_difficulty = 0
            last_enemy = pygame.time.get_ticks()
            enemy_group.empty()
            tower_group.empty()
            castle.score = 0
            castle.health = 1000
            castle.max_health = castle.health
            castle.money = 0
            pygame.mouse.set_visible(False)

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Update display window
    pygame.display.update()

pygame.quit()
