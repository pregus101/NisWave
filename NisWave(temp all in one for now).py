import pygame
import os
from screeninfo import get_monitors
import subprocess
import sys
from platformdirs import user_music_dir
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import random

monitors = str(get_monitors())

temp = monitors.split("[Monitor(x=0, y=0, width=")
temp = temp[1].split("height=")
temp = temp[0] + temp[1]
temp = temp.split(", width_mm=")
temp = temp[0]
temp = temp.split(", ")

import os

folder_path = Path(user_music_dir())  # Get the user's music directory

def get_music_files_and_directories(folder_path):
    DIRECTORY_ONLY = [
        entry for entry in os.listdir(folder_path) 
        if os.path.isdir(os.path.join(folder_path, entry))
    ]

    directory_buttons = []

    for directory in DIRECTORY_ONLY:
        directory_buttons.append([(DIRECTORY_ONLY.index(directory)+1)*40 + 10, directory])

    supported_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
    FILES_ONLY = [
        entry for entry in os.listdir(folder_path) 
        if os.path.isfile(os.path.join(folder_path, entry)) and os.path.splitext(entry)[1].lower() in supported_formats
    ]

    file_buttons = []

    for file in FILES_ONLY:
        file_buttons.append([(len(DIRECTORY_ONLY)+FILES_ONLY.index(file)+2)*40 + 10, file])

    return DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons

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


def get_cover_art(mp3_file_path, output_dir=os.path.abspath(__file__) + "/temp_cover_art"):
    """
    Extracts the cover art from an MP3 file using the mutagen library.
    """
    try:
        # Load the MP3 file with mutagen
        audio = MP3(mp3_file_path)
        
        # Check if there are any ID3 tags
        if not audio.tags:
            print(f"No ID3 tags found in {mp3_file_path}")
            return

        # Iterate over the tags to find the album art (APIC tag)
        for tag in audio.tags.getall('APIC'):
            if isinstance(tag, APIC):
                # Ensure the output directory exists
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # Determine file extension based on image mime type
                if tag.mime == 'image/jpeg':
                    ext = 'jpg'
                elif tag.mime == 'image/png':
                    ext = 'png'
                else:
                    print(f"Unsupported image mime type: {tag.mime}")
                    continue
                
                # Create the output filename
                track_title = audio.get('TIT2', ['untitled'])[0]
                output_filename = f"{track_title.replace('/', '_')}_cover.{ext}"
                output_path = os.path.join(output_dir, output_filename)

                # Write the image data to a file
                with open(output_path, 'wb') as img_file:
                    img_file.write(tag.data)
                
                print(f"Successfully extracted cover art to: {output_path}")
                return # Stop after the first image is found
        
        print(f"No cover art (APIC tag) found in {mp3_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons = get_music_files_and_directories(folder_path)

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

    if STARTED:
        text_surface = font.render("Now Playing: " + PLAYING_SONG, True, (255, 255, 255))
        screen.blit(text_surface, ((SCREEN_WIDTH-song_select_window)/2+song_select_window-(13+len(PLAYING_SONG))*7, 10))

    pygame.display.flip()

