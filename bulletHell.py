import pygame
import random

pygame.init()
SCREENWIDTH = 700
SCREENHEIGHT = 900
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
clock = pygame.time.Clock()
running = True
RED = (255, 0, 0)
SPEEDMULTIPLIER = 0.6

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
        
class Projectile(pygame.sprite.Sprite):
    def __init__(self, screen, projectileRadius, projectileColor, spawnLocX, spawnLocY):
        super().__init__()
        self.screen = screen
        self.Radius = projectileRadius
        self.Color = projectileColor
        self.spawnLocX = spawnLocX
        self.spawnLocY = spawnLocY
        
    def draw(self):
        pygame.draw.circle(surface=self.screen, color=self.projectileColor, center=(self.spawnLocX, self.spawnLocY), radius=self.projectileRadius)
        
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


# create player obj
player1 = Player(screen, 10, RED, (SCREENWIDTH / 2), (SCREENHEIGHT * 0.9))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # player movement with arrow keys
    MOVEMENTSPEED = 800
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
        
    # lock player to screenspace
    # TODO: left and top of screen not accurate
    if player1.playerLocX < (player1.playerRadius / 2):
        player1.playerLocX = (player1.playerRadius / 2)
    if player1.playerLocX > SCREENWIDTH - player1.playerRadius:
        player1.playerLocX = SCREENWIDTH - player1.playerRadius
    if player1.playerLocY < (player1.playerRadius / 2):
        player1.playerLocY = (player1.playerRadius / 2)
    if player1.playerLocY > SCREENHEIGHT - player1.playerRadius:
        player1.playerLocY = SCREENHEIGHT - player1.playerRadius
        
    #spawn projectiles
    projectiles = []
    
        
    screen.fill((0, 0, 0))  
    player1.draw() 
    
    pygame.display.flip()
    clock.tick(60)
    deltaTime = clock.tick(60) / 1000
    
pygame.quit()
