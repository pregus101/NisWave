# =============================================================================
# NisWave Music Player UI
# A music player interface built with Pygame featuring folder navigation,
# track selection, and album cover display
# =============================================================================

import pygame
import os
import threading
from pynput import keyboard
from screeninfo import get_monitors
import sys
from platformdirs import user_music_dir
from pathlib import Path
from get_metadata import image_get, get_artist
from get_files import get_drives, scroll_files_and_directories, search, find_offset_to_file, get_music_files_and_directories
from Song_Bar import SongBar
from input_handler import Inputs
from volume_worker import volume_manager
import shutil

from typing import Any


# Get monitor information and extract screen dimensions
primary_monitor = [mon for mon in get_monitors() if mon.is_primary][0]    

# Set default screen size to primary monitor dimensions
screen = pygame.display.set_mode((primary_monitor.width, primary_monitor.height), pygame.RESIZABLE)
pygame.display.set_caption("pregus101's NisWave app")

# Initialize Pygame and font
pygame.init()
pygame.mixer.init()  # Initialize mixer for audio playback
pygame.font.init()  # Initialize font module and load custom font
font = pygame.font.Font(os.path.join(os.path.dirname(__file__), Path("assets/NotoSansJP-Regular.ttf")), 25)


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

drives: list[Path] = get_drives()

multi_drives = False
if len(drives) > 1:
    multi_drives = True
    print(drives)

if not os.path.exists(folder_path):
    for drive in drives:
        new_folder: str = str(drive) + folder_path[3:]
        if os.path.exists(new_folder):
            og_folder: str = new_folder
            folder: str = new_folder
            break
    if not os.path.exists(folder_path):
        new_folder = str(drives[0])
        og_folder = new_folder
        folder = new_folder

class DriveSwitch:
    def __init__(self, og: str) -> None:
        self.index: int = 0
        if oper == "mac":
            self.index = drives.index(Path("/Volumes/Macintosh HD"))
        if oper == "windows":
            self.index = int(drives.index(Path(folder_path).drive+"\\")) # type: ignore
            self.defualt: str = og[3:]
        else:
            self.defualt = og[1:]
        self.defualt2 = "/music"
    
    def switchDrive(self, direction: int) -> str:
        self.index += direction
        if self.index < 0:
            self.index = len(drives)-1
        if self.index > len(drives):
            self.index = 0

        if os.path.exists(str(drives[self.index])+ self.defualt):
            return str(drives[self.index]) + self.defualt
            
        elif oper == "mac" and str(drives[self.index]) == "/Volumes/Macintosh HD":
                return user_music_dir()
            
        elif os.path.exists(str(drives[self.index])+ self.defualt2):
            return str(drives[self.index])+ self.defualt2
        else:
            return str(drives[self.index])

drive_handler = DriveSwitch(folder_path)

print("Drives found:", drives)

# Set up media inputs
global media_input
media_input: list[Any] = []
data_lock: threading.Lock = threading.Lock()

def on_press(key: Any) -> None:
    global media_input
    with data_lock:
        if key != keyboard.Key.caps_lock:
            print(key)
            media_input.append(key) # type: ignore

def listening():
    with keyboard.Listener(on_press=on_press) as listener: # type: ignore
        listener.join()

listener_thread = threading.Thread(target=listening)
listener_thread.daemon = True  # Make it a daemon thread so it exits when main thread exits
# if oper == "windows" or oper == "linux":
listener_thread.start()


# Set up button rate limit
last_button_press_time = 0
button_press_cooldown = 0.5  # Cooldown time in seconds

directory_only, files_only, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(folder_path, screen.get_height(), folder_path)

current_dir = og_folder

# set up class instances
image_handler = image_get(screen, 720)
player = Inputs(folder_path)
player.queue = files_only.copy()

# Scroll state variables
dir_scroll_offset = 0  # Vertical offset for directories
file_scroll_offset = 0  # Vertical offset for files
dir_scroll_speed = 20  # Speed of scrolling for directories
file_scroll_speed = 20  # Speed of scrolling for files
dir_scoll_decay = 2  # Decay rate for directory scroll inertia
file_scroll_decay = 2  # Decay rate for file scroll inertia
dir_scroll_velocity = 0  # Current velocity for directory scrolling
file_scroll_velocity = 0  # Current velocity for file scrolling
file_scroll_target = 0  # Target offset for file scrolling when clicking a file

file_text = font.render("Files: ", True, (255, 255, 255))
directory_text = font.render("Directories: ", True, (255, 255, 255))

image_handler.update_size()
render_path: Path
render_size: tuple[int, int]
render_size, render_path = image_handler.default_cover("")

button_images: list[pygame.Surface] = [] 
button_images.append([pygame.image.load(os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")), os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")]) # type: ignore
button_images.append([pygame.image.load(os.path.join(os.path.dirname(__file__), "assets/shuffle_unshuffled.jpg")), os.path.join(os.path.dirname(__file__), "assets/shuffle_unshuffled.jpg")]) # type: ignore
album_cover: list[Any] = [pygame.image.load(render_path), render_path]
album_cover_rect: list[Any] = album_cover[0].get_rect()
album_cover_rect.center = (screen.get_width()/5 + (screen.get_width()-screen.get_width()/5)/2, screen.get_height()/2)

# Frame rate limiter for battery savings
clock: pygame.time.Clock = pygame.time.Clock()
FPS = 20

# set defualt button colors and define button rectangles for click detection
skip_button_color = (64, 64, 64)  # Default gray for skip button
play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")  # Default image for play/pause button
back_button_color = (64, 64, 64)  # Default gray for back button
shuffle_button_path = os.path.join(os.path.dirname(__file__), "assets/shuffle_unshuffled.jpg")  # Default image for shuffle button
previous_button_color = (64, 64, 64)  # Default gray for previous button
drive_prev_color = (64, 64, 64)  # Default gray for drive previous button
jump_to_button_color = (64, 64, 64) # Default gray for the jump to button

skip_button = pygame.Rect((screen.get_width()-screen.get_width()/5)/2+30+screen.get_width()/5, screen.get_height() - 50, 50, 20)
play_pause_button: pygame.Rect = button_images[0][0].get_rect() # type: ignore
play_pause_button.center = ((screen.get_width()-screen.get_width()/5)/2+screen.get_width()/5, screen.get_height() - 50) # type: ignore
shuffle_button: pygame.Rect = button_images[1][0].get_rect()
shuffle_button.center = ((screen.get_width()-screen.get_width()/5)/2-135+screen.get_width()/5+25, screen.get_height() - 50) # type: ignore
previous_button = pygame.Rect((screen.get_width()-screen.get_width()/5)/2-80+screen.get_width()/5, screen.get_height() - 50, 50, 20)
drive_prev_button = pygame.Rect((screen.get_width()/5 + 10), (screen.get_height()/60), 25, 40)
back_button = pygame.Rect(screen.get_width()/5-40, 5, 20, 20)
jump_to_button = pygame.Rect(screen.get_width()/5+20, screen.get_height()-50, 50, 20)

typing_box = pygame.Rect(90, screen.get_height()/2, 250*(screen.get_width()/1920), 40)

volume = volume_manager(screen, primary_monitor.width, primary_monitor.height)
album_handler = image_get(screen, 640)
visualizer = None

typing = False
search_query = ""

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
        visualizer = player.next(bar = song_length_bar)
        render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))

    # draw background and UI elements
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, screen.get_width()/5, screen.get_height()/2))
    pygame.draw.rect(screen, (40, 40, 40), (0, screen.get_height()/2, screen.get_width()/5, screen.get_height()/2)) 

    if dir_scroll_velocity != 0:
        dir_scroll_offset += dir_scroll_velocity
        dir_scroll_velocity *= (1 - dir_scoll_decay / 40)  # Apply decay to the velocity
        if abs(dir_scroll_velocity) < 0.1:  # Stop scrolling when velocity is low
            dir_scroll_velocity = 0

        dir_scroll_offset = max(0, min(dir_scroll_offset, max(0, len(directory_only) * 40 - (screen.get_height()/2 - 60))))  # Clamp to valid scroll range

        directory_buttons, file_buttons = scroll_files_and_directories(dir_scroll_offset, file_scroll_offset, directory_buttons, file_buttons, screen.get_height(), directory_only, files_only)
        
    # if file_scroll_velocity != 0:
    #     file_scroll_offset += file_scroll_velocity
    #     file_scroll_velocity *= (1 - file_scroll_decay / 20)  # Apply decay to the velocity
    #     if abs(file_scroll_velocity) < 0.1:  # Stop scrolling when velocity is low
    #         file_scroll_velocity = 0

    #     file_scroll_offset = max(0, min(file_scroll_offset, max(0, len(files_only) * 40 - (screen.get_height()/2 - 60))))  # Clamp to valid scroll range
        
    #     directory_buttons, file_buttons = scroll_files_and_directories(dir_scroll_offset, file_scroll_offset, directory_buttons, file_buttons, screen.get_height(), DIRECTORY_ONLY, files_only)

    lerp_speed = 0.4
    
    if abs(file_scroll_target - file_scroll_offset) > 0.5:
        file_scroll_offset += (file_scroll_target - file_scroll_offset) * lerp_speed
        # Update the button positions based on the new animated offset
        directory_buttons, file_buttons = scroll_files_and_directories(
            dir_scroll_offset, file_scroll_offset, directory_buttons, file_buttons, 
            screen.get_height(), directory_only, files_only
        )
    else:
        file_scroll_offset = file_scroll_target

    if file_scroll_velocity != 0:
        file_scroll_target += file_scroll_velocity
        file_scroll_velocity *= (1 - file_scroll_decay / 20)
        if abs(file_scroll_velocity) < 0.1:
            file_scroll_velocity = 0

        file_scroll_target = max(0, min(file_scroll_target, max(0, len(files_only) * 40 - (screen.get_height()/2 - 60))))

    for button in directory_buttons:
        button_rect = pygame.Rect(0, button[0], screen.get_width()/5, 40)
        pygame.draw.rect(screen, (40, 40, 40), button_rect)
        text_surface = font.render(button[1], True, (255, 255, 255))
        screen.blit(text_surface, (10, button[0]+5))

    for button in file_buttons:
        button_rect = pygame.Rect(0, button[0], screen.get_width()/5, 40)
        pygame.draw.rect(screen, (40, 40, 40), button_rect)
        if player.playing_song != button[1][:-4]:
             text_surface = font.render(button[1], True, (255, 255, 255))
        else:             text_surface = font.render(button[1], True, (64, 255, 64))  # Highlight currently playing song in red
        screen.blit(text_surface, (10, button[0]+5))

    pygame.draw.rect(screen, (40, 40, 40), (0, 0, screen.get_width()/5, 40))
    pygame.draw.rect(screen, (40, 40, 40), (0, screen.get_height()/2-40, screen.get_width()/5, 80))

    screen.blit(directory_text, (10, 10))
    screen.blit(file_text, (10, screen.get_height()/2))

    try:
        # Draw scrollbars
        dir_max_scroll = max(0, len(directory_only) * 40 - (screen.get_height()/2 - 60))
        if dir_max_scroll > 0:
            scrollbar_h = (screen.get_height()/2 - 60) * (screen.get_height()/2 - 60) / (len(directory_only) * 40)
            scrollbar_y = dir_scroll_offset * (screen.get_height()/2 - 60) / (len(directory_only) * 40)
            pygame.draw.rect(screen, (100, 100, 100), 
                            (screen.get_width()/5 - 10, scrollbar_y, 8, scrollbar_h))

        file_max_scroll = max(0, len(files_only) * 40 - (screen.get_height()/2 - 60))
        if file_max_scroll > 0:
            scrollbar_h = (screen.get_height()/2 - 60) * (screen.get_height()/2 - 60) / (len(files_only) * 40)
            scrollbar_y = file_scroll_offset * (screen.get_height()/2 - 60) / (len(files_only) * 40)
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
        if visualizer:
            visualizer.set_color_from_image(render_path)

    screen.blit(playing_text, playing_rect)
    screen.blit(artist_text, artist_rect)

    if button_images[0][1] != play_pause_button_path:
        button_images[0][0] = pygame.image.load(play_pause_button_path)
        button_images[0][1] = play_pause_button_path

    if button_images[1][1] != shuffle_button_path:
        button_images[1][0] = pygame.image.load(shuffle_button_path)
        button_images[1][1] = shuffle_button_path

    screen.blit(button_images[0][0], play_pause_button)
    screen.blit(button_images[1][0], shuffle_button)
    pygame.draw.rect(screen, skip_button_color, skip_button)
    pygame.draw.rect(screen, previous_button_color, previous_button)
    pygame.draw.rect(screen, drive_prev_color, drive_prev_button)
    pygame.draw.rect(screen, back_button_color, back_button)
    pygame.draw.rect(screen, jump_to_button_color, jump_to_button)

    pygame.draw.rect(screen, (20, 20, 20), typing_box)

    if search_query != "" or typing:
        search_text = font.render(search_query, True, (255, 255, 255))
        search_rect = search_text.get_rect(topleft=(typing_box.x + 5, typing_box.y + 5))
        if search_rect.width > typing_box.width - 10:  # If text is too wide, trim it
            temp_query = search_query
            while search_rect.width > typing_box.width - 10:  # If text is too wide, trim it
                temp_query = temp_query[1:]
                search_text = font.render(temp_query, True, (255, 255, 255))
                search_rect = search_text.get_rect(topleft=(typing_box.x + 5, typing_box.y + 5))
        screen.blit(search_text, search_rect)
    else:
        hint_text = font.render("Search...", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(topleft=(typing_box.x + 5, typing_box.y))
        screen.blit(hint_text, hint_rect)

    volume.draw()

    song_length_bar.update(current_length=player.visualizer.get_position() if player.visualizer else 0)

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
                    shuffle_button_path = os.path.join(os.path.dirname(__file__), "assets/shuffle_shuffled_hover.jpg")  # Highlight shuffled image on hover
                else:
                    shuffle_button_path = os.path.join(os.path.dirname(__file__), "assets/shuffle_unshuffled_hover.jpg")
            else:
                if player.shuffled:
                    shuffle_button_path = os.path.join(os.path.dirname(__file__), "assets/shuffle_shuffled.jpg")
                else:
                    shuffle_button_path = os.path.join(os.path.dirname(__file__), "assets/shuffle_unshuffled.jpg")  # Default image

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

                if typing_box.collidepoint(mouse_pos):
                    typing = True
                else:
                    typing = False

                if jump_to_button.collidepoint(mouse_pos):
                    if player.playing_song != "None" and player.playing_song != "":
                        file_scroll_target = find_offset_to_file(player.playing_song, screen, files_only)

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
                        directory_only, files_only, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(player.currently_dir, screen.get_height(), og_folder)
                        player.unshuffled = files_only.copy()
                        player.queue = files_only.copy()
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
                        shuffle_button_path = os.path.join(os.path.dirname(__file__), "assets/shuffle_unshuffled_hover.jpg")
                    else:
                        shuffle_button_path = os.path.join(os.path.dirname(__file__), "assets/shuffle_shuffled_hover.jpg")
                    player.shuffle()

                if previous_button.collidepoint(mouse_pos):
                    visualizer = player.previous(song_length_bar)
                    if visualizer:
                        render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))

                if drive_prev_button.collidepoint(mouse_pos):
                    drives = get_drives()
                    new_folder = drive_handler.switchDrive(-1)
                    directory_only, files_only, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(new_folder, screen.get_height(), og_folder)
                    current_dir = og_folder
                    if not(player.playing) and (player.playing_song == "None" or player.playing_song == ""):
                        player.queue = files_only.copy()
                        player.currently_dir = current_dir

                if back_button.collidepoint(mouse_pos):
                    new_folder = Path(og_folder).parent
                    directory_only, files_only, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(new_folder, screen.get_height(), og_folder)
                    current_dir = og_folder
                    if not(player.playing) and (player.playing_song == "None" or player.playing_song == ""):
                        player.queue = files_only.copy()
                        player.currently_dir = current_dir

                for button in directory_buttons:
                    button_rect = pygame.Rect(0, button[0], screen.get_width()/5, 40)
                    if button_rect.collidepoint(mouse_pos):
                        new_folder = os.path.join(og_folder, button[1])
                        directory_only, files_only, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(new_folder, screen.get_height(), og_folder)
                        if (player.playing_song == "None" or player.playing_song == ""):
                            player.queue = files_only.copy()
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

                        if search_query != "":
                            search_query = ""
                            filtered_files = files_only.copy()
                            file_buttons = [(screen.get_height()/2+(filtered_files.index(file)+1)*40, file) for i, file in enumerate(filtered_files)]

                            file_scroll_target = find_offset_to_file(button[1], screen, files_only)

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
            shuffle_button.center = ((screen.get_width()-screen.get_width()/5)/2-135+screen.get_width()/5+25, screen.get_height() - 50)
            previous_button.topleft = ((screen.get_width()-screen.get_width()/5)/2-80+screen.get_width()/5, screen.get_height() - 50)
            jump_to_button.topleft = (screen.get_width()/5+20, screen.get_height()-50)
            render_size, render_path = album_handler.update_size()
            typing_box.topleft = (90, screen.get_height()/2)
            typing_box.width = 250*(screen.get_width()/1920)
            album_cover[0] = pygame.image.load(render_path)
            album_cover[1] = render_path
            album_cover_rect = album_cover[0].get_rect()
            album_cover_rect.center = (screen.get_width()/5 + (screen.get_width()-screen.get_width()/5)/2, screen.get_height()/2)
            player.update_size(render_size)
            playing_song = ""
            song_length_bar.resize(screen.get_width(), screen.get_height())
            directory_buttons, file_buttons = scroll_files_and_directories(dir_scroll_offset, file_scroll_offset, directory_buttons, file_buttons, screen.get_height(), directory_only, files_only)

        if event.type == pygame.MOUSEWHEEL:
            if mouse_pos[0] <= screen.get_width()/5:  # Only scroll if mouse is within the directory/file section
                if mouse_pos[1] < screen.get_height()/2:  # Directory section
                    dir_scroll_offset = max(0, min(dir_scroll_offset, 
                                                   max(0, len(directory_only) * 40 - (screen.get_height()/2 - 60))))
                    dir_scroll_velocity = -event.y * 4  # Set velocity for inertia effect
                else:  # File section
                    file_scroll_offset = max(0, min(file_scroll_offset,
                                                    max(0, len(files_only) * 40 - (screen.get_height()/2 - 60))))

                    file_scroll_velocity = -event.y * 4  # Set velocity for inertia effect
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not typing:
                if player.playing_song != "None" and player.playing_song != "":
                    player.pause()
                    if player.playing:
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")
                    else:
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")
                else:
                    player.currently_dir = current_dir
                    directory_only, files_only, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(player.currently_dir, screen.get_height(), og_folder)
                    player.unshuffled = files_only.copy()
                    player.queue = files_only.copy()
                    if player.shuffled:
                        player.shuffled = False
                        player.shuffle()
                    visualizer = player.pause(bar = song_length_bar)
                    if player.playing:
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause_hover.jpg")
                    if visualizer:
                        render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))

            else:
                if event.key == pygame.K_BACKSPACE and typing:
                    search_query = search_query[:-1]
                    filtered_files = search(files_only, search_query)
                    file_buttons = [(screen.get_height()/2+(filtered_files.index(file)+1)*40, file) for i, file in enumerate(filtered_files)]
                elif event.key == pygame.K_RETURN and typing:
                    if len(file_buttons) > 0:
                        selected_file = file_buttons[0][1]  # Get the first file in the filtered list
                        visualizer = player.play(os.path.join(current_dir, selected_file), bar = song_length_bar)
                        render_size, render_path = album_handler.update_size()
                        render_size, render_path = album_handler.update_image(os.path.join(current_dir, selected_file))  
                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")

                        typing = False
                        search_query = ""
                        file_buttons = [(screen.get_height()/2+(files_only.index(file)+1)*40, file) for i, file in enumerate(files_only)]

                        file_scroll_target = find_offset_to_file(selected_file, screen, files_only)


                        
                elif event.key == pygame.K_ESCAPE and typing:
                    typing = False
                    search_query = ""
                    filtered_files = files_only.copy()
                    file_buttons = [(screen.get_height()/2+(filtered_files.index(file)+1)*40, file) for i, file in enumerate(filtered_files)]
                elif typing:
                    search_query += event.unicode
                    filtered_files = search(files_only, search_query)
                    file_buttons = [(screen.get_height()/2+(filtered_files.index(file)+1)*40, file) for i, file in enumerate(filtered_files)]
                    
    with data_lock:
        input_key = media_input[0] if media_input else None
        media_input = media_input[1:]

    if input_key:
        if input_key == keyboard.Key.media_play_pause:
            if player.playing_song != "None" and player.playing_song != "":
                player.pause()
                if player.playing:
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")
                else:
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")
            else:
                player.currently_dir = current_dir
                directory_only, files_only, directory_buttons, file_buttons, og_folder = get_music_files_and_directories(player.currently_dir, screen.get_height(), og_folder)
                player.unshuffled = files_only.copy()
                player.queue = files_only.copy()
                if player.shuffled:
                    player.shuffled = False
                    player.shuffle()
                visualizer = player.play(bar = song_length_bar)
                if player.playing:
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")
                if visualizer:
                    render_size, render_path = album_handler.update_image(os.path.join(player.currently_dir, player.queue[player.index]))


shutil.rmtree(os.path.join(os.path.dirname(__file__), "main_cover_art/"))
sys.exit()