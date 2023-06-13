from typing import Any
import pygame
import random
import time
import math

SCREENWIDTH = 700
SCREENHEIGHT = 900
MOVEMENTSPEED = 800
SPEEDMULTIPLIER = 0.6
PROJECTILERADIUS = 10
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
        self.gravity = .5

    def update(self):
        self.speedY += self.gravity
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

def generateRandomProjectiles(last_executed_time, initial_projectile_count, projectile_radius):
    current_time = time.time()
    PROJECTILECOUNT = initial_projectile_count
    if current_time - last_executed_time >= 10:
        PROJECTILECOUNT = 1
        last_executed_time = current_time
    
    while PROJECTILECOUNT > 0:
        new_projectile = Projectile(random.randint(0, SCREENWIDTH), 100, random.randint(-1,1), random.randint(-1,1))
        projectiles.append(new_projectile)
        PROJECTILECOUNT -= 1
        
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

projectiles = []
last_executed_time = time.time()
player1 = Player(screen, 10, RED, (SCREENWIDTH / 2), (SCREENHEIGHT * 0.9))

hitcount = 0
# main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    playerMovement(MOVEMENTSPEED)
    playerScreenLock(player1)
        
    screen.fill((0, 0, 0))  
        
    generateRandomProjectiles(last_executed_time, 2, PROJECTILERADIUS)
    
    for projectile in projectiles:
        if hitDetected(player1.playerLocX, player1.playerLocY, player1.playerRadius, projectile.x, projectile.y, PROJECTILERADIUS):
            print(f'HIT {hitcount}')
            projectiles.remove(projectile)
            hitcount += 1
            
    player1.draw() 
    pygame.display.flip()
    
    clock.tick(60)
    deltaTime = clock.tick(60) / 1000
    
pygame.quit()
