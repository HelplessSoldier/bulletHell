import numpy as np
import pygame.mixer
import pygame
import tkinter as tk
from tkinter import filedialog
from typing import Any
import random
import math
import threading
import librosa
import queue
import time

music_path = '/home/patrick/Desktop/my_github_repos/bulletHell/cYsmix_theBalladOfAMindlessGirl.mp3'

def populate_beat_stack(audio_path):
    waveform, sample_rate = librosa.load(audio_path)
    tempo, beat_frames = librosa.beat.beat_track(y=waveform, sr=sample_rate)
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)

    return beat_times

def populate_onset_stack(audio_path):
    waveform, sample_rate = librosa.load(audio_path)
    onset_frames = librosa.onset.onset_detect(y=waveform, sr=sample_rate, hop_length=512, backtrack=True)
    onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)

    return onset_times

def mainMenu():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((0, 0, 0))

        # Draw the start button
        start_button = pygame.Rect(300, 200, 200, 50)
        pygame.draw.rect(screen, (255, 0, 0), start_button)
        start_text = pygame.font.Font(None, 30).render("Start", True, (255, 255, 255))
        screen.blit(start_text, (355, 215))

        # Draw the song select button
        song_button = pygame.Rect(300, 300, 200, 50)
        pygame.draw.rect(screen, (0, 255, 0), song_button)
        song_text = pygame.font.Font(None, 30).render("Song Select", True, (255, 255, 255))
        screen.blit(song_text, (325, 315))

        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if start_button.collidepoint(mouse_pos) and mouse_click[0] == 1:
            onsets = populate_onset_stack(music_path)
            beats = populate_beat_stack(music_path)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
            gameLoop(beats, onsets)

        if song_button.collidepoint(mouse_pos) and mouse_click[0] == 1:
            root = tk.Tk()
            root.withdraw()

            # Open the file dialog
            file_path = filedialog.askopenfilename()
            if file_path:
                # Set the selected song
                global selected_song
                selected_song = pygame.mixer.Sound(file_path)

        pygame.display.flip()
        clock.tick(60)

def gameLoop(beats, onsets):

    LIVES = 9
    SCREENWIDTH = 700
    SCREENHEIGHT = 900
    MOVEMENTSPEED = 800
    SPEEDMULTIPLIER = 0.6
    ENEMYUPDATEDELAY = 5000
    PROJECTILESPEED = 4
    GRAVITY = .2
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0,255,0)
    PURPLE = (255, 0, 255)
        
    pygame.init()
    pygame.mixer.init()
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
        def __init__(self, x, y, initial_speed_x, initial_speed_y, color, radius):
            self.x = x
            self.y = y
            self.speedY = initial_speed_y
            self.speedX = initial_speed_x
            self.gravity = GRAVITY
            self.color = color
            self.radius = radius

        def update(self):
            self.x += self.speedX
            self.y += self.speedY

        def draw(self, screen, radius):
            pygame.draw.circle(screen, self.color, (self.x, self.y), radius)

    class Enemy(pygame.sprite.Sprite):
        def __init__(self, screen, enemyRadius, enemyColor):
            super().__init__()
            self.radius = enemyRadius
            self.color = enemyColor
            self.screen = screen
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect()
            self.position = pygame.Vector2(random.randint(100, SCREENWIDTH - 100), random.randint(100, SCREENHEIGHT * 0.35))
            self.target = self.position
            self.speed = 4
            self.attack_delay = 500  # Delay between attacks in milliseconds
            self.last_attack_time = pygame.time.get_ticks() 

        def update(self):
            # Interpolate towards the target position
            direction = self.target - self.position
            distance = direction.length()
            if distance > 0:
                direction.normalize_ip()
                movement = direction * min(distance, self.speed)
                self.position += movement
                self.rect.center = self.position

            # Check if target reached, then set a new target
            if distance <= self.speed:
                self.target = pygame.Vector2(random.randint(100, SCREENWIDTH - 100), random.randint(100, SCREENHEIGHT * 0.35))

        def attackBasic(self):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time >= self.attack_delay:
                self.last_attack_time = current_time
                generateCircularProjectiles(projectiles, projectile_count=8, projectile_radius=5, sourceX=self.position[0], sourceY=self.position[1], angle=0)
                
        def attackOnset(self):
            generateCircularProjectiles(projectiles, projectile_count=9, projectile_radius=20, sourceX=self.position[0], sourceY=self.position[1], angle=random.randint(0,360), color=YELLOW)
            
        def attackBeat(self):
            generateCircularProjectiles(projectiles, projectile_count=16, projectile_radius=5, sourceX=self.position[0], sourceY=self.position[1], angle=0, color=PURPLE)
                        
        def draw(self):
            pygame.draw.circle(surface=self.screen, color=self.color, center=(self.position[0], self.position[1]), radius=self.radius)

    def playerInput(speed):
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

    def generateCircularProjectiles(projectiles, projectile_count, projectile_radius, sourceX, sourceY, angle, color):
        angle_increment = 2 * math.pi / projectile_count
        current_angle = angle

        for _ in range(projectile_count):
            direction_x = math.cos(current_angle) * PROJECTILESPEED
            direction_y = math.sin(current_angle) * PROJECTILESPEED

            new_projectile = Projectile(sourceX, sourceY, direction_x, direction_y, color=color, radius=projectile_radius)
            projectiles.append(new_projectile)

            current_angle += angle_increment

    def hitDetected(playerX, playerY, playerRadius, projectileX, projectileY, projectileRadius):
        distance = math.sqrt((playerX - projectileX) ** 2 + (playerY - projectileY) ** 2)
        # threshold = playerRadius + projectileRadius
        threshold = projectileRadius
        if threshold > distance:
            return True
        else:
            return False

    heart_image = pygame.image.load('heart.png')
    heart_width = 32
    heart_height = 32
    def drawLives(lives):
        for i in range(lives):
            x = i * (heart_width + 5) 
            y = 0  
            screen.blit(heart_image, (x, y)) 

    def drawProjectiles():
        for projectile in projectiles:
            projectile.draw(screen, projectile.radius)
            projectile.update()
                     
    projectiles = []
    player1 = Player(screen, 10, RED, (SCREENWIDTH / 2), (SCREENHEIGHT * 0.9))
    
    game_over = False
    game_over_timer = 0
    game_over_duration = 5000
    
    default_font = pygame.font.Font(pygame.font.get_default_font(), 75)
    game_over_text = default_font.render('GAME OVER', True, (255, 255, 255))
    start_time = pygame.time.get_ticks()
    
    gameTimeThing = True # goofy hack for game over condition
    
    enemy = Enemy(screen=screen, enemyRadius=20, enemyColor=GREEN)
    hitsound = pygame.mixer.Sound('hitsound.mp3')
    
    attack_start_time_ms = pygame.time.get_ticks()
    onset_index = 0
    beat_index = 0
    last_onset = 0
    last_beat = 0

    # main loop---------------------------------------------------------------------------------------------------------------------------------------------------
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        playerInput(MOVEMENTSPEED)
        playerScreenLock(player1)
        screen.fill((0, 0, 0))  
        drawLives(LIVES)    
        
    # hit detection
        for projectile in projectiles:
            if hitDetected(player1.playerLocX, player1.playerLocY, player1.playerRadius, projectile.x, projectile.y, projectile.radius):
                projectiles.remove(projectile)
                LIVES -= 1
                hitsound.play()
    
    # game over condition  
        if LIVES <= 0:
            current_time = pygame.time.get_ticks()
            screen.blit(game_over_text, (SCREENWIDTH // 2 - game_over_text.get_width() // 2, SCREENHEIGHT // 2 - game_over_text.get_height() // 2))
            elapsed_time_text = default_font.render("TIME: " + str((current_time - start_time)//1000) + " S", True, (255,255,255))
            screen.blit(elapsed_time_text, (SCREENWIDTH // 2 - elapsed_time_text.get_width() // 2, 700))
            
            if gameTimeThing:
                start_time = current_time
                gameTimeThing= False
                
            if current_time - start_time >= game_over_duration:
                running = False 

    # enemy movement
        enemy_current_time = pygame.time.get_ticks()
        if enemy_current_time - start_time >= ENEMYUPDATEDELAY:
            enemy.target = pygame.Vector2(random.randint(50, SCREENWIDTH - 50), random.randint(100, SCREENHEIGHT * 0.3))
            start_time = enemy_current_time
        
    # ememy attacks
        onset_current_time = pygame.time.get_ticks() - attack_start_time_ms
        if onset_current_time >= (onsets[onset_index] * 1000):
            enemy.attackOnset()
            # print(f'onsettime: {onsets[onset_index]} currentTime: {onset_current_time} last_onset: {last_onset}')
            last_onset = onset_current_time
            onset_index += 1
            
        beat_current_time = pygame.time.get_ticks() - attack_start_time_ms
        if beat_current_time >= (beats[beat_index] * 1000):
            enemy.attackBeat()
            # print(f'beattime: {beats[beat_index]} currentTime: {beat_current_time} last_beat: {last_beat}')
            last_beat = beat_current_time
            beat_index += 1
  
        enemy.update()
        enemy.draw()

        drawProjectiles()

        player1.draw() 
        pygame.display.flip()
        
        clock.tick(60)
        deltaTime = clock.tick(60) / 1000
        
    pygame.mixer.music.stop()
    pygame.quit()

mainMenu()