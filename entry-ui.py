import pygame
import os
from screeninfo import get_monitors
import sys
from platformdirs import user_music_dir
from pathlib import Path
import random
from get_files import get_music_files_and_directories
from update_image import get_cover_art

monitors = str(get_monitors())

temp = monitors.split("[Monitor(x=0, y=0, width=")
temp = temp[1].split("height=")
temp = temp[0] + temp[1]
temp = temp.split(", width_mm=")
temp = temp[0]
temp = temp.split(", ")

folder_path = Path(user_music_dir())  # Get the user's music directory

# Initialize Pygame
pygame.init()
pygame.font.init() # Initialize the font module

font = pygame.font.SysFont('Arial', 30)

default_screen_size = []

for i in range(0, len(temp)):
    default_screen_size.append(int(temp[i]))

default_width, default_height = default_screen_size

# Set up the display
SCREEN_WIDTH = default_width
SCREEN_HEIGHT = default_height
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("pregus101's NisWave app")

STARTED = False

PLAYING_SONG = ""

directory_buttons_window = pygame.Surface((SCREEN_WIDTH/5, SCREEN_HEIGHT/2))

file_buttons_window = pygame.Surface((SCREEN_WIDTH/5, SCREEN_HEIGHT/2))

while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons = get_music_files_and_directories(folder_path)

                print(SCREEN_WIDTH/5+5 <= mouse_pos[0] <= SCREEN_WIDTH/15+25 and  5 <= mouse_pos[1] <= 25)
                print(SCREEN_WIDTH/5+5, mouse_pos[0], SCREEN_WIDTH/5+25, mouse_pos[1])

                if SCREEN_WIDTH/5+5 <= mouse_pos[0] <= SCREEN_WIDTH/5+25 and  5 <= mouse_pos[1] <= 25:
                    folder_path = os.path.dirname(folder_path)
                    print("switch", folder_path)    

                for button in directory_buttons:
                    if button[0] <= mouse_pos[1] <= button[0] + 30 and mouse_pos[0] <= song_select_window:
                        folder_path = os.path.join(folder_path, button[1])
                
                for button in file_buttons:
                    if button[0] <= mouse_pos[1] <= button[0] + 30 and mouse_pos[0] <= song_select_window:
                        pygame.mixer.music.load(os.path.join(folder_path, button[1]))
                        pygame.mixer.music.play()
                        STARTED = True
                        queue.remove(button[1])
                        PLAYING_SONG = button[1]
                        get_cover_art(os.path.join(folder_path, button[1]))
    if STARTED:
        if not pygame.mixer.music.get_busy():
           newsong = queue[random.randint(0, len(queue)-1)]
           pygame.mixer.music.load(os.path.join(folder_path, newsong))
           pygame.mixer.music.play()
           queue.remove(newsong)
           PLAYING_SONG = newsong
           get_cover_art(os.path.join(folder_path, newsong))

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    song_select_window = SCREEN_WIDTH/5
    pygame.draw.rect(screen, (0, 0, 20), (0, 0, song_select_window, SCREEN_HEIGHT))

    DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons = get_music_files_and_directories(folder_path)

    queue = FILES_ONLY.copy()

    text_surface = font.render("Folders:", True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))
    for directory in DIRECTORY_ONLY:
        text_surface = font.render(directory, True, (255, 255, 255))
        screen.blit(text_surface, (10, (DIRECTORY_ONLY.index(directory)+1)*40 + 10))


    text_surface = font.render("Files:", True, (255, 255, 255))
    screen.blit(text_surface, (10, (len(DIRECTORY_ONLY)+1)*40 + 10))
    for file in FILES_ONLY:
         text_surface = font.render(file, True, (255, 255, 255))
         screen.blit(text_surface, (10, (len(DIRECTORY_ONLY) + FILES_ONLY.index(file)+2)*40 + 10))

    pygame.draw.rect(screen, (20, 0, 0), (song_select_window, 0, SCREEN_WIDTH - song_select_window, SCREEN_HEIGHT))
    pygame.draw.rect(screen, (64, 64, 64), (SCREEN_WIDTH/5+5, 5, 20, 20))

    if STARTED:
        text_surface = font.render("Now Playing: " + PLAYING_SONG, True, (255, 255, 255))
        screen.blit(text_surface, ((SCREEN_WIDTH-song_select_window)/2+song_select_window-(13+len(PLAYING_SONG))*7, 10))

    pygame.display.flip()

