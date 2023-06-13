from typing import Any
import pygame
import random
import time
import math

LIVES = 3
SCREENWIDTH = 700
SCREENHEIGHT = 900
MOVEMENTSPEED = 800
SPEEDMULTIPLIER = 0.6
PROJECTILERADIUS = 5
PROJECTILESPEED = 5
GRAVITY = .2
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

pygame.init()
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
clock = pygame.time.Clock()
running = True

class Player(pygame.sprite.Sprite):
    def __init__(self, screen, playerRadius, playerColor, playerLocX, playerLocY):
        super().__init__()
        self.screen = screen
        self.playerRadius = playerRadius
        self.playerColor = playerColor
        self.playerLocX = playerLocX
        self.playerLocY = playerLocY

    def draw(self):
        pygame.draw.circle(surface=self.screen, color=self.playerColor, center=(self.playerLocX, self.playerLocY), radius=self.playerRadius)

class Projectile:
    def __init__(self, x, y, initial_speed_x, initial_speed_y):
        self.x = x
        self.y = y
        self.speedY = initial_speed_y
        self.speedX = initial_speed_x
        self.gravity = GRAVITY

    def update(self):
        self.x += self.speedX
        self.y += self.speedY

    def draw(self, screen, radius):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), radius)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, enemyRadius, enemyColor, spawnLocX, spawnLocY):
        super().__init__()
        self.screen = screen
        self.radius = enemyRadius
        self.color = enemyColor
        self.locX = spawnLocX
        self.locY = spawnLocY
    
    def draw(self):
        pygame.draw.circle(surface=self.screen, color=self.color, center=(self.locX, self.locY), radius=self.radius)

def playerMovement(speed):
    MOVEMENTSPEED = speed
    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:
        MOVEMENTSPEED = MOVEMENTSPEED * SPEEDMULTIPLIER
    if keys[pygame.K_UP]:
        player1.playerLocY -= MOVEMENTSPEED * deltaTime
    if keys[pygame.K_DOWN]:
        player1.playerLocY += MOVEMENTSPEED * deltaTime
    if keys[pygame.K_LEFT]:
        player1.playerLocX -= MOVEMENTSPEED * deltaTime
    if keys[pygame.K_RIGHT]:
        player1.playerLocX += MOVEMENTSPEED * deltaTime
    
def playerScreenLock(player1):
    if player1.playerLocX < (player1.playerRadius):
        player1.playerLocX = (player1.playerRadius)
    if player1.playerLocX > SCREENWIDTH - player1.playerRadius:
        player1.playerLocX = SCREENWIDTH - player1.playerRadius
    if player1.playerLocY < (player1.playerRadius):
        player1.playerLocY = (player1.playerRadius)
    if player1.playerLocY > SCREENHEIGHT - player1.playerRadius:
        player1.playerLocY = SCREENHEIGHT - player1.playerRadius

def generateCircularProjectiles(projectiles, projectile_count, projectile_radius, sourceX, sourceY, angle):
    angle_increment = 2 * math.pi / projectile_count
    current_angle = angle

    for _ in range(projectile_count):
        direction_x = math.cos(current_angle) * PROJECTILESPEED
        direction_y = math.sin(current_angle) * PROJECTILESPEED

        new_projectile = Projectile(sourceX, sourceY, direction_x, direction_y)
        projectiles.append(new_projectile)

        current_angle += angle_increment
        
    for projectile in projectiles:
        projectile.update()
        projectile.draw(screen, projectile_radius)
        if projectile.y <= 0:
            projectiles.remove(projectile)

def hitDetected(playerX, playerY, playerRadius, projectileX, projectileY, projectileRadius):
    distance = math.sqrt((playerX - projectileX) ** 2 + (playerY - projectileY) ** 2)
    threshold = playerRadius + projectileRadius
    if threshold > distance:
        return True
    else:
        return False

# life count display
heart_image = pygame.image.load('heart.png')
heart_width = 32
heart_height = 32
def drawLives(lives):
    for i in range(lives):
        x = i * (heart_width + 5) 
        y = 0  
        screen.blit(heart_image, (x, y)) 

projectiles = []
player1 = Player(screen, 10, RED, (SCREENWIDTH / 2), (SCREENHEIGHT * 0.9))

game_over = False
game_over_timer = 0
game_over_duration = 6000
default_font = pygame.font.Font(pygame.font.get_default_font(), 32)
game_over_text = default_font.render('GAME OVER', True, (255, 255, 255))

# main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    playerMovement(MOVEMENTSPEED)
    playerScreenLock(player1)
        
    screen.fill((0, 0, 0))  
    
    generateCircularProjectiles(projectiles, 8, PROJECTILERADIUS, random.randint(100, 600), 100, random.randint(0,20))
    
    drawLives(LIVES)    
    
    for projectile in projectiles:
        if hitDetected(player1.playerLocX, player1.playerLocY, player1.playerRadius, projectile.x, projectile.y, PROJECTILERADIUS):
            projectiles.remove(projectile)
            LIVES -= 1
    
    if LIVES <= 0:
        screen.blit(game_over_text, (SCREENWIDTH // 2 - game_over_text.get_width() // 2, SCREENHEIGHT // 2 - game_over_text.get_height() // 2))

        current_time = pygame.time.get_ticks()
        if current_time - game_over_timer >= game_over_duration:
            running = False 

    player1.draw() 
    pygame.display.flip()
    
    clock.tick(60)
    deltaTime = clock.tick(60) / 1000
    
pygame.quit()
