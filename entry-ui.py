# =============================================================================
# NisWave Music Player UI
# A music player interface built with Pygame featuring folder navigation,
# track selection, and album cover display
# =============================================================================

import pygame
import os
from screeninfo import get_monitors
import sys
from platformdirs import user_music_dir
from pathlib import Path
import random
from get_files import get_music_files_and_directories
from update_image import get_cover_art
from wave_renderer import WaveVisualizer 

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

# Initialize Pygame and font
pygame.init()
pygame.mixer.init()  # Initialize mixer for audio playback
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)

# Extract and store screen dimensions
default_screen_size = []
for i in range(0, len(temp)):
    default_screen_size.append(int(temp[i]))

default_width, default_height = default_screen_size

# Get initial music directory path
folder_path = Path(user_music_dir())

# Set up the display window
SCREEN_WIDTH = default_width
SCREEN_HEIGHT = default_height
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("pregus101's NisWave app")

# =============================================================================
# Application State Variables
# =============================================================================

OLD_SIZE = 640  # Previous album cover size (for resize detection)
STARTED = False  # Track whether playback has begun
PLAYING_SONG = ""  # Currently playing song filename

# Wave visualizer state
visualizer = None  # Will hold the WaveVisualizer instance
visualizer_running = False

# Create surface objects for directory and file windows
directory_buttons_window = pygame.Surface((SCREEN_WIDTH/5, SCREEN_HEIGHT/2))
file_buttons_window = pygame.Surface((SCREEN_WIDTH/5, SCREEN_HEIGHT/2))

# Set inital pause/play button state
play_pause = "play"  # Can be "play" or "pause"

# Initialize the played songs
played_songs = []

# # Create the queue for auto-playing songs (will be populated with files from the current directory)
# DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons = get_music_files_and_directories(folder_path, SCREEN_HEIGHT)
# queue = FILES_ONLY.copy()  # Initialize queue with available songs in the current directory

# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================
while True:
    # Calculate album cover size based on screen resolution for scaling
    SIZE = int(640 * ((SCREEN_WIDTH * SCREEN_HEIGHT) / (1920 * 1147)))
    mouse_pos = pygame.mouse.get_pos()
    
    # ========================================================================
    # EVENT HANDLING
    # ========================================================================
    for event in pygame.event.get():
        # Exit application when window is closed
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Handle mouse button clicks (folder/file selection and navigation)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button only
                # Get current directory contents for button interaction
                
                DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons = get_music_files_and_directories(folder_path, SCREEN_HEIGHT)

                # Debug output (can be removed later)
                print(SCREEN_WIDTH/5-25 <= mouse_pos[0] <= SCREEN_WIDTH/5-5 and 5 <= mouse_pos[1] <= 25)
                print(SCREEN_WIDTH/5-25, mouse_pos[0], SCREEN_WIDTH/5-5, mouse_pos[1])

                # Check if back button was clicked (navigate to parent directory)
                if SCREEN_WIDTH/5-25 <= mouse_pos[0] <= SCREEN_WIDTH/5-5 and 5 <= mouse_pos[1] <= 25:
                    folder_path = os.path.dirname(folder_path)
                    print("Back button clicked, new folder path:", folder_path)


                # Check if pause/play button was clicked
                if (SCREEN_WIDTH-SCREEN_WIDTH/5)/2-25+SCREEN_WIDTH/5 <= mouse_pos[0] <= (SCREEN_WIDTH-SCREEN_WIDTH/5)/2+25+SCREEN_WIDTH/5 and SCREEN_HEIGHT-30 <= mouse_pos[1] <= SCREEN_HEIGHT-10:
                    if play_pause == "play" and STARTED:
                        pygame.mixer.music.pause()
                        STARTED = False
                        play_pause = "pause"
                        WaveVisualizer.set_pause_state(visualizer, True)  # Pause the visualizer
                    else:
                        pygame.mixer.music.unpause()
                        STARTED = True
                        play_pause = "play"
                        WaveVisualizer.set_pause_state(visualizer, False)  # Unpause the visualizer

                # Check if a directory was clicked and navigate into it
                for button in directory_buttons:
                    if button[0] <= mouse_pos[1] <= button[0] + 30 and mouse_pos[1] <= SCREEN_HEIGHT/2 and mouse_pos[0] <= song_select_window:
                        folder_path = os.path.join(folder_path, button[1])
        
                # Check if a music file was clicked to play it
                for button in file_buttons:
                    if button[0] <= mouse_pos[1] <= button[0] + 30 and mouse_pos[0] <= song_select_window:
                        # refresh variables for new song
                        queue = FILES_ONLY.copy()
                        play_pause = "play"  # Reset play/pause state to "play" when a new song is selected
                        played_songs = []  # Clear the list of played songs when a new song is selected
                        played_songs.append(button[1])  # Add the selected song to the list of played songs
                        
                        # Load and play the selected file
                        file_path = os.path.join(folder_path, button[1])
                        # pygame.mixer.music.load(file_path)
                        # pygame.mixer.music.play()
                        STARTED = True
                        queue.remove(button[1])
                        PLAYING_SONG = button[1]
                        
                        # Get album cover art for the selected track
                        render_size = get_cover_art(file_path, SIZE)

                        # CREATE AND START WAVE VISUALIZER
                        visualizer = WaveVisualizer(file_path, 
                                                   render_size[0], 
                                                   render_size[1])
                        # Set wave color to contrast with album cover
                        cover_art_path = os.path.join(os.path.dirname(__file__), "temp_cover_art/temp_cover.png")
                        visualizer.set_color_from_image(cover_art_path)
                        visualizer.load_audio()
                        visualizer.play()
                        visualizer_running = True
        
        # Handle spacebar for pause/play (currently disabled)
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE and visualizer:
        #         visualizer.toggle_pause()

    # ========================================================================
    # AUTO-PLAY & QUEUE MANAGEMENT
    # ========================================================================
    
    # Auto-play next song when current song finishes
    if STARTED:
        if not pygame.mixer.music.get_busy():
            # Pick a random song from the queue and play it
            newsong = queue[random.randint(0, len(queue)-1)]
            file_path = os.path.join(folder_path, newsong)
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            PLAYING_SONG = newsong

            played_songs.append(newsong)  # Add the new song to the list of played songs

            queue.remove(newsong)

            # Get cover art and update visualizer for the new song
            render_size = get_cover_art(file_path, SIZE)
            
            # UPDATE VISUALIZER FOR NEW SONG
            visualizer = WaveVisualizer(file_path, 
                                    render_size[0], 
                                    render_size[1])
            # Set wave color to contrast with album cover
            cover_art_path = os.path.join(os.path.dirname(__file__), "temp_cover_art/temp_cover.png")
            visualizer.set_color_from_image(cover_art_path)
            visualizer.load_audio()
            visualizer.play()
            visualizer_running = True

    # ========================================================================
    # RENDERING & DISPLAY
    # ========================================================================
    # ========================================================================
    # RENDERING & DISPLAY
    # ========================================================================
    
    # Update screen dimensions in case window was resized
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    song_select_window = SCREEN_WIDTH / 5
    
    # ---- LEFT SIDEBAR: Directory and File Selection ----
    
    # Draw left sidebar background (dark blue)
    pygame.draw.rect(screen, (0, 0, 20), (0, 0, song_select_window, SCREEN_HEIGHT))

    # Get directories and files in current folder
    DIRECTORY_ONLY, FILES_ONLY, directory_buttons, file_buttons = get_music_files_and_directories(folder_path, SCREEN_HEIGHT)

    # Create subsurface for folder section (top half of sidebar)
    folder_surf = screen.subsurface(0, 0, song_select_window, SCREEN_HEIGHT)
    
    # Create subsurface for file list section (bottom half of sidebar)
    file_surf = screen.subsurface(0, SCREEN_HEIGHT/2, song_select_window, SCREEN_HEIGHT/2)

    # Draw folder list with header
    text_surface = font.render("Folders:", True, (255, 255, 255))
    folder_surf.blit(text_surface, (10, 10))
    for directory in DIRECTORY_ONLY:
        text_surface = font.render(directory, True, (255, 255, 255))
        folder_surf.blit(text_surface, (10, (DIRECTORY_ONLY.index(directory)+1)*40 + 10))

    # Draw file list background
    pygame.draw.rect(screen, (0, 0, 20), (0, SCREEN_HEIGHT/2, song_select_window, SCREEN_HEIGHT/2))

    # Draw file list with header
    text_surface = font.render("Files:", True, (255, 255, 255))
    file_surf.blit(text_surface, (10, 10))
    for file in FILES_ONLY:
        text_surface = font.render(file, True, (255, 255, 255))
        file_surf.blit(text_surface, (10, (FILES_ONLY.index(file)+1)*40 + 10))

    # ---- RIGHT SIDE: Album Cover and Visualizer ----
    
    # Draw right side background (dark red for album cover area)
    pygame.draw.rect(screen, (20, 0, 0), (song_select_window, 0, SCREEN_WIDTH - song_select_window, SCREEN_HEIGHT))
    
    # Draw back button (small gray square)
    pygame.draw.rect(screen, (64, 64, 64), (SCREEN_WIDTH/5-25, 5, 20, 20))

    #draw play/pause button (small gray square)
    pygame.draw.rect(screen, (64, 64, 64), ((SCREEN_WIDTH-SCREEN_WIDTH/5)/2-25+SCREEN_WIDTH/5, SCREEN_HEIGHT-30, 50, 20))

    # Load and display album cover art, centered on right side
    album_cover = pygame.image.load(os.path.join(os.path.dirname(__file__), "temp_cover_art/temp_cover.png"))
    image_rect = album_cover.get_rect()
    # Center the cover image on the right side of the screen
    image_rect.center = ((SCREEN_WIDTH-(SCREEN_WIDTH/5))/2+SCREEN_WIDTH/5, SCREEN_HEIGHT/2)
    screen.blit(album_cover, image_rect)

    # ---- NOW PLAYING INFO ----
    
    # Display currently playing song name
    if STARTED:
        text_surface = font.render("Now Playing: " + PLAYING_SONG, True, (255, 255, 255))
        screen.blit(text_surface, ((SCREEN_WIDTH-song_select_window)/2+song_select_window-(13+len(PLAYING_SONG))*7, 10))

    # Update album cover if screen size changed
    if SIZE != OLD_SIZE:
        render_size = get_cover_art(os.path.join(folder_path, PLAYING_SONG), SIZE)

    OLD_SIZE = SIZE
    
    # ---- WAVE VISUALIZATION RENDERING ----
    
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

    # ---- UPDATE DISPLAY ----
    
    # Refresh the display with all rendered elements
    pygame.display.flip()


