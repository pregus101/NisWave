import sounddevice as sd
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

for i in range(1, 358):
            for j in range(20 * i, 20 * i + 20 + 1):
                BarHeight.append(default_height)


# Gets the OS of the device
device_OS = platform.system()

# Gets the loopback/input
def get_loopback_device_id():
    # Finds the device ID for a loopback device based on the operating system.
    system = platform.system()
    devices = sd.query_devices()
    
    if system == "Darwin": # macOS
        search_terms = ["BlackHole"]
        
    elif system == "Windows":
        # Common loopback device names on Windows
        search_terms = ["Stereo Mix", "What U Hear", "Loopback"]
        
    else: # Linux/Other
        # Common Linux/PulseAudio names for loopback/monitor
        search_terms = ["Monitor", "Loopback"]

    for i, device in enumerate(devices):
        for term in search_terms:
            if term in device['name']:
                print(f"Found loopback device: {device['name']}")
                return i
                
    # Fallback: Try finding the default input device
    try:
        default_device_name = sd.query_devices(sd.default.device[0])['name']
        print(f"Warning: Loopback device not found. Using default input device: {default_device_name}")
        return sd.default.device[0]
    except Exception:
        raise ValueError(f"Loopback audio device not found for {system}. Please ensure a loopback device (like Stereo Mix/BlackHole) is installed and enabled.")

# --- CONFIGURATION ---
try:
    LOOPBACK_DEVICE_ID = get_loopback_device_id()
except ValueError as e:
    print(e)
    LOOPBACK_DEVICE_ID = None 
    if platform.system() == "Windows":
        print("\n**Action Required on Windows:** You likely need to enable 'Stereo Mix' or install a virtual cable.")
        
CHANNELS = 2
RATE = 96000
BLOCKSIZE = 1024
DURATION = 0.04
# ----------------------

def get_song_name():
    if device_OS == "Darwin":
        # Defines the script to get the currently playing spotify song
        script = """
        tell application "Spotify"
            if it is running then
                if player state is playing then
                    set trackName to name of current track
                    set artistName to artist of current track
                    return trackName & " by " & artistName
                else
                    return "Spotify is paused or stopped."
                end if
            else
                return "Spotify is not running."
            end if
        end tell
        """
        return subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True).stdout.strip()

# Set the initial song
global song_name
song_name = get_song_name()

# Gets the song image
def get_song_image(width=default_width, height=default_height):
    # Checks if the os if MAC
    if device_OS == "Darwin":

        # Sets path to image
        image_path = os.getcwd()+"/temp.jpg"

        # Gets the image by first getting the link then parsing it
        searcher = VideosSearch(song_name, 1)
        result = searcher.result()
        song_link = []
        try:
            for video_data in result['result']:
                song_link.append(video_data['link'])
            song_link = song_link[0]
        except:
            print("Error finding image")

        if 'youtu.be' in song_link:
            path = urlparse(song_link).path
            path.lstrip('/')
        elif 'youtube.com' in song_link:
            query = urlparse(song_link).query
            if query:
                query_params = parse_qs(query)
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    if '&list=' in song_link:
                        video_id.split('&')[0]
        try:
            # Download the embed image
            if video_id:
                    try:
                        # Try high resolution first
                        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                        urllib.request.urlretrieve(thumbnail_url, image_path)
                    except:
                        # Fallback to default resolution
                        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/default.jpg'
                        urllib.request.urlretrieve(thumbnail_url, image_path)

            try:
                image = Image.open(image_path)
                new_size = (width, height)
                resized_image = image.resize(new_size)
                resized_image.save(image_path)
            except Exception as e:
                print(f"Error resizing image: {e}")

        except:
            print("Error downloading image")

# Gets the avarage color and then returns the inverted color
def get_avg_img_col():
    image = Image.open(str(os.getcwd()) + "/temp.jpg")
    image_array = np.array(image)

    average_color_per_channel = np.average(image_array, axis=(0, 1))
    
    # Convert to integer values
    average_color = tuple(map(int, average_color_per_channel))

    neg_average_color = (255-average_color[0], 255-average_color[1], 255-average_color[2])

    return(neg_average_color)


# Gets the initial image
get_song_image()

# Initialize Pygame
pygame.init()
pygame.font.init() # Initialize the font module

font = pygame.font.SysFont('Arial', 30)

clock = pygame.time.Clock()

# Set up the display
screen_width = default_width
screen_height = default_height
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("pregus101's WaveBar app")

# The song update task
def song_update_task():
    global color
    global song_name

    oldColor = color

    get_song_image()
    song_name = get_song_name()
    song_name_old = get_song_name()

    oldSize = default_screen_size

    while True:

        window_size = screen.get_size()
        width = window_size[0]
        height = window_size[1]

        song_name = get_song_name()

        if oldSize != window_size:
            print("switch", color)
            get_song_image(width, height)
            color = get_avg_img_col()
            oldSize = window_size

        if song_name_old != song_name:
            print("switch", color)
            get_song_image(width, height)
            color = get_avg_img_col()
            oldSize = window_size
            oldColor = color

        song_name_old = song_name
        

# Audio Proccessor
def callback(indata, frames, time, status):
    window_size = screen.get_size()
    width = window_size[0]
    height = window_size[1]

    yf = fft(indata[:, 0])

    size = (width/1470)*10

    with data_lock:
        bar_index = 0
        for i in range(1, int(size) + 1):
            for j in range(20 * i, 20 * i + 20 + 1):
                if bar_index < len(BarHeight):
                    BarHeight[bar_index] = (height - int(np.abs(yf[j])))
                bar_index += 1

def main_loop():
    global song_name
    global BarHeight
    global color

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window_size = screen.get_size()
        width = window_size[0]
        height = window_size[1]

        size = int((width/1470)*10)

        try:
            image = pygame.image.load(os.getcwd()+"/temp.jpg").convert_alpha()
            screen.blit(image, [(0,0),(width, height)])
        except pygame.error:
            screen.fill((0,0,0))
        
        with data_lock:
            bar_index = 0
            for i in range(1, size + 1):
                for j in range(20 * i, 20 * i + 20 + 1):
                    if bar_index >= len(BarHeight):
                        break

                    bar_height_y = BarHeight[bar_index] 
                    # trailer_height_y = trailer[bar_index]

                    bar_x = int((j-20)*((width/size)/20))+2
                    bar_w = 2 
                    bar_h = (height) - bar_height_y/50

                    # Draw the main bar
                    pygame.draw.rect(screen, (color), (bar_x, bar_height_y, bar_w, bar_h))
                    bar_index += 1

        # Draw text
        text = font.render(song_name, True, (color))
        screen.blit(text, (50, 50))

        # Update display and tick clock
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Exiting application.")
    os._exit(0) 

if __name__ == "__main__":

    song_thread = threading.Thread(target=song_update_task)
    song_thread.start()
    
    try:
        audio_stream = sd.InputStream(
                device=LOOPBACK_DEVICE_ID,
                samplerate=RATE,
                channels=CHANNELS,
                blocksize=int(RATE*DURATION),
                callback=callback
            )
        audio_stream.start()

        # 3. Run the Pygame Loop in the Main Thread
        main_loop()

    except:
        pass
    

