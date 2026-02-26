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
from get_metadata import get_cover_art
from get_metadata import get_artist
from wave_renderer import WaveVisualizer 
from queue_handler import shuffler
from queue_handler import generated_unshuffled_queue
from Song_Bar import SongBar
from input_handler import previous
from input_handler import skip
import time
import random

# =============================================================================
# Screen Initialization
# =============================================================================

# Get monitor information and extract screen dimensions
monitors = str(get_monitors())
temp = monitors.split("[Monitor(x=0, y=0, width=")
temp = temp[1].split("height=")
temp = temp[0] + temp[1]
temp = temp.split(", width_mm=")
temp = temp[0]
temp = temp.split(", ")

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
listener_thread.start()

# Set up button rate limit (Because someone stalled my program by spamming the back button. Thanks [REDACTED] :D)
last_button_press_time = 0
button_press_cooldown = 0.5  # Cooldown time in seconds

# Initialize Pygame and font
pygame.init()
pygame.mixer.init()  # Initialize mixer for audio playback
pygame.font.init()  # Initialize font module and load custom font
font = pygame.font.SysFont(os.path.join(os.path.dirname(__file__), "Cyberbit.ttf"), 30)

# Extract and store screen dimensions
default_screen_size = []
for i in range(0, len(temp)):
    default_screen_size.append(int(temp[i]))

default_width, default_height = default_screen_size

# Get initial music directory path
folder_path = user_music_dir()
og_folder = folder_path
currently_playing_folder_path = folder_path

# Set up the display window
SCREEN_WIDTH = default_width
SCREEN_HEIGHT = default_height
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("pregus101's NisWave app")

running = True

# =============================================================================
# Application State Variables
# =============================================================================

OLD_SIZE = 640  # Previous album cover size (for resize detection)
STARTED = False  # Track whether playback has begun
PLAYING_SONG = ""  # Currently playing song filename

is_dragging = False  # State variable to track if the user is currently dragging the song length bar

current_time_ms = 0
current_time_sec = current_time_ms / 1000.0

retry = False

# Wave visualizer state
visualizer = None  # Will hold the WaveVisualizer instance
visualizer_running = False

# Create surface objects for directory and file windows
directory_buttons_window = pygame.Surface((SCREEN_WIDTH/5, SCREEN_HEIGHT/2))
file_buttons_window = pygame.Surface((SCREEN_WIDTH/5, SCREEN_HEIGHT/2))

# Set inital button states
play_pause = "play"  # Can be "play" or "pause"
shuffle = False  # Shuffle mode state

# Initialize the played songs
played_songs = {}  # Dictionary to track played songs and their indices in the queue_raw

# Scroll state variables
dir_scroll_offset = 0  # Vertical offset for directories
file_scroll_offset = 0  # Vertical offset for files

# Default cover art path (used if no cover art is found in the MP3 file)
cover_art_path = os.path.join(os.path.dirname(__file__), "assets/default_cover.jpg")  # Default cover art path

# ============================================================================
# PERFORMANCE OPTIMIZATIONS
# ============================================================================
# Image and text surface caching
button_images_cache = {}
album_cover_cache = pygame.image.load(cover_art_path)  # Cache the default cover art
text_cache = {}
metadata_cache = {}

# Frame rate limiter for battery savings
clock = pygame.time.Clock()
FPS = 30  # Reduced from 60 for significant battery savings

# set defualt button colors
skip_button_color = (64, 64, 64)  # Default gray for skip button
play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")  # Default image for play/pause button
back_button_color = (64, 64, 64)  # Default gray for back button
shuffle_button_color = (64, 64, 64)  # Default gray for shuffle button
previous_button_color = (64, 64, 64)  # Default gray for previous button

# # Create the queue for auto-playing songs (will be populated with files from the current directory)
# DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons = get_music_files_and_directories(folder_path, SCREEN_HEIGHT)
# queue = FILES_ONLY.copy()  # Initialize queue with available songs in the current directory

# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================
while running:
    # Limit frame rate for battery savings (Major optimization)
    clock.tick(FPS)
    
    # Calculate album cover size based on screen resolution for scaling
    SIZE = int(640 * ((SCREEN_WIDTH/1920 + SCREEN_HEIGHT/1147) / 2))
    mouse_pos = pygame.mouse.get_pos()
    
    # ========================================================================
    # EVENT HANDLING
    # ========================================================================
    for event in pygame.event.get():
        # Exit application when window is closed
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos  # Update mouse position on movement

            if is_dragging:
                if visualizer_running:
                    # Update the current time based on mouse position when dragging
                    adjust = SongBar(total_length, current_time_sec, SCREEN_WIDTH, SCREEN_HEIGHT, screen)
                    new_current_time = adjust.adjust_time(mouse_pos, total_length, SCREEN_WIDTH, SCREEN_HEIGHT, screen, visualizer)
                    current_time_sec = new_current_time

            # Optimized button hover detection (reduced calculations)
            def check_hover(x1, y1, x2, y2, px, py):
                return x1 <= px <= x2 and y1 <= py <= y2
            
            mx, my = mouse_pos
            shuffle_hovered = check_hover((SCREEN_WIDTH-SCREEN_WIDTH/5)/2-135+SCREEN_WIDTH/5, SCREEN_HEIGHT-50, (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-85+SCREEN_WIDTH/5, SCREEN_HEIGHT-30, mx, my)
            shuffle_button_color = (64, 255, 64) if shuffle and shuffle_hovered else (64, 128, 64) if shuffle else (128, 128, 128) if shuffle_hovered else (64, 64, 64)
            
            play_pause_hovered = check_hover((SCREEN_WIDTH-SCREEN_WIDTH/5)/2-25+SCREEN_WIDTH/5, SCREEN_HEIGHT-75, (SCREEN_WIDTH-SCREEN_WIDTH/5)/2+25+SCREEN_WIDTH/5, SCREEN_HEIGHT-25, mx, my)
            if play_pause_hovered:
                play_pause_button_path = "assets/play_pause_hover.jpg" if play_pause == "play" and STARTED else "assets/play_play_hover.jpg"
            else:
                play_pause_button_path = "assets/play_pause.jpg" if play_pause == "play" and STARTED else "assets/play_play.jpg"
            
            back_button_color = (128, 128, 128) if check_hover(SCREEN_WIDTH/5-40, 5, SCREEN_WIDTH/5-20, 25, mx, my) else (64, 64, 64)
            skip_button_color = (128, 128, 128) if check_hover((SCREEN_WIDTH-SCREEN_WIDTH/5)/2+30+SCREEN_WIDTH/5, SCREEN_HEIGHT-50, (SCREEN_WIDTH-SCREEN_WIDTH/5)/2+80+SCREEN_WIDTH/5, SCREEN_HEIGHT-30, mx, my) else (64, 64, 64)
            previous_button_color = (128, 128, 128) if check_hover((SCREEN_WIDTH-SCREEN_WIDTH/5)/2-80+SCREEN_WIDTH/5, SCREEN_HEIGHT-50, (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-30+SCREEN_WIDTH/5, SCREEN_HEIGHT-30, mx, my) else (64, 64, 64)


        # Handle mouse button clicks (folder/file selection and navigation)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and time.time() - last_button_press_time > button_press_cooldown:  # Left mouse button only
                last_button_press_time = time.time()

                is_dragging = True  # Start dragging when mouse button is pressed down
                
                if is_dragging:
                    if visualizer_running:
                        # Update the current time based on mouse position when dragging
                        adjust = SongBar(total_length, current_time_sec, SCREEN_WIDTH, SCREEN_HEIGHT, screen)
                        new_current_time = adjust.adjust_time(mouse_pos, total_length, SCREEN_WIDTH, SCREEN_HEIGHT, screen, visualizer)

                # Get current directory contents for button interaction
                
                try:
                    DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, folder_path = get_music_files_and_directories(folder_path, SCREEN_HEIGHT, og_folder, dir_scroll_offset, file_scroll_offset)
                except Exception as e:
                    DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, folder_path = get_music_files_and_directories(og_folder, SCREEN_HEIGHT, og_folder, dir_scroll_offset, file_scroll_offset)
                    print("Error accessing directory contents for button interaction:", e)

                # Check if back button was clicked (navigate to parent directory)
                if SCREEN_WIDTH/5-40 <= mouse_pos[0] <= SCREEN_WIDTH/5-20 and 5 <= mouse_pos[1] <= 25:
                    folder_path = os.path.dirname(folder_path)
                    print("Back button clicked, new folder path:", folder_path)

                # Check if skip button was clicked
                if (SCREEN_WIDTH-SCREEN_WIDTH/5)/2+30+SCREEN_WIDTH/5 <= mouse_pos[0] <= (SCREEN_WIDTH-SCREEN_WIDTH/5)/2+80+SCREEN_WIDTH/5 and SCREEN_HEIGHT-50 <= mouse_pos[1] <= SCREEN_HEIGHT-30 and visualizer_running:
                    STARTED, play_pause, play_pause_button_path = skip()
                    album_cover_cache = pygame.image.load(cover_art_path)  # Upadate album cover cache to default when skipping songs

                # Check if previous button was clicked
                if (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-80+SCREEN_WIDTH/5 <= mouse_pos[0] <= (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-30+SCREEN_WIDTH/5 and SCREEN_HEIGHT-50 <= mouse_pos[1] <= SCREEN_HEIGHT-30 and visualizer_running:
                    play_pause, played_songs, queue_raw, queue, play_pause_button_path, visualizer, STARTED, PLAYING_SONG, render_size, cover_art_path = previous(current_time_sec, currently_playing_folder_path, played_songs, queue_raw, queue, SIZE, visualizer, screen, total_length, play_pause, play_pause_button_path, visualizer_running, STARTED, PLAYING_SONG, render_size, cover_art_path, file_path)
                    album_cover_cache = pygame.image.load(cover_art_path)  # Update album cover cache with the new cover art when going to the previous song

                # Check if pause/play button was clicked
                if (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-25+SCREEN_WIDTH/5 <= mouse_pos[0] <= (SCREEN_WIDTH-SCREEN_WIDTH/5)/2+25+SCREEN_WIDTH/5 and SCREEN_HEIGHT-75 <= mouse_pos[1] <= SCREEN_HEIGHT-25:
                    if visualizer_running:
                        if play_pause == "play" and STARTED:
                            STARTED = False
                            play_pause = "pause"
                            try:
                                WaveVisualizer.set_pause_state(visualizer, True)  # Pause the visualizer
                            except:
                                pass  # Visualizer may not be initialized yet, ignore if error occurs
                            play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play_hover.jpg")  # Default image for play button
                        else:
                            STARTED = True
                            play_pause = "play"
                            
                            try:
                                WaveVisualizer.set_pause_state(visualizer, False)  # Unpause the visualizer
                            except:
                                pass  # Visualizer may not be initialized yet, ignore if error occurs
                                STARTED = False
                                visualizer_running = False
                                visualizer = None  # Reset visualizer instance when stopping playback

                            if STARTED:
                                play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause_hover.jpg")  # Default image for pause button
                    else:
                        if FILES_ONLY:
                            song_play = ""
                            if shuffle:
                                song_play = FILES_ONLY[random.randint(0, len(FILES_ONLY))]
                                queue_raw = generated_unshuffled_queue(song_play, FILES_ONLY.copy())
                                queue = shuffler(queue_raw, song_play, True)
                            else:
                                queue_raw = generated_unshuffled_queue(FILES_ONLY[0], FILES_ONLY.copy())
                                queue = queue_raw.copy()
                                song_play = FILES_ONLY[0]
                            
                            play_pause = "play"  # Reset play/pause state to "play" when a new song is selected
                            played_songs = {}  # Clear the list of played songs when a new song is selected
                            
                            # Load and play the selected file
                            file_path = os.path.join(folder_path, song_play)
                            currently_playing_folder_path = folder_path  # Update the currently playing folder path
                            STARTED = True
                            # queue_raw.remove(button[1])
                            # queue.remove(button[1])
                            PLAYING_SONG = song_play

                            # Load the sound file as a Sound object to get its length
                            temp_sound_object = pygame.mixer.Sound(file_path)
                            total_length = temp_sound_object.get_length() # Length in seconds

                            # Get image for the selected track
                            render_size, cover_art_path = get_cover_art(file_path, SIZE)
                            album_cover_cache = pygame.image.load(cover_art_path)  # Update album cover cache with the new cover art when a song is selected

                            play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Change play/pause button to hover state when a new song is selected

                            # CREATE AND START WAVE VISUALIZER
                            visualizer = WaveVisualizer(file_path, 
                                                    render_size[0], 
                                                    render_size[1])
                            # Set wave color to contrast with album cover
                            visualizer.set_color_from_image(cover_art_path)
                            visualizer.load_audio()
                            visualizer.play()
                            visualizer_running = True

                # Check if shuffle button was clicked
                if (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-135+SCREEN_WIDTH/5 <= mouse_pos[0] <= (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-85+SCREEN_WIDTH/5 and SCREEN_HEIGHT-50 <= mouse_pos[1] <= SCREEN_HEIGHT-30:
                    if not PLAYING_SONG == '':
                        if shuffle:
                            queue = generated_unshuffled_queue(PLAYING_SONG, queue_raw)
                            shuffle_button_color = (128, 128, 128)  # Change shuffle button color to indicate shuffle is off
                        else:
                            queue = shuffler(queue_raw, PLAYING_SONG)
                            shuffle_button_color = (64, 255, 64)  # Change shuffle button color to indicate shuffle is on

                    shuffle = not shuffle  # Toggle shuffle state

                # Check if a directory was clicked and navigate into it
                for button in directory_buttons:
                    if button[0] <= mouse_pos[1] <= button[0] + 30 and mouse_pos[1] <= SCREEN_HEIGHT/2 and mouse_pos[0] <= song_select_window:
                        folder_path = os.path.join(folder_path, button[1])
        
                # Check if a music file was clicked to play it
                for button in file_buttons:
                    if button[0] <= mouse_pos[1] <= button[0] + 30 and mouse_pos[0] <= song_select_window:
                        # refresh variables for new song
                        queue_raw = generated_unshuffled_queue(button[1], FILES_ONLY.copy())

                        if shuffle:
                            queue = shuffler(queue_raw, button[1], True)
                        else:
                            queue = queue_raw.copy()
                        
                        play_pause = "play"  # Reset play/pause state to "play" when a new song is selected
                        played_songs = {}  # Clear the list of played songs when a new song is selected
                        
                        # Load and play the selected file
                        file_path = os.path.join(folder_path, button[1])
                        currently_playing_folder_path = folder_path  # Update the currently playing folder path
                        STARTED = True
                        # queue_raw.remove(button[1])
                        # queue.remove(button[1])
                        PLAYING_SONG = button[1]

                        # Load the sound file as a Sound object to get its length
                        temp_sound_object = pygame.mixer.Sound(file_path)
                        total_length = temp_sound_object.get_length() # Length in seconds

                        # Get metadata for the selected track
                        render_size, cover_art_path = get_cover_art(file_path, SIZE)
                        album_cover_cache = pygame.image.load(cover_art_path)  # Update album cover cache with the new cover art when a song is selected

                        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Change play/pause button to hover state when a new song is selected

                        # CREATE AND START WAVE VISUALIZER
                        visualizer = WaveVisualizer(file_path, 
                                                   render_size[0], 
                                                   render_size[1])
                        # Set wave color to contrast with album cover
                        visualizer.set_color_from_image(cover_art_path)
                        visualizer.load_audio()
                        visualizer.play()
                        visualizer_running = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging = False  # Stop dragging when mouse button is released

        if event.type == pygame.MOUSEWHEEL:
            if mouse_pos[0] <= song_select_window:
                if mouse_pos[1] < SCREEN_HEIGHT/2:  # Directory section
                    dir_scroll_offset -= event.y * 40  # Scroll by item height
                    dir_scroll_offset = max(0, min(dir_scroll_offset, 
                                                   max(0, len(DIRECTORY_ONLY) * 40 - (SCREEN_HEIGHT/2 - 60))))
                else:  # File section
                    file_scroll_offset -= event.y * 40
                    file_scroll_offset = max(0, min(file_scroll_offset,
                                                    max(0, len(FILES_ONLY) * 40 - (SCREEN_HEIGHT/2 - 60))))

        
        # Handle spacebar for pause/play
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and visualizer:
                if play_pause == "play" and STARTED:
                    pygame.mixer.music.pause()
                    STARTED = False
                    play_pause = "pause"
                    try:
                        WaveVisualizer.set_pause_state(visualizer, True)  # Pause the visualizer
                    except:
                        pass  # Visualizer may not be initialized yet, ignore if error occurs
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")  # Default image for play button
                else:
                    pygame.mixer.music.unpause()
                    STARTED = True
                    play_pause = "play"
                    try:
                        WaveVisualizer.set_pause_state(visualizer, False)  # Unpause the visualizer
                    except:
                        pass  # Visualizer may not be initialized yet, ignore if error occurs
                        STARTED = False
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Default image for pause button

    with data_lock:
        input_key = media_input[0] if media_input else None
        media_input = media_input[1:]

    if input_key:
        if input_key == Key.media_play_pause and visualizer:
                if play_pause == "play" and STARTED:
                    pygame.mixer.music.pause()
                    STARTED = False
                    play_pause = "pause"
                    try:
                        WaveVisualizer.set_pause_state(visualizer, True)  # Pause the visualizer
                    except:
                        pass  # Visualizer may not be initialized yet, ignore if error occurs
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_play.jpg")  # Default image for play button
                else:
                    pygame.mixer.music.unpause()
                    STARTED = True
                    play_pause = "play"
                    try:
                        WaveVisualizer.set_pause_state(visualizer, False)  # Unpause the visualizer
                    except:
                        pass  # Visualizer may not be initialized yet, ignore if error occurs
                        STARTED = False
                    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Default image for pause button

        if input_key == Key.media_next and visualizer_running:
            STARTED, play_pause, play_pause_button_path = skip()

        if input_key == Key.media_previous and STARTED:
            play_pause, played_songs, queue_raw, queue, play_pause_button_path, visualizer, STARTED, PLAYING_SONG, render_size, cover_art_path = previous(current_time_sec, currently_playing_folder_path, played_songs, queue_raw, queue, SIZE, visualizer, screen, total_length, play_pause, play_pause_button_path, visualizer_running, STARTED, PLAYING_SONG, render_size, cover_art_path, file_path) 
            album_cover_cache = pygame.image.load(cover_art_path)  # Update album cover cache with the new cover art when going to the previous song

    # ========================================================================
    # AUTO-PLAY & QUEUE MANAGEMENT
    # ========================================================================
    
    # Auto-play next song when current song finishes
    if STARTED and not len(queue_raw) <= 0:
        if not pygame.mixer.music.get_busy():

            try:
                played_songs[PLAYING_SONG] = queue_raw.index(PLAYING_SONG)  # Add the previous song to the played_songs dictionary with its index
                queue_raw.remove(PLAYING_SONG)
                queue.remove(PLAYING_SONG)
            except:
                retry = True

            newsong = queue[0] if queue else ""

            file_path = os.path.join(currently_playing_folder_path, newsong)
            if os.path.isfile(file_path):

                PLAYING_SONG = newsong

                # Get cover art and update visualizer for the new song
                render_size, cover_art_path = get_cover_art(file_path, SIZE)
                album_cover_cache = pygame.image.load(cover_art_path)  # Update album cover cache with the new cover art when a song is selected

                # Load the sound file as a Sound object to get its length
                temp_sound_object = pygame.mixer.Sound(file_path)
                total_length = temp_sound_object.get_length() # Length in seconds

                
                # UPDATE VISUALIZER FOR NEW SONG
                visualizer = WaveVisualizer(file_path, 
                                        render_size[0], 
                                        render_size[1])
                # Set wave color to contrast with album cover
                visualizer.set_color_from_image(cover_art_path)
                visualizer.load_audio()
                visualizer.play()
                visualizer_running = True
            else:
                print("No more songs in the queue to play.")
                STARTED = False  # Stop playback if there are no more songs to play
                visualizer_running = False  # Stop the visualizer as well
                cover_art_path = os.path.join(os.path.dirname(__file__), "assets/default_cover.jpg")  # Reset to default cover art path
                album_cover_cache = pygame.image.load(cover_art_path)  # Reset album cover cache to default when no more songs are available
            
            if retry:
                pygame.mixer.music.stop()
                retry = False

    # ========================================================================
    # RENDERING & DISPLAY
    # ========================================================================
    if visualizer_running and visualizer:
        current_time_sec = visualizer.get_position()  # Get current time from visualizer for more accurate tracking during seeking
    
    # Update screen dimensions in case window was resized
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    song_select_window = SCREEN_WIDTH / 5
    
    # ---- LEFT SIDEBAR: Directory and File Selection ----
    
    # Draw left sidebar background (light gray for directory/file selection area)
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, song_select_window, SCREEN_HEIGHT))

    try:
        # Get directories and files in current folder
        DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, folder_path = get_music_files_and_directories(folder_path, SCREEN_HEIGHT, og_folder, dir_scroll_offset, file_scroll_offset)
    except Exception as e:
        DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons, folder_path = get_music_files_and_directories(og_folder, SCREEN_HEIGHT, og_folder, dir_scroll_offset, file_scroll_offset)

    # Create subsurface for folder section (top half of sidebar)
    folder_surf = screen.subsurface(0, 0, song_select_window, SCREEN_HEIGHT)
    
    # Create subsurface for file list section (bottom half of sidebar)
    file_surf = screen.subsurface(0, SCREEN_HEIGHT/2, song_select_window, SCREEN_HEIGHT/2)

    # Draw folder list with header (optimized with enumeration and caching)
    for idx, directory in enumerate(DIRECTORY_ONLY):
        cache_key = f"folder_{directory}_{id(font)}"
        if cache_key not in text_cache:
            text_cache[cache_key] = font.render(directory, True, (255, 255, 255))
        folder_surf.blit(text_cache[cache_key], (10, (idx+1)*40 + 10 - dir_scroll_offset))

    pygame.draw.rect(screen, (40, 40, 40), (0, 0, song_select_window, 40))
    cache_key = "header_folders"
    if cache_key not in text_cache:
        text_cache[cache_key] = font.render("Folders:", True, (255, 255, 255))
    folder_surf.blit(text_cache[cache_key], (10, 10))

    # Draw file list background
    pygame.draw.rect(screen, (40, 40, 40), (0, SCREEN_HEIGHT/2, song_select_window, SCREEN_HEIGHT/2))

    # Draw file list with header (optimized with enumeration and caching)
    for idx, file in enumerate(FILES_ONLY):
        cache_key = f"file_{file}_{id(font)}"
        if cache_key not in text_cache:
            text_cache[cache_key] = font.render(file, True, (255, 255, 255))
        file_surf.blit(text_cache[cache_key], (10, (idx+1)*40 + 10 - file_scroll_offset))

    pygame.draw.rect(screen, (40, 40, 40), (0, SCREEN_HEIGHT/2, song_select_window, 40))   
    cache_key = "header_files"
    if cache_key not in text_cache:
        text_cache[cache_key] = font.render("Files:", True, (255, 255, 255))
    file_surf.blit(text_cache[cache_key], (10, 10))

    try:
        # Draw scrollbars
        dir_max_scroll = max(0, len(DIRECTORY_ONLY) * 40 - (SCREEN_HEIGHT/2 - 60))
        if dir_max_scroll > 0:
            scrollbar_h = (SCREEN_HEIGHT/2 - 60) * (SCREEN_HEIGHT/2 - 60) / (len(DIRECTORY_ONLY) * 40)
            scrollbar_y = dir_scroll_offset * (SCREEN_HEIGHT/2 - 60) / (len(DIRECTORY_ONLY) * 40)
            pygame.draw.rect(screen, (100, 100, 100), 
                            (song_select_window - 10, scrollbar_y, 8, scrollbar_h))

        file_max_scroll = max(0, len(FILES_ONLY) * 40 - (SCREEN_HEIGHT/2 - 60))
        if file_max_scroll > 0:
            scrollbar_h = (SCREEN_HEIGHT/2 - 60) * (SCREEN_HEIGHT/2 - 60) / (len(FILES_ONLY) * 40)
            scrollbar_y = file_scroll_offset * (SCREEN_HEIGHT/2 - 60) / (len(FILES_ONLY) * 40)
            pygame.draw.rect(screen, (100, 100, 100), 
                            (song_select_window - 10, SCREEN_HEIGHT/2 + scrollbar_y, 8, scrollbar_h))
    except:
        print("Not enough space to draw scrollbars")

    # ---- RIGHT SIDE: Album Cover and Visualizer ----
    
    # Draw right side background (dark gray for album cover area)
    pygame.draw.rect(screen, (20, 20, 20), (song_select_window, 0, SCREEN_WIDTH - song_select_window, SCREEN_HEIGHT))
    
    # Draw back button (small gray square)
    pygame.draw.rect(screen, back_button_color, (SCREEN_WIDTH/5-40, 5, 20, 20))

    # Load and cache button images
    button_path = os.path.join(os.path.dirname(__file__), play_pause_button_path)
    if button_path not in button_images_cache:
        button_images_cache[button_path] = pygame.image.load(button_path)
    play_button = button_images_cache[button_path]

    play_button_rect = play_button.get_rect()
    play_button_rect.center = ((SCREEN_WIDTH-SCREEN_WIDTH/5)/2+SCREEN_WIDTH/5, SCREEN_HEIGHT-50)
    screen.blit(play_button, play_button_rect)
        
    pygame.draw.rect(screen, skip_button_color, ((SCREEN_WIDTH-SCREEN_WIDTH/5)/2+30+SCREEN_WIDTH/5, SCREEN_HEIGHT-50, 50, 20))
    pygame.draw.rect(screen, previous_button_color, ((SCREEN_WIDTH-SCREEN_WIDTH/5)/2-80+SCREEN_WIDTH/5, SCREEN_HEIGHT-50, 50, 20))
    pygame.draw.rect(screen, shuffle_button_color, ((SCREEN_WIDTH-SCREEN_WIDTH/5)/2-135+SCREEN_WIDTH/5, SCREEN_HEIGHT-50, 50, 20))

    # Load and cache album cover art
    album_cover_cache = pygame.image.load(cover_art_path)

    image_rect = album_cover_cache.get_rect()
    # Center the cover image on the right side of the screen
    image_rect.center = ((SCREEN_WIDTH-(SCREEN_WIDTH/5))/2+SCREEN_WIDTH/5, SCREEN_HEIGHT/2)
    screen.blit(album_cover_cache, image_rect)

    # ---- NOW PLAYING INFO ----
    
    # Display currently playing song name (optimized with caching)
    try:
        # Cache metadata lookups (expensive operation)
        song_file_path = os.path.join(currently_playing_folder_path, PLAYING_SONG)
        if song_file_path not in metadata_cache:
            metadata_cache[song_file_path] = get_artist(song_file_path)
        artist = metadata_cache[song_file_path]
        
        song_title = "Now Playing: " + PLAYING_SONG[:-4]
        cache_key = f"now_playing_{song_title}_{id(font)}"
        if cache_key not in text_cache:
            text_cache[cache_key] = font.render(song_title, True, (255, 255, 255))
        screen.blit(text_cache[cache_key], ((SCREEN_WIDTH-song_select_window)/2+SCREEN_WIDTH/5-(13+len(PLAYING_SONG)*6), SCREEN_HEIGHT/2 + render_size[1]/2 + 10))
        
        artist_text = "Artist: " + artist
        cache_key = f"artist_{artist}_{id(font)}"
        if cache_key not in text_cache:
            text_cache[cache_key] = font.render(artist_text, True, (255, 255, 255))
        screen.blit(text_cache[cache_key], ((SCREEN_WIDTH-song_select_window)/2+SCREEN_WIDTH/5-(13+len(artist)*6), SCREEN_HEIGHT/2 + render_size[1]/2 + 50))
    except:
        pass  # Silently fail if metadata unavailable

    # Draw/update the song length bar
    try:
        song_length_bar = SongBar(total_length, current_time_sec, SCREEN_WIDTH, SCREEN_HEIGHT, screen)
        song_length_bar.update(current_time_sec, total_length, SCREEN_WIDTH, SCREEN_HEIGHT, screen)
    except:
        pass

    # Update album cover if screen size changed
    if SIZE != OLD_SIZE:
        render_size, cover_art_path = get_cover_art(os.path.join(currently_playing_folder_path, PLAYING_SONG), SIZE)
        album_cover_cache = pygame.image.load(cover_art_path)  # Update album cover cache with the new cover art when a song is selected

    OLD_SIZE = SIZE
    
    # ---- WAVE VISUALIZATION RENDERING ----
    
    try:
        # Render wave visualization on the right side
        if visualizer and visualizer_running:
            # Create a subsurface for the visualizer (right side of screen)
            vis_surface = screen.subsurface(song_select_window+(((SCREEN_WIDTH-song_select_window)/2-render_size[0]/2)), 0,
                                        render_size[0], SCREEN_HEIGHT/2+render_size[1]/2)
            
            # Render one frame of the wave visualization
            if not visualizer.render_frame(vis_surface, mouse_pos):
                visualizer_running = False  # Song finished, stop rendering
            
            # Update visualizer render position if window was resized
            if visualizer:
                visualizer.update_render_size(int(render_size[0]), 
                                            int((SCREEN_HEIGHT/2)+(render_size[1]/2)))
    except:
        pass # give the visualizer some time to initialize before trying to create the subsurface for it, ignore errors if it fails at first

    # ---- UPDATE DISPLAY ----
    
    # Refresh the display with all rendered elements
    pygame.display.flip()

pygame.quit()
sys.exit()