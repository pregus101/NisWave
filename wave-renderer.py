import librosa
import numpy as np
from scipy.fft import fft
import pygame
import subprocess
import urllib.request
from urllib.parse import urlparse, parse_qs
from youtubesearchpython import VideosSearch
import os
from PIL import Image
import threading
import platform
import sys
from screeninfo import get_monitors

# Initialize a lock for Thread-safe data access
data_lock = threading.Lock()

# Gets the initial screen height and info
monitors = str(get_monitors())

default_screen_size = []

temp = monitors.split("[Monitor(x=0, y=0, width=")
temp = temp[1].split("height=")
temp = temp[0] + temp[1]
temp = temp.split(", width_mm=")
temp = temp[0]
temp = temp.split(", ")

for i in range(0, len(temp)):
    default_screen_size.append(int(temp[i]))

default_width, default_height = default_screen_size

# Defines global/default variables
global BarHeight
global color

color = (100, 100, 100)

oldSize = default_screen_size

#initializes the global variables
BarHeight = []
BarHeightTarget = []  # Target heights for smooth interpolation

for i in range(1, 358):
            for j in range(20 * i, 20 * i + 20 + 1):
                BarHeight.append(default_height)
                BarHeightTarget.append(default_height)


# Gets the OS of the device
device_OS = platform.system()

# --- CONFIGURATION ---
CHANNELS = 2
RATE = 96000
BLOCKSIZE = 4096  # Larger window for smoother FFT
DURATION = 0.04
SMOOTHING_FACTOR = 0.7  # Higher = smoother, closer to 1 means slower response
DECAY_RATE = 0.95  # How quickly bars fall (closer to 1 = slower fall)
# ----------------------

# Set the MP3 file path here
MP3_FILE = "/Users/presian/Music/Mariah Carey - All I Want for Christmas Is You (Make My Wish Come True Edition).wav"


# Initialize Pygame
pygame.init()
pygame.font.init() # Initialize the font module
pygame.mixer.init()  # Initialize mixer for audio playback

font = pygame.font.SysFont('Arial', 30)

clock = pygame.time.Clock()

# Set up the display
screen_width = default_width
screen_height = default_height
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("pregus101's WaveBar app")
        

# Audio Processor - Process chunks from file with smoothing
def process_audio_chunk(indata):
    global BarHeight, BarHeightTarget
    
    window_size = screen.get_size()
    width = window_size[0]
    height = window_size[1]

    # Handle both mono and stereo
    if len(indata.shape) == 1 or indata.shape[1] == 1:
        audio_channel = indata.flatten()
    else:
        audio_channel = indata[:, 0]
    
    # Pad to BLOCKSIZE if smaller
    if len(audio_channel) < BLOCKSIZE:
        audio_channel = np.pad(audio_channel, (0, BLOCKSIZE - len(audio_channel)))
    
    yf = fft(audio_channel)
    size = (width/1470)*10

    with data_lock:
        bar_index = 0
        for i in range(1, int(size) + 1):
            for j in range(20 * i, 20 * i + 20 + 1):
                if bar_index < len(BarHeightTarget):
                    # Calculate new target height
                    new_height = height - int(np.abs(yf[j]) * 2)  # Scale up for visibility
                    new_height = max(0, min(height, new_height))  # Clamp between 0 and height
                    
                    # Exponential smoothing
                    BarHeightTarget[bar_index] = new_height
                    BarHeight[bar_index] = SMOOTHING_FACTOR * BarHeight[bar_index] + (1 - SMOOTHING_FACTOR) * BarHeightTarget[bar_index]
                bar_index += 1


global paused
paused = False
pause_time = 0  # Time at which pause occurred
paused_elapsed_seconds = 0  # Freeze elapsed time when paused

# Define pause button
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 50
BUTTON_X = 20
BUTTON_Y = 20
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_ACTIVE_COLOR = (200, 50, 50)

def main_loop(audio_data, audio_duration):
    global BarHeight, BarHeightTarget
    global color, paused, pause_time, paused_elapsed_seconds

    running = True
    start_time = pygame.time.get_ticks()  # Get the start time in milliseconds
    last_chunk_index = -1
    
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        button_hovered = (BUTTON_X <= mouse_x <= BUTTON_X + BUTTON_WIDTH and 
                         BUTTON_Y <= mouse_y <= BUTTON_Y + BUTTON_HEIGHT)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if pause button was clicked
                if button_hovered:
                    paused = not paused
                    if paused:
                        # Store the current elapsed time
                        paused_elapsed_seconds = (pygame.time.get_ticks() - start_time) / 1000.0
                        pygame.mixer.music.pause()
                    else:
                        # Resume from paused state
                        pygame.mixer.music.unpause()
                        start_time = pygame.time.get_ticks() - (paused_elapsed_seconds * 1000)
            elif event.type == pygame.KEYDOWN:
                # Spacebar to toggle pause
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        # Store the current elapsed time
                        paused_elapsed_seconds = (pygame.time.get_ticks() - start_time) / 1000.0
                        pygame.mixer.music.pause()
                    else:
                        # Resume from paused state
                        pygame.mixer.music.unpause()
                        start_time = pygame.time.get_ticks() - (paused_elapsed_seconds * 1000)

        # Calculate elapsed time in seconds
        if paused:
            elapsed_seconds = paused_elapsed_seconds
        else:
            elapsed_ms = pygame.time.get_ticks() - start_time
            elapsed_seconds = elapsed_ms / 1000.0
        
        # Stop if audio has finished
        if elapsed_seconds > audio_duration:
            break
        
        # Calculate which chunk we should be visualizing based on elapsed time
        chunk_index = int(elapsed_seconds * RATE)
        
        # Only process new audio when the chunk changes
        if chunk_index != last_chunk_index:
            # Get the next audio chunk
            if chunk_index + BLOCKSIZE <= len(audio_data):
                audio_chunk = audio_data[chunk_index:chunk_index + BLOCKSIZE]
            else:
                if chunk_index < len(audio_data):
                    audio_chunk = audio_data[chunk_index:]
                else:
                    audio_chunk = np.zeros(BLOCKSIZE)
            
            # Process the audio chunk
            if len(audio_chunk) > 0:
                process_audio_chunk(audio_chunk)
            
            last_chunk_index = chunk_index
        
        # Apply decay to bars every frame (makes them fall smoothly)
        with data_lock:
            for i in range(len(BarHeight)):
                # Bars slowly decay toward their target
                BarHeight[i] = BarHeight[i] * DECAY_RATE + BarHeightTarget[i] * (1 - DECAY_RATE)
        
        window_size = screen.get_size()
        width = window_size[0]
        height = window_size[1]

        size = int((width/1470)*10)
        
        screen.fill((0, 0, 0))  # Black background
        
        with data_lock:
            bar_index = 0
            for i in range(1, size + 1):
                for j in range(20 * i, 20 * i + 20 + 1):
                    if bar_index >= len(BarHeight):
                        break

                    bar_height_y = int(BarHeight[bar_index])

                    bar_x = int((j-20)*((width/size)/20))+2
                    bar_w = 2 
                    bar_h = (height) - bar_height_y/50

                    # Draw the main bar
                    pygame.draw.rect(screen, (color), (bar_x, bar_height_y, bar_w, bar_h))
                    bar_index += 1
        
        # Draw pause button
        button_color = BUTTON_ACTIVE_COLOR if paused else (BUTTON_HOVER_COLOR if button_hovered else BUTTON_COLOR)
        pygame.draw.rect(screen, button_color, (BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT))
        pygame.draw.rect(screen, (255, 255, 255), (BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT), 2)  # Border
        
        # Draw button text
        button_text = "RESUME" if paused else "PAUSE"
        text_surface = font.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(BUTTON_X + BUTTON_WIDTH // 2, BUTTON_Y + BUTTON_HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Exiting application.")
    os._exit(0) 

if __name__ == "__main__":
    
    try:
        # Check if MP3 file exists
        if not os.path.exists(MP3_FILE):
            print(f"Error: MP3 file '{MP3_FILE}' not found.")
            print("Please set the MP3_FILE variable to a valid file path.")
            os._exit(1)
        
        # Load the audio file using librosa for visualization
        print(f"Loading audio from {MP3_FILE}...")
        audio_data, sr = librosa.load(MP3_FILE, sr=RATE, mono=True)
        
        audio_duration = len(audio_data) / sr
        print(f"Audio loaded. Sample rate: {sr}, Duration: {audio_duration:.2f} seconds")
        
        # Convert to the correct shape for processing
        audio_data = audio_data.reshape(-1, 1) if len(audio_data.shape) == 1 else audio_data
        
        # Load and play the MP3 file using pygame mixer
        print("Starting playback...")
        pygame.mixer.music.load(MP3_FILE)
        pygame.mixer.music.play()
        
        # Run the Pygame Loop in the Main Thread
        main_loop(audio_data, audio_duration)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        os._exit(1)