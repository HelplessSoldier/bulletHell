import pygame.mixer
import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import filedialog
from typing import Any
import random
import math
from threading import Thread
import librosa
#Copyright (c) 2013--2023, librosa development team.

music_path = ''

SCREEN_HEIGHT = 900
SCREEN_WIDTH = 700

PLANE_SIZE = 900
SUBDIVISIONS = 20
SUB_PLANE_SIZE = PLANE_SIZE // SUBDIVISIONS

PLANE_X_LOC = (SCREEN_WIDTH // 2) - (PLANE_SIZE // 2)
PLANE_Y_LOC = (SCREEN_HEIGHT // 2) - (PLANE_SIZE // 2)

PINK = (255, 105, 180)
TEAL = (0, 128, 128)

def create_vertex_groups(PLANE_SIZE, SUBDIVISIONS, bassValue, midsValue, highsValue):
    vertex_array = []
    plane_x_loc = (SCREEN_WIDTH // 4) + (PLANE_SIZE // 4)
    plane_y_loc = (SCREEN_HEIGHT // 4) + (PLANE_SIZE // 4)
    vertex_groups = []
    
    for j in range(SUBDIVISIONS + 1):
        for i in range(SUBDIVISIONS + 1):
            x = i * (PLANE_SIZE / SUBDIVISIONS) - (PLANE_SIZE / 2) + plane_x_loc
            y = j * (PLANE_SIZE / SUBDIVISIONS) - (PLANE_SIZE / 2) + plane_y_loc
            
            if j <= SUBDIVISIONS // 3 and i % 2 == 0:
                y = ((highsValue / 600) + 1) * y
            elif j >= SUBDIVISIONS // 3 and j <= (SUBDIVISIONS // 3) * 2 and i % 2 == 0:
                y = ((midsValue / 600) + 1) * y
            elif j >= (SUBDIVISIONS // 3) * 2 and i % 2 == 0:
                y = ((bassValue / 600) + 1) * y
                   
            vertex_array.append((x, y))
    
    row_size = SUBDIVISIONS + 1
    for i in range(0, len(vertex_array), row_size):
        row_group = vertex_array[i:i+row_size]
        vertex_groups.append(tuple(row_group))
    
    return vertex_groups

def draw_edges(screen, vertex_array):
    last_location = (0, 0)
    new_group = True 
    num_groups = len(vertex_array)
    
    for group_index, groups in enumerate(vertex_array):
        for vertex_index, location in enumerate(groups):
            if new_group:
                last_location = location
                new_group = False
            else:
                # Calculate the color for the current edge based on the gradient
                color_ratio = group_index / (num_groups - 1)  # Calculate the ratio based on group index
                r = int(PINK[0] + (TEAL[0] - PINK[0]) * color_ratio)
                g = int(PINK[1] + (TEAL[1] - PINK[1]) * color_ratio)
                b = int(PINK[2] + (TEAL[2] - PINK[2]) * color_ratio)
                color = (r, g, b)
                
                pygame.draw.line(screen, color, last_location, location, 1)
                last_location = location
        
        new_group = True

def audio_time_magnitude(audio_file):
    y, sr = librosa.load(audio_file)

    # Extract the frequency components using a Short-Time Fourier Transform (STFT)
    D = librosa.stft(y)

    # Split the frequency components into bass, mids, and highs ranges
    frequencies = librosa.fft_frequencies(sr=sr)
    bass_range = (20, 140)
    mids_range = (140, 2000)
    highs_range = (2000, frequencies.max())

    bass_bins = librosa.core.fft_frequencies(sr=sr, n_fft=D.shape[0]).searchsorted(bass_range)
    mids_bins = librosa.core.fft_frequencies(sr=sr, n_fft=D.shape[0]).searchsorted(mids_range)
    highs_bins = librosa.core.fft_frequencies(sr=sr, n_fft=D.shape[0]).searchsorted(highs_range)

    # Compute the magnitude spectrum
    magnitude = librosa.amplitude_to_db(abs(D))

    # Calculate the mean magnitude within each frequency range
    bass_magnitude = abs(magnitude[bass_bins[0]:bass_bins[1]].mean(axis=0))
    mids_magnitude = abs(magnitude[mids_bins[0]:mids_bins[1]].mean(axis=0))
    highs_magnitude = abs(magnitude[highs_bins[0]:highs_bins[1]].mean(axis=0))

    # Get the time information
    frames = librosa.frames_to_time(range(magnitude.shape[1]), sr=sr)

    # Create a tuple of (time, magnitude) for each frequency range
    bass_data = list(zip(frames, bass_magnitude))
    mids_data = list(zip(frames, mids_magnitude))
    highs_data = list(zip(frames, highs_magnitude))

    return bass_data, mids_data, highs_data

def smoothData(array, smoothingFactor):
    smoothed_array = []
    num_points = len(array)
    
    for i in range(num_points):
        if i < smoothingFactor // 2:
            smoothed_value = array[i][1]
        elif i >= num_points - smoothingFactor // 2:
            smoothed_value = array[i][1]
        else:
            start_index = i - smoothingFactor // 2
            end_index = i + smoothingFactor // 2
            values = [array[j][1] for j in range(start_index, end_index + 1)]
            smoothed_value = sum(values) / smoothingFactor
        
        smoothed_array.append((array[i][0], smoothed_value))
    
    return smoothed_array

def equalizeArrays(array1, array2, array3):
    maxValue = 100
    
    array1Multi = maxValue / max(x[1] for x in array1 if x[1] != maxValue)
    array2Multi = maxValue / max(x[1] for x in array2 if x[1] != maxValue)
    array3Multi = maxValue / max(x[1] for x in array3 if x[1] != maxValue)
    
    newArray1 = [(x[0], x[1] * array1Multi) for x in array1]
    newArray2 = [(x[0], x[1] * array2Multi) for x in array2]
    newArray3 = [(x[0], x[1] * array3Multi) for x in array3]

    return newArray1, newArray2, newArray3

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

def open_file_dialog():
    global music_path
    root = tk.Tk()
    root.withdraw()

    selected_music_path = filedialog.askopenfilename()
    if selected_music_path:  
        music_path = selected_music_path

def mainMenu():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    file_dialog_thread = None    

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((0, 0, 0))

        # Draw the start button
        start_button = pygame.Rect(300, 200, 200, 50)
        pygame.draw.rect(screen, (0, 153, 51), start_button)
        start_text = pygame.font.Font(None, 30).render("Start", True, (255, 255, 255))
        screen.blit(start_text, (355, 215))

        # Draw the song select button
        song_button = pygame.Rect(300, 300, 200, 50)
        pygame.draw.rect(screen, (0, 102, 255), song_button)
        song_text = pygame.font.Font(None, 30).render("Song Select", True, (255, 255, 255))
        screen.blit(song_text, (325, 315))

        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if start_button.collidepoint(mouse_pos) and mouse_click[0] == 1:
            if music_path == '':
                selectSongReminder = pygame.Rect(300, 300, 200, 50)
                pygame.draw.rect(screen, (0, 0, 0), selectSongReminder)
                selectSongReminderText = pygame.font.Font(None, 50).render('Please select a song.', True, (255, 255, 255))
                screen.blit(selectSongReminderText, (225, 115))
                pygame.display.flip()
                pygame.time.wait(2000)
            else:
                onsets = populate_onset_stack(music_path)
                beats = populate_beat_stack(music_path)
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play()
                gameLoop(beats, onsets)

        if song_button.collidepoint(mouse_pos) and mouse_click[0] == 1:
            # Check if the file dialog thread is already running
            if file_dialog_thread and file_dialog_thread.is_alive():
                continue

            file_dialog_thread = Thread(target=open_file_dialog)
            file_dialog_thread.start()

        pygame.display.flip()
        clock.tick(60)

def hello():
    print('helloworld')

def gameLoop(beats, onsets):

    LIVES = 9
    SCREENWIDTH = 700
    SCREENHEIGHT = 900
    MOVEMENTSPEED = 800
    SPEEDMULTIPLIER = 0.6
    ENEMYUPDATEDELAY = 5000
    PROJECTILESPEED = 4
    PLAYERPROJECTILESPEED = 20
    GRAVITY = .2
    PLAYERCOLOR = (255, 0, 149)
    YELLOW = (255, 255, 0)
    GREEN = (0,255,0)
    ENEMYCOLOR = (255, 0, 0)
    PROJECTILEBRIGHTNESS = 1
    SCORE = 0
    
    BASSVOLUMETHRESHOLD = 60
    MIDSVOLUMETHRESHOLD = 60
    HIGHSVOLUMETHRESHOLD = 60
    TIMINGOFFSET = -800
        
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    clock = pygame.time.Clock()
    running = True
        
    class Player(pygame.sprite.Sprite):
        def __init__(self, screen, playerRadius, playerColor, playerLocX, playerLocY, horizontalSpeed):
            super().__init__()
            self.screen = screen
            self.playerRadius = playerRadius
            self.playerColor = playerColor
            self.playerLocX = playerLocX
            self.playerLocY = playerLocY
            self.horizontalSpeed = horizontalSpeed

        def draw(self):
            pygame.draw.circle(surface=self.screen, color=self.playerColor, center=(self.playerLocX, self.playerLocY), radius=self.playerRadius)
            
        def attack(self, horizontalSpeed):            
            new_player_projectile = Projectile(self.playerLocX, self.playerLocY, horizontalSpeed, -PLAYERPROJECTILESPEED, PLAYERCOLOR, 5)
            playerProjectiles.append(new_player_projectile)

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

    def playerInput(speed, player):
        MOVEMENTSPEED = speed
        horizontalSpeed = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            MOVEMENTSPEED = MOVEMENTSPEED * SPEEDMULTIPLIER
        if keys[pygame.K_UP]:
            player.playerLocY -= MOVEMENTSPEED * deltaTime
        if keys[pygame.K_DOWN]:
            player.playerLocY += MOVEMENTSPEED * deltaTime
        if keys[pygame.K_LEFT]:
            player.playerLocX -= MOVEMENTSPEED * deltaTime
            horizontalSpeed = -MOVEMENTSPEED
        if keys[pygame.K_RIGHT]:
            player.playerLocX += MOVEMENTSPEED * deltaTime
            horizontalSpeed = MOVEMENTSPEED
        if keys[pygame.K_x]:
            player.attack(horizontalSpeed= horizontalSpeed / 120)
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            
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
                
        def attackBass(self, value):
            output_color = value * (255 / 100)
            
            generateCircularProjectiles(projectiles, 
                                        projectile_count= 8, 
                                        projectile_radius= int(value / 5), 
                                        sourceX= self.position[0], 
                                        sourceY= self.position[1], 
                                        angle= 360 * (value/32), 
                                        color= (0, output_color * PROJECTILEBRIGHTNESS, output_color * PROJECTILEBRIGHTNESS))
        
        def attackMids(self, value):
            output_color = value * (255 // 100)
            
            generateCircularProjectiles(projectiles, 
                                        projectile_count= max(1, (int(value) // 4)), 
                                        projectile_radius= 10, 
                                        sourceX= self.position[0], 
                                        sourceY= self.position[1], 
                                        angle= 360 * (value/32), 
                                        color= (output_color * PROJECTILEBRIGHTNESS, 0, output_color * PROJECTILEBRIGHTNESS))
        
        def attackHighs(self, value):
            output_color = value * (255 // 100)

            generateCircularProjectiles(projectiles,
                                        projectile_count=max(abs(int(value / 10)), 1),
                                        projectile_radius= 5,
                                        sourceX= self.position[0],
                                        sourceY= self.position[1],
                                        angle=0,
                                        color=(119, 0, 255))
                
        def attackOnset(self):
            generateCircularProjectiles(projectiles, projectile_count=9, projectile_radius=20, sourceX=self.position[0], sourceY=self.position[1], angle=random.randint(0,360), color=YELLOW)
            
        def attackBeat(self, value):
            generateCircularProjectiles(projectiles, projectile_count=16, projectile_radius=5, sourceX=self.position[0], sourceY=self.position[1], angle=0, color=GREEN)
                        
        def draw(self):
            pygame.draw.circle(surface=self.screen, color=self.color, center=(self.position[0], self.position[1]), radius=self.radius)
        
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

    def hitDetected(targetX, targetY, targetRadius, projectileX, projectileY, projectileRadius, threshold_var):
        distance = math.sqrt((targetX - projectileX) ** 2 + (targetY - projectileY) ** 2)
        threshold = (targetRadius * threshold_var) + projectileRadius
        # threshold = projectileRadius
        if threshold > distance:
            return True
        else:
            return False

    heart_image = pygame.image.load('heart.png')
    heart_width = 32
    def drawLives(lives):
        for i in range(lives):
            x = i * (heart_width + 5) 
            y = SCREEN_HEIGHT - heart_width  
            screen.blit(heart_image, (x, y)) 

    def drawProjectiles():
        for projectile in projectiles:
            projectile.draw(screen, projectile.radius)
            projectile.update()
            
        for playerProjectile in playerProjectiles:
            playerProjectile.draw(screen, playerProjectile.radius)
            playerProjectile.update()
                                          
    projectiles = []
    playerProjectiles = []
    player1 = Player(screen, 10, PLAYERCOLOR, (SCREENWIDTH / 2), (SCREENHEIGHT * 0.9), 0)
    
    game_over = False
    game_over_duration = 5000
    
    default_font = pygame.font.Font(pygame.font.get_default_font(), 75)
    final_score_font = pygame.font.Font(pygame.font.get_default_font(), 50)
    current_score_font = pygame.font.Font(pygame.font.get_default_font(), 25)
    game_over_text = default_font.render('GAME OVER', True, (255, 255, 255))
    start_time = pygame.time.get_ticks()
    win_text = default_font.render('STAGE CLEAR!', True, (255, 255, 255))
    
    gameTimeThing = True # goofy hack for game over condition
    
    enemy = Enemy(screen=screen, enemyRadius=20, enemyColor=ENEMYCOLOR)
    hitsound = pygame.mixer.Sound('hitsound.mp3')
    enemyHitsound = pygame.mixer.Sound('enemyHitsound.mp3')
    
    attack_start_time_ms = pygame.time.get_ticks()
    
    smoothingFactor = 7
    bassChoppy, midsChoppy, highsChoppy = audio_time_magnitude(music_path)
    bass, mids, highs = equalizeArrays(smoothData(bassChoppy, smoothingFactor), smoothData(midsChoppy, smoothingFactor), smoothData(highsChoppy, smoothingFactor))
    
    bassIndex, midsIndex, highsIndex = 0, 0, 0 
    bassValue, midsValue, highsValue = 0, 0, 0
    bassLength = len(bass) - 1
    midsLength = len(mids) - 1
    highsLength = len(highs) - 1
    search_range = 3

    final_score = 0
    win_condition = False

    # main loop---------------------------------------------------------------------------------------------------------------------------------------------------
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        if bassIndex >= bassLength or midsIndex >= midsLength or highsIndex >= highsLength:
            win_condition = True
            game_over = True
        
        if not game_over:
            playerInput(MOVEMENTSPEED, player1)
            playerScreenLock(player1)
            screen.fill((0, 0, 0))  
            
            plane_verts = create_vertex_groups(PLANE_SIZE, SUBDIVISIONS, bassValue, midsValue, highsValue)
            draw_edges(screen, plane_verts)
            
        # hit detection and kill projectile on exiting screen
            for projectile in projectiles:
                if hitDetected(player1.playerLocX, player1.playerLocY, player1.playerRadius, projectile.x, projectile.y, projectile.radius, 0.2):
                    projectiles.remove(projectile)
                    LIVES -= 1
                    hitsound.play()
                if (projectile.x < -100 
                    or projectile.x > SCREENWIDTH + 100 
                    or projectile.y < -100 
                    or projectile.y > SCREENHEIGHT + 100):
                    projectiles.remove(projectile)
                    
        # enemy hit detection and kill projectile on exiting screen
            for projectile in playerProjectiles:
                if hitDetected(enemy.position[0], enemy.position[1], enemy.radius, projectile.x, projectile.y, projectile.radius, 1):
                    playerProjectiles.remove(projectile)
                    SCORE += 100
                    enemyHitsound.play()
                if (projectile.x < -100 
                    or projectile.x > SCREENWIDTH + 100 
                    or projectile.y < -100 
                    or projectile.y > SCREENHEIGHT + 100):
                    playerProjectiles.remove(projectile)
            

        # enemy movement
            enemy_current_time = pygame.time.get_ticks()
            if enemy_current_time - start_time >= ENEMYUPDATEDELAY:
                enemy.target = pygame.Vector2(random.randint(50, SCREENWIDTH - 50), random.randint(100, SCREENHEIGHT * 0.3))
                start_time = enemy_current_time
            
        # ememy attacks
            attackCurrentTime = pygame.time.get_ticks() - attack_start_time_ms

            while bassIndex < len(bass) and (bass[bassIndex][0] * 1000) <= attackCurrentTime - TIMINGOFFSET:
                bassIndex += 1
            if bassIndex < len(bass):
                bassValue = bass[bassIndex][1]

            while midsIndex < len(mids) and (mids[midsIndex][0] * 1000) <= attackCurrentTime - TIMINGOFFSET:
                midsIndex += 1
            if midsIndex < len(mids):
                midsValue = mids[midsIndex][1]

            while highsIndex < len(highs) and (highs[highsIndex][0] * 1000) <= attackCurrentTime - TIMINGOFFSET:
                highsIndex += 1
            if highsIndex < len(highs):
                highsValue = highs[highsIndex][1]
                        

            if highsIndex - search_range >= 0 and highsValue > HIGHSVOLUMETHRESHOLD:
                start_index = max(highsIndex - search_range, 0)
                end_index = min(highsIndex - 1, len(highs) - 1)  # Ensure end_index is within array bounds
                if highs[highsIndex][1] > max(highs[start_index:end_index], key=lambda x: x[1])[1]:
                    if highsIndex + 1 < len(highs) and highs[highsIndex][1] >= max(highs[highsIndex + 1:highsIndex + search_range], key=lambda x: x[1])[1]:
                        enemy.attackHighs(highsValue)
                        print("----------------------------------------------%%%%%%%%%%%%%%%%%%%%")

            if midsIndex - search_range >= 0 and midsValue > MIDSVOLUMETHRESHOLD:
                start_index = max(midsIndex - search_range, 0)
                end_index = min(midsIndex - 1, len(mids) - 1)  # Ensure end_index is within array bounds
                if mids[midsIndex][1] > max(mids[start_index:end_index], key=lambda x: x[1])[1]:
                    if midsIndex + 1 < len(mids) and mids[midsIndex][1] >= max(mids[midsIndex + 1:midsIndex + search_range], key=lambda x: x[1])[1]:
                        enemy.attackMids(midsValue)
                        print("---------------------%%%%%%%%%%%%%%%%%%%------------------------")

            if bassIndex - search_range >= 0 and bassValue > BASSVOLUMETHRESHOLD:
                start_index = max(bassIndex - search_range, 0)
                end_index = min(bassIndex - 1, len(bass) - 1)  # Ensure end_index is within array bounds
                if bass[bassIndex][1] > max(bass[start_index:end_index], key=lambda x: x[1])[1]:
                    if bassIndex + 1 < len(bass) and bass[bassIndex][1] >= max(bass[bassIndex + 1:bassIndex + search_range], key=lambda x: x[1])[1]:
                        enemy.attackBass(bassValue)
                        print("%%%%%%%%%%%%%%%%---------------------------------------------")

                
            print(f"Bass: {bassValue:.2f}    Mids: {midsValue:.2f}    Highs: {highsValue:.2f}", end="\r")
            
            drawProjectiles()
            drawLives(LIVES)    
            
            enemy.update()
            enemy.draw()
            
            player1.draw() 
            
            current_score_text = current_score_font.render(f'{SCORE}', True, (255, 255, 255), (0,0,0))
            screen.blit(current_score_text, (SCREENWIDTH - current_score_text.get_width(), SCREENHEIGHT - current_score_text.get_height()))
            
            if LIVES <= 0:
                game_over = True
        
    # game over condition  
        else:
            screen.fill((0,0,0))
            
            if win_condition:
                screen.blit(win_text, (SCREENWIDTH // 2 - win_text.get_width() // 2, SCREENHEIGHT // 2 - win_text.get_height() // 2))
            else:
                screen.blit(game_over_text, (SCREENWIDTH // 2 - game_over_text.get_width() // 2, SCREENHEIGHT // 2 - game_over_text.get_height() // 2))
                
            final_score_text = final_score_font.render(f'Final score: {final_score}', True, (255, 255, 255))
            screen.blit(final_score_text, (SCREENWIDTH // 2 - final_score_text.get_width() // 2, SCREENHEIGHT // 2 - final_score_text.get_height() // 2 + 100))
            current_time = pygame.time.get_ticks()
            # pygame.mixer.music.stop()
            
            if gameTimeThing:
                final_score = SCORE
                start_time = current_time
                gameTimeThing= False
                
            if current_time - start_time >= game_over_duration:
                running = False
                 
        pygame.display.flip()
                
        clock.tick(60)
        deltaTime = clock.tick(60) / 1000
        
    pygame.mixer.music.stop()
    pygame.quit()

mainMenu()