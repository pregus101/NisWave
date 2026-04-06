# =============================================================================
# NisWave Music Player UI
# A music player interface built with Pygame featuring folder navigation,
# track selection, and album cover display
# =============================================================================

import pygame
import os
import threading
from pynput.keyboard import Key, Listener
from screeninfo import get_monitors
import sys
from platformdirs import user_music_dir
from pathlib import Path
from get_files import get_music_files_and_directories
from get_metadata import image_get
from get_metadata import get_artist
from wave_renderer import WaveVisualizer 
from get_files import get_drives
from Song_Bar import SongBar
from input_handler import Inputs
from volume_worker import volume_manager
import time
import random
import shutil

# Get monitor information and extract screen dimensions
monitors = str(get_monitors())
temp = monitors.split("[Monitor(x=0, y=0, width=")
temp = temp[1].split("height=")
temp = temp[0] + temp[1]
temp = temp.split(", width_mm=")
temp = temp[0]
temp = temp.split(", ")

# Extract and store screen dimensions
default_screen_size = []
for i in range(0, len(temp)):
    default_screen_size.append(int(temp[i]))
screen = None
screen = pygame.display.set_mode((default_screen_size[0], default_screen_size[1]), pygame.RESIZABLE)
pygame.display.set_caption("pregus101's NisWave app")

# Set up media inputs
global media_input
media_input = []
data_lock = threading.Lock()

def on_press(key):
    global media_input
    with data_lock:
        media_input.append(key)

def listening():
    # Start the listener
    # The listener runs in a separate thread, use .join() to prevent the script from exiting immediately
    with Listener(on_press=on_press) as listener:
        listener.join()

listener_thread = threading.Thread(target=listening)
listener_thread.daemon = True  # Make it a daemon thread so it exits when main thread exits
# listener_thread.start()

# Set up button rate limit
last_button_press_time = 0
button_press_cooldown = 0.5  # Cooldown time in seconds

# Initialize Pygame and font
pygame.init()
pygame.mixer.init()  # Initialize mixer for audio playback
pygame.font.init()  # Initialize font module and load custom font
font = pygame.font.SysFont(os.path.join(os.path.dirname(__file__), "/assets/Cyberbit.ttf"), 30)

# get folder and file information for the initial directory
folder_path = user_music_dir()

oper = ""
# Get other drives
if sys.platform.startswith('win'):
    # print("Running on Windows")
    oper = "windows"
elif sys.platform.startswith('linux'):
    # print("Running on Linux")
    oper = "linux"
elif sys.platform == 'darwin':
    # print("Running on macOS")
    oper = "mac"
else:
    # print("Unknown OS")
    oper = "default"

DRIVES = get_drives(oper)

multi_drives = False
if len(DRIVES) > 1:
    multi_drives = True
    print(DRIVES)

if not os.path.exists(folder_path):
    for drive in DRIVES:
        new_folder = drive + folder_path[1:]
        if os.path.exists(new_folder):
            og_folder = new_folder
            folder = new_folder
            break
    if not os.path.exists(folder_path):
        new_folder = DRIVES[0]
        og_folder = new_folder
        folder = new_folder

class DriveSwitch:
    def __init__(self, og):
        self.index = 0
        if oper == "mac":
            self.index = DRIVES.index(Path("/Volumes/Macintosh HD"))
        self.defualt = og[1:]
        self.defualt2 = "/music"
    
    def switchDrive(self, direction):
        self.index += direction
        if self.index < 0:
            self.index = len(DRIVES)-1
        if self.index > len(DRIVES):
            self.index = 0

        if os.path.exists(str(DRIVES[self.index])+ self.defualt):
            return str(DRIVES[self.index]) + self.defualt
            
        elif oper == "mac" and str(DRIVES[self.index]) == "/Volumes/Macintosh HD":
                return user_music_dir()
            
        elif os.path.exists(str(DRIVES[self.index])+ self.defualt2):
            return str(DRIVES[self.index])+ self.defualt2
        else:
            return DRIVES[self.index]

print(folder_path)

drive_handler = DriveSwitch(folder_path)

print("Drives found:", DRIVES)

DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(folder_path, screen.get_height(), folder_path)

current_dir = og_folder

# set up class instances
image_handler = image_get(screen, 720)
player = Inputs(folder_path)
player.queue = FILES_ONLY.copy()

# Scroll state variables
dir_scroll_offset = 0  # Vertical offset for directories
file_scroll_offset = 0  # Vertical offset for files

image_handler.update_size()
render_size, render_path = image_handler.default_cover("")

button_images = []
button_images.append([pygame.image.load(os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")), os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")])
album_cover = [pygame.image.load(render_path), render_path]
album_cover_rect = album_cover[0].get_rect()
album_cover_rect.center = (screen.get_width()/5 + (screen.get_width()-screen.get_width()/5)/2, screen.get_height()/2)

# Frame rate limiter for battery savings
clock = pygame.time.Clock()
FPS = 20

# set defualt button colors and define button rectangles for click detection
skip_button_color = (64, 64, 64)  # Default gray for skip button
play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")  # Default image for play/pause button
back_button_color = (64, 64, 64)  # Default gray for back button
shuffle_button_color = (64, 64, 64)  # Default gray for shuffle button
previous_button_color = (64, 64, 64)  # Default gray for previous button
drive_prev_color = (64, 64, 64)  # Default gray for drive previous button

skip_button = pygame.Rect((screen.get_width()-screen.get_width()/5)/2+30+screen.get_width()/5, screen.get_height() - 50, 50, 20)
play_pause_button = button_images[0][0].get_rect()
play_pause_button.center = ((screen.get_width()-screen.get_width()/5)/2+screen.get_width()/5, screen.get_height() - 50)
shuffle_button = pygame.Rect((screen.get_width()-screen.get_width()/5)/2-135+screen.get_width()/5, screen.get_height() - 50, 50, 20)
previous_button = pygame.Rect((screen.get_width()-screen.get_width()/5)/2-80+screen.get_width()/5, screen.get_height() - 50, 50, 20)
drive_prev_button = pygame.Rect((screen.get_width()/5 + 10), (screen.get_height()/60), 25, 40)
back_button = pygame.Rect(screen.get_width()/5-40, 5, 20, 20)
volume = volume_manager(screen, default_screen_size[0], default_screen_size[1])
album_handler = image_get(screen, 640)
visualizer = None

song_length_bar = SongBar(0, 0, screen.get_width(), screen.get_height(), screen, None)

dragging = False

running = True

playing_song = "None"
playing_text = font.render(playing_song, True, (255, 255, 255))
playing_rect = playing_text.get_rect(center=((screen.get_width()-screen.get_width()/5)// 2+screen.get_width()/5, screen.get_height() // 2+render_size[1]/2+20))

artist = "Unknown Artist"
artist_text = font.render(artist, True, (255, 255, 255))
artist_rect = artist_text.get_rect(center=((screen.get_width()-screen.get_width()/5)// 2+screen.get_width()/5, screen.get_height() // 2+render_size[1]/2+50))

while running:

    mouse_pos = pygame.mouse.get_pos()

    if not(pygame.mixer_music.get_busy()) and player.playing:
        player.next(bar = song_length_bar)
        render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))

    # draw background and UI elements
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, screen.get_width()/5, screen.get_height()/2))
    pygame.draw.rect(screen, (40, 40, 40), (0, screen.get_height()/2, screen.get_width()/5, screen.get_height()/2)) 

    for button in directory_buttons:
        button_rect = pygame.Rect(0, button[0], screen.get_width()/5, 40)
        pygame.draw.rect(screen, (40, 40, 40), button_rect)
        text_surface = font.render(button[1], True, (255, 255, 255))
        screen.blit(text_surface, (10, button[0]+5))

    for button in file_buttons:
        button_rect = pygame.Rect(0, button[0], screen.get_width()/5, 40)
        pygame.draw.rect(screen, (40, 40, 40), button_rect)
        text_surface = font.render(button[1], True, (255, 255, 255))
        screen.blit(text_surface, (10, button[0]+5))

    try:
        # Draw scrollbars
        dir_max_scroll = max(0, len(DIRECTORY_ONLY) * 40 - (screen.get_height()/2 - 60))
        if dir_max_scroll > 0:
            scrollbar_h = (screen.get_height()/2 - 60) * (screen.get_height()/2 - 60) / (len(DIRECTORY_ONLY) * 40)
            scrollbar_y = dir_scroll_offset * (screen.get_height()/2 - 60) / (len(DIRECTORY_ONLY) * 40)
            pygame.draw.rect(screen, (100, 100, 100), 
                            (screen.get_width()/5 - 10, scrollbar_y, 8, scrollbar_h))

        file_max_scroll = max(0, len(FILES_ONLY) * 40 - (screen.get_height()/2 - 60))
        if file_max_scroll > 0:
            scrollbar_h = (screen.get_height()/2 - 60) * (screen.get_height()/2 - 60) / (len(FILES_ONLY) * 40)
            scrollbar_y = file_scroll_offset * (screen.get_height()/2 - 60) / (len(FILES_ONLY) * 40)
            pygame.draw.rect(screen, (100, 100, 100), 
                            (screen.get_width()/5 - 10, screen.get_height()/2 + scrollbar_y, 8, scrollbar_h))
    except:
        print("Not enough space to draw scrollbars")

    pygame.draw.rect(screen, (20, 20, 20), (screen.get_width()/5, 0, screen.get_width()-screen.get_width()/5, screen.get_height()))  # Main background for album cover and visualizer

    if render_path != album_cover[1]:
        album_cover[0] = pygame.image.load(render_path)
        album_cover[1] = render_path
        album_cover_rect = album_cover[0].get_rect()
        album_cover_rect.center = (screen.get_width()/5 + (screen.get_width()-screen.get_width()/5)/2, screen.get_height()/2)

    screen.blit(album_cover[0], album_cover_rect)

    if playing_song != player.playing_song:
        playing_song = player.playing_song
        playing_text = font.render(player.playing_song, True, (255, 255, 255))
        playing_rect = playing_text.get_rect(center=((screen.get_width()-screen.get_width()/5)// 2+screen.get_width()/5, screen.get_height() // 2+render_size[1]/2+20))
        artist = get_artist(os.path.join(player.currently_dir, player.queue[player.index])) if player.playing_song != "None" and player.playing_song != "" else "Unknown Artist"
        artist_text = font.render(artist, True, (255, 255, 255))
        artist_rect = artist_text.get_rect(center=((screen.get_width()-screen.get_width()/5)// 2+screen.get_width()/5, screen.get_height() // 2+render_size[1]/2+50))

    screen.blit(playing_text, playing_rect)
    screen.blit(artist_text, artist_rect)

    if button_images[0][1] != play_pause_button_path:
        button_images[0][0] = pygame.image.load(play_pause_button_path)
        button_images[0][1] = play_pause_button_path

    screen.blit(button_images[0][0], play_pause_button)
    pygame.draw.rect(screen, skip_button_color, skip_button)
    pygame.draw.rect(screen, shuffle_button_color, shuffle_button)
    pygame.draw.rect(screen, previous_button_color, previous_button)
    pygame.draw.rect(screen, drive_prev_color, drive_prev_button)
    pygame.draw.rect(screen, back_button_color, back_button)

    volume.draw()

    song_length_bar.update(current_length=player.visulizer.get_position() if player.visulizer else 0)

    try:
        if visualizer != None:
            vis_surface = screen.subsurface(screen.get_width()/5+(((screen.get_width()-screen.get_width()/5)/2-render_size[0]/2)), 0,
                                            render_size[0], screen.get_height()/2+render_size[1]/2)
            
            if not visualizer.render_frame(vis_surface, mouse_pos):
                    visualizer = None

            if visualizer:
                    visualizer.update_render_size(int(render_size[0]), 
                                                int((screen.get_height()/2)+(render_size[1]/2)))
    except:
        pass


    pygame.display.flip()

    clock.tick(20)  # Limit the frame rate to save battery

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            if skip_button.collidepoint(mouse_pos):
                skip_button_color = (128, 128, 128)  # Highlight skip button on hover
            else:
                skip_button_color = (64, 64, 64)  # Default color

            if play_pause_button.collidepoint(mouse_pos):
                if player.playing:
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause_hover.jpg")  # Highlight pause image on hover
                else:
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play_hover.jpg")  # Highlight play image on hover
            else:
                if player.playing:
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Default image
                else:
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")  # Default image

            if shuffle_button.collidepoint(mouse_pos):
                if player.shuffled:
                    shuffle_button_color = (64, 255, 64) 
                else:
                    shuffle_button_color = (128, 128, 128)
            else:
                if player.shuffled:
                    shuffle_button_color = (64, 128, 64)
                else:
                    shuffle_button_color = (64, 64, 64)  # Default color

            if previous_button.collidepoint(mouse_pos):
                previous_button_color = (128, 128, 128)  # Highlight previous button on hover
            else:
                previous_button_color = (64, 64, 64)  # Default color

            if drive_prev_button.collidepoint(mouse_pos):
                drive_prev_color = (128, 128, 128)  # Highlight drive previous button on hover
            else:
                drive_prev_color = (64, 64, 64)  # Default color

            if back_button.collidepoint(mouse_pos):
                back_button_color = (128, 128, 128)  # Highlight back button on hover
            else:
                back_button_color = (64, 64, 64)  # Default color

            if dragging:
                volume.adjust_volume(mouse_pos)
                if song_length_bar:
                    song_length_bar.adjust_time(mouse_pos)


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if song_length_bar:
                    song_length_bar.adjust_time(mouse_pos)

                if skip_button.collidepoint(mouse_pos):
                    visualizer = player.next(song_length_bar)
                    if visualizer:
                        render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))
                    else:
                        render_size, render_path = album_handler.update_image()
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")

                if play_pause_button.collidepoint(mouse_pos):
                    if player.playing_song != "None" and player.playing_song != "":
                        player.pause()
                        if player.playing:
                            play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause_hover.jpg")
                        else:
                            play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play_hover.jpg")
                    else:
                        player.currently_dir = current_dir
                        DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(player.currently_dir, screen.get_height(), og_folder)
                        player.unshuffled = FILES_ONLY.copy()
                        player.queue = FILES_ONLY.copy()
                        if player.shuffled:
                            player.shuffled = False
                            player.shuffle()
                        visualizer = player.play(bar = song_length_bar)
                        if player.playing:
                            play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause_hover.jpg")
                        if visualizer:
                            render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))
                        

                if shuffle_button.collidepoint(mouse_pos):
                    if player.shuffled:
                        shuffle_button_color = (128, 128, 128)
                    else:
                        shuffle_button_color = (64, 255, 64)
                    player.shuffle()

                if previous_button.collidepoint(mouse_pos):
                    visualizer = player.previous(song_length_bar)
                    if visualizer:
                        render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))

                if drive_prev_button.collidepoint(mouse_pos):
                    DRIVES = get_drives(oper)
                    new_folder = drive_handler.switchDrive(-1)
                    DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(new_folder, screen.get_height(), og_folder)
                    current_dir = og_folder
                    if not(player.playing) and (player.playing_song == "None" or player.playing_song == ""):
                        player.queue = FILES_ONLY.copy()
                        player.currently_dir = current_dir

                if back_button.collidepoint(mouse_pos):
                    new_folder = Path(og_folder).parent
                    DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(new_folder, screen.get_height(), og_folder)
                    current_dir = og_folder
                    if not(player.playing) and (player.playing_song == "None" or player.playing_song == ""):
                        player.queue = FILES_ONLY.copy()
                        player.currently_dir = current_dir

                for button in directory_buttons:
                    button_rect = pygame.Rect(0, button[0], screen.get_width()/5, 40)
                    if button_rect.collidepoint(mouse_pos):
                        new_folder = os.path.join(og_folder, button[1])
                        DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(new_folder, screen.get_height(), og_folder)
                        if (player.playing_song == "None" or player.playing_song == ""):
                            player.queue = FILES_ONLY.copy()
                            current_dir = og_folder
                        else:
                            current_dir = og_folder

                for button in file_buttons:
                    button_rect = pygame.Rect(0, button[0], screen.get_width()/5, 40)
                    if button_rect.collidepoint(mouse_pos):
                        visualizer = player.play(os.path.join(current_dir, button[1]), bar = song_length_bar)
                        render_size, render_path = album_handler.update_size()
                        render_size, render_path = album_handler.update_image(os.path.join(current_dir, button[1]))  
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")

                volume.adjust_volume(mouse_pos)

                dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        if event.type == pygame.WINDOWRESIZED:
            volume.resize()
            drive_prev_button.topleft = (screen.get_width()/5 + 10, (screen.get_height()/60))
            back_button.topleft = (screen.get_width()/5-40, 5)
            skip_button.topleft = ((screen.get_width()-screen.get_width()/5)/2+30+screen.get_width()/5, screen.get_height() - 50)
            play_pause_button.center = ((screen.get_width()-screen.get_width()/5)/2+screen.get_width()/5, screen.get_height() - 50)
            shuffle_button.topleft = ((screen.get_width()-screen.get_width()/5)/2-135+screen.get_width()/5, screen.get_height() - 50)
            previous_button.topleft = ((screen.get_width()-screen.get_width()/5)/2-80+screen.get_width()/5, screen.get_height() - 50)
            render_size, render_path = album_handler.update_size()
            album_cover[0] = pygame.image.load(render_path)
            album_cover[1] = render_path
            album_cover_rect = album_cover[0].get_rect()
            album_cover_rect.center = (screen.get_width()/5 + (screen.get_width()-screen.get_width()/5)/2, screen.get_height()/2)
            player.update_size(render_size)
            playing_song = ""
            song_length_bar.resize(screen.get_width(), screen.get_height())

        if event.type == pygame.MOUSEWHEEL:
            if mouse_pos[0] <= screen.get_width()/5:  # Only scroll if mouse is within the directory/file section
                if mouse_pos[1] < screen.get_height()/2:  # Directory section
                    dir_scroll_offset -= event.y * 8  # Scroll by item height
                    dir_scroll_offset = max(0, min(dir_scroll_offset, 
                                                   max(0, len(DIRECTORY_ONLY) * 40 - (screen.get_height()/2 - 60))))
                else:  # File section
                    file_scroll_offset -= event.y * 8
                    file_scroll_offset = max(0, min(file_scroll_offset,
                                                    max(0, len(FILES_ONLY) * 40 - (screen.get_height()/2 - 60))))
                    
                DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(og_folder, screen.get_height(), og_folder, dir_scroll_offset, file_scroll_offset)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if player.playing_song != "None" and player.playing_song != "":
                    player.pause()
                    if player.playing:
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")
                    else:
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")
                else:
                    player.currently_dir = current_dir
                    DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(player.currently_dir, screen.get_height(), og_folder)
                    player.unshuffled = FILES_ONLY.copy()
                    player.queue = FILES_ONLY.copy()
                    if player.shuffled:
                        player.shuffled = False
                        player.shuffle()
                    visualizer = player.pause(bar = song_length_bar)
                    if player.playing:
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause_hover.jpg")
                    if visualizer:
                        render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))

shutil.rmtree(os.path.join(os.path.dirname(__file__), "main_cover_art/"))
sys.exit()

