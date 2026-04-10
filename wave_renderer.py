import librosa
import numpy as np
from scipy.fft import fft # type: ignore
import pygame
import subprocess
import tempfile
import os
from PIL import Image
import threading
import platform

from typing import Any, NoReturn

# Initialize a lock for Thread-safe data access
data_lock: threading.Lock = threading.Lock()

# Gets the OS of the device
device_OS: str = platform.system()

# --- CONFIGURATION ---
CHANNELS = 2
RATE = 44100  # Reduced from 96000 for significant CPU savings (still high quality)
BLOCKSIZE = 2048  # Reduced from 4096 (less data to process per frame)
DURATION = 0.04
SMOOTHING_FACTOR = 0.85  # Higher = smoother, closer to 1 means slower response
DECAY_RATE = 0.95  # How quickly bars fall (closer to 1 = slower fall)
# ----------------------

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for audio playback

clock = pygame.time.Clock()


# =============================================================================
# WAVE VISUALIZER SYSTEM - Modular function-based renderer
# =============================================================================

class WaveVisualizer:
    """
    A modular wave visualizer that can be integrated with UI systems.
    Takes file input, render size, and pause/play control from external sources.
    
    Thread-safe: All public methods can safely be called from multiple threads.
    """
    
    def __init__(self, file_path: str, render_width: int, render_height: int, screen_surface: pygame.Surface | None = None) -> None:
        """
        Initialize the wave visualizer with custom render parameters.
        
        Args:
            file_path (str): Path to the audio file to visualize
            render_width (int): Width for the render area
            render_height (int): Height for the render area
            screen_surface (pygame.Surface, optional): External pygame surface to render to
        """
        self.file_path: str = file_path
        self.render_width: int = render_width
        self.render_height: int = render_height
        self.screen_surface: pygame.Surface | None = screen_surface
        
        # Thread safety lock for this visualizer instance
        self._instance_lock: threading.Lock = threading.Lock()
        
        # Visualizer state
        self.is_paused = False
        self.audio_data = None
        self.audio_duration = 0
        self.bar_height: list[int] = []
        self.bar_height_target: list[int] = []
        self.color: tuple[int, int, int] = (100, 100, 100)
        
        # Timing
        self.start_time: float = 0
        self.pause_time: float = 0
        self.paused_elapsed_seconds: float = 0

        # Temp file for m4a conversion
        self.temp_file = None
        
        self._initialize_bars()
    
    def set_color_from_image(self, image_path: str) -> None:
        """
        Extract dominant color from image and set a contrasting color for visualization.
        Thread-safe.
        
        Args:
            image_path (str): Path to the image file
        """
        try:
            img: Any = Image.open(image_path)
            # Resize for faster processing
            img = img.resize((100, 100))
            
            # Get image pixels
            pixels: list[Any] = list(img.getdata())
            
            # Calculate average color (dominant color)
            if len(pixels) > 0:
                r: int = sum(p[0] if len(p) > 0 else 0 for p in pixels) // len(pixels)
                g: int = sum(p[1] if len(p) > 1 else 0 for p in pixels) // len(pixels)
                b: int = sum(p[2] if len(p) > 2 else 0 for p in pixels) // len(pixels)
                
                # Calculate complementary color for contrast
                comp_r: int = 255 - r
                comp_g: int = 255 - g
                comp_b: int = 255 - b
                
                # Set the color (with lock for thread safety)
                with self._instance_lock:
                    self.color = (comp_r, comp_g, comp_b)
                print(f"Wave color set to RGB{self.color} for contrast")
        except Exception as e:
            print(f"Error setting color from image: {e}")
            # Default to bright cyan for good contrast
            with self._instance_lock:
                self.color = (0, 255, 255)
    
    def _initialize_bars(self) -> None:
        """Initialize bar heights based on render dimensions."""
        self.bar_height = []
        self.bar_height_target = []
        for i in range(1, 358):
            for j in range(20 * i, 20 * i + 20 + 1):  # type: ignore
                self.bar_height.append(self.render_height)
                self.bar_height_target.append(self.render_height)
    
    def load_audio(self) -> bool:
        """Load audio file for visualization."""
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"Audio file '{self.file_path}' not found.")
            
            print(f"Loading audio from {self.file_path}...")
            self.audio_data, sr = librosa.load(self.file_path, sr=RATE, mono=True)
            self.audio_duration: float = len(self.audio_data) / sr
            
            # Convert to correct shape
            self.audio_data = self.audio_data.reshape(-1, 1) if len(self.audio_data.shape) == 1 else self.audio_data
            
            print(f"Audio loaded. Duration: {self.audio_duration:.2f} seconds")
            return True
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False
    
    def set_pause_state(self, paused: bool) -> None:
        """
        Externally control pause/play state. Thread-safe.
        
        Args:
            paused (bool): True to pause, False to resume
        """
        with self._instance_lock:
            if paused != self.is_paused:
                self.is_paused: bool = paused
                if paused:
                    self.paused_elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000.0
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                    self.start_time = pygame.time.get_ticks() - (self.paused_elapsed_seconds * 1000)
    
    def get_pause_state(self) -> bool:
        """Get current pause state. Thread-safe."""
        with self._instance_lock:
            return self.is_paused
    
    def toggle_pause(self) -> None:
        """Toggle pause/play state. Thread-safe."""
        with self._instance_lock:
            paused = not self.is_paused
            self.is_paused = paused
            if paused:
                self.paused_elapsed_seconds = (pygame.time.get_ticks() - self.start_time) / 1000.0
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
                self.start_time = pygame.time.get_ticks() - (self.paused_elapsed_seconds * 1000)
    
    def update_render_size(self, new_width: int, new_height: int) -> None:
        """
        Update render dimensions dynamically. Thread-safe.
        
        Args:
            new_width (int): New render width
            new_height (int): New render height
        """
        with self._instance_lock:
            if new_width != self.render_width or new_height != self.render_height:
                self.render_width = new_width
                self.render_height = new_height
                self._initialize_bars()
    
    def process_audio_chunk(self, indata: Any) -> None:
        """Process audio chunk for visualization."""
        # Handle both mono and stereo
        if len(indata.shape) == 1 or indata.shape[1] == 1:
            audio_channel: int | Any = indata.flatten()
        else:
            audio_channel = indata[:, 0]
        
        # Pad to BLOCKSIZE if smaller
        if len(audio_channel) < BLOCKSIZE: # type: ignore
            audio_channel = np.pad(audio_channel, (0, BLOCKSIZE - len(audio_channel))) # type: ignore
        
        yf = fft(audio_channel)
        size = (self.render_width / 1470) * 10
        
        with data_lock:
            bar_index = 0
            for i in range(1, int(size) + 1):
                for j in range(20 * i, 20 * i + 20 + 1):
                    if bar_index < len(self.bar_height_target):
                        new_height: int = self.render_height - int(np.abs(yf[j]) * 2) # type: ignore
                        new_height = max(0, min(self.render_height, new_height))
                        
                        self.bar_height_target[bar_index] = new_height
                        self.bar_height[bar_index] = ( # type: ignore
                            SMOOTHING_FACTOR * self.bar_height[bar_index] + 
                            (1 - SMOOTHING_FACTOR) * self.bar_height_target[bar_index]
                        )
                    bar_index += 1
    
    def render_frame(self, screen: pygame.Surface, mouse_pos: None | list[int] = None) -> bool:
        """
        Render a single frame of visualization.
        
        Args:
            screen (pygame.Surface): Surface to render to
            mouse_pos (tuple, optional): Current mouse position for button hover detection
        """
        if self.audio_data is not None:
            elapsed_seconds: float = self._get_elapsed_time()
            
            if elapsed_seconds > self.audio_duration:
                return False
            
            # Process audio
            chunk_index = int(elapsed_seconds * RATE)
            if chunk_index + BLOCKSIZE <= len(self.audio_data):
                audio_chunk = self.audio_data[chunk_index:chunk_index + BLOCKSIZE]
            else:
                if chunk_index < len(self.audio_data):
                    audio_chunk = self.audio_data[chunk_index:]
                else:
                    audio_chunk = np.zeros(BLOCKSIZE)
            
            if len(audio_chunk) > 0:
                self.process_audio_chunk(audio_chunk)
        
        # Apply decay
        with data_lock:
            for i in range(len(self.bar_height)):
                self.bar_height[i] = ( # type: ignore
                    self.bar_height[i] * DECAY_RATE + 
                    self.bar_height_target[i] * (1 - DECAY_RATE)
                )
        
        # Draw background
        # screen.fill((0, 0, 0))
        
        # Draw bars
        size = int((self.render_width / 1470) * 10)
        with data_lock:
            bar_index = 0
            for i in range(1, size + 1):
                for j in range(20 * i, 20 * i + 20 + 1):
                    if bar_index >= len(self.bar_height):
                        break
                    
                    bar_height_y = int(self.bar_height[bar_index])
                    bar_x = int((j - 20) * ((self.render_width / size) / 20)) + 2
                    bar_w = 2
                    bar_h = self.render_height - bar_height_y / 50
                    
                    pygame.draw.rect(screen, self.color, (bar_x, bar_height_y, bar_w, bar_h))
                    bar_index += 1
        
        pygame.display.flip()
        clock.tick(60)
        return True
    
    def _get_elapsed_time(self):
        """Get current elapsed time, accounting for pause state. Thread-safe."""
        with self._instance_lock:
            if self.is_paused:
                return self.paused_elapsed_seconds
            else:
                elapsed_ms = pygame.time.get_ticks() - self.start_time
                return elapsed_ms / 1000.0
    
    def set_position(self, position_seconds: float) -> None:
        """
        Set the playback position to a specific time in seconds. Thread-safe.
        
        Args:
            position_seconds (float): Target position in seconds
        """
        with self._instance_lock:
            print(f"DEBUG: set_position called with {position_seconds:.2f}s, audio_duration={self.audio_duration:.2f}s")
            
            # Only clamp if audio is loaded
            if self.audio_duration > 0:
                clamped_position = max(0, min(position_seconds, self.audio_duration))
                print(f"DEBUG: Audio loaded, clamped position to {clamped_position:.2f}s")
            else:
                # If audio not loaded, just use the position as-is
                clamped_position = max(0, position_seconds)
                print(f"DEBUG: Audio not loaded yet, using position {clamped_position:.2f}s as-is")
            
            # Update internal timing
            if self.is_paused:
                self.paused_elapsed_seconds = clamped_position
                print(f"DEBUG: State=PAUSED, set paused_elapsed_seconds to {self.paused_elapsed_seconds:.2f}s")
            else:
                self.start_time = pygame.time.get_ticks() - (clamped_position * 1000)
                print(f"DEBUG: State=PLAYING, adjusted start_time, next elapsed should be {clamped_position:.2f}s")
            
            # Try to set mixer position
            try:
                pygame.mixer.music.set_pos(clamped_position)
                print(f"DEBUG: Mixer position set to {clamped_position:.2f}s")
            except Exception as e:
                print(f"DEBUG: Could not set mixer position: {type(e).__name__}: {e}")
            
            print(f"Set position to {clamped_position:.2f} seconds")
    
    def get_position(self):
        """Get current playback position in seconds. Thread-safe."""
        with self._instance_lock:
            if self.is_paused:
                return self.paused_elapsed_seconds
            else:
                elapsed_ms = pygame.time.get_ticks() - self.start_time
                return elapsed_ms / 1000.0
    
    def play(self):
        """Start playback. Thread-safe."""
        try:
            with self._instance_lock:
                if self.audio_data is not None:
                    play_path = self.file_path
                    if self.file_path.lower().endswith('.m4a'):
                        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                        tmp.close()
                        subprocess.run(
                            ['ffmpeg', '-y', '-i', self.file_path, tmp.name],
                            capture_output=True
                        )
                        if self.temp_file and os.path.exists(self.temp_file):
                            os.remove(self.temp_file)
                        self.temp_file = tmp.name
                        play_path = tmp.name
                    pygame.mixer.music.load(play_path)
                    pygame.mixer.music.play()
                    self.start_time = pygame.time.get_ticks()
                    self.is_paused = False
                    return True
        except Exception as e:
            print(f"Error playing audio: {e}")
        return False

    def cleanup(self):
        """Remove any temp files created for m4a conversion."""
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            self.temp_file = None


# =============================================================================
# LEGACY CODE (for backwards compatibility)
# =============================================================================

# Defines global/default variables
color = (100, 100, 100)

#initializes the global variables
BarHeight: list[int] = []
BarHeightTarget: list[int] = []  # Target heights for smooth interpolation

# Audio Processor - Process chunks from file with smoothing
def process_audio_chunk(indata: Any) -> None:
    global BarHeight, BarHeightTarget
    
    window_size: int = screen.get_size() # type: ignore
    width: int = window_size[0] # type: ignore
    height: int = window_size[1] # type: ignore

    # Handle both mono and stereo
    if len(indata.shape) == 1 or indata.shape[1] == 1:
        audio_channel: int = indata.flatten()
    else:
        audio_channel = indata[:, 0]
    
    # Pad to BLOCKSIZE if smaller
    if len(audio_channel) < BLOCKSIZE: # type: ignore
        audio_channel = np.pad(audio_channel, (0, BLOCKSIZE - len(audio_channel))) # type: ignore
    
    yf = fft(audio_channel)
    size: float = (width/1470)*10 # type: ignore

    with data_lock:
        bar_index = 0
        for i in range(1, int(size) + 1): # type: ignore
            for j in range(20 * i, 20 * i + 20 + 1):
                if bar_index < len(BarHeightTarget):
                    # Calculate new target height
                    new_height: Any | int = height - int(np.abs(yf[j]) * 2)  # Scale up for visibility # type: ignore
                    new_height: Any | int = max(0, min(height, new_height))  # Clamp between 0 and height # type: ignore
                    
                    # Exponential smoothing
                    BarHeightTarget[bar_index] = new_height
                    BarHeight[bar_index] = SMOOTHING_FACTOR * BarHeight[bar_index] + (1 - SMOOTHING_FACTOR) * BarHeightTarget[bar_index] # type: ignore
                bar_index += 1


global paused
paused = False
pause_time = 0  # Time at which pause occurred
paused_elapsed_seconds = 0  # Freeze elapsed time when paused


def main_loop(audio_data: Any, audio_duration: int) -> NoReturn:
    global BarHeight, BarHeightTarget
    global color, paused, pause_time, paused_elapsed_seconds

    running = True
    start_time: int = pygame.time.get_ticks()  # Get the start time in milliseconds
    last_chunk_index = -1
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
                BarHeight[i] = BarHeight[i] * DECAY_RATE + BarHeightTarget[i] * (1 - DECAY_RATE) # type: ignore
        
        window_size: Any | int = screen.get_size() # type: ignore
        width: Any | int = window_size[0] # type: ignore
        height: Any | int = window_size[1] # type: ignore

        size: int = int((width/1470)*10) # type: ignore
        
        # screen.fill((0, 0, 0))  # Black background
        
        with data_lock:
            bar_index = 0
            for i in range(1, size + 1):
                for j in range(20 * i, 20 * i + 20 + 1):
                    if bar_index >= len(BarHeight):
                        break

                    bar_height_y = int(BarHeight[bar_index])

                    bar_x: int = int((j-20)*((width/size)/20))+2 # type: ignore
                    bar_w = 2 
                    bar_h: int | Any = (height) - bar_height_y/50 # type: ignore

                    # Draw the main bar
                    pygame.draw.rect(screen, (color), (bar_x, bar_height_y, bar_w, bar_h)) # type: ignore
                    bar_index += 1  
    
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Exiting application.")
    os._exit(0) 

if __name__ == "__main__":
    
    try:
        # Check if MP3 file exists
        if not os.path.exists(MP3_FILE): # type: ignore
            print(f"Error: MP3 file '{MP3_FILE}' not found.") # type: ignore
            print("Please set the MP3_FILE variable to a valid file path.")
            os._exit(1)
        
        # Load the audio file using librosa for visualization
        print(f"Loading audio from {MP3_FILE}...") # type: ignore
        audio_data, sr = librosa.load(MP3_FILE, sr=RATE, mono=True) # type: ignore
        
        audio_duration = len(audio_data) / sr
        print(f"Audio loaded. Sample rate: {sr}, Duration: {audio_duration:.2f} seconds")
        
        # Convert to the correct shape for processing
        audio_data = audio_data.reshape(-1, 1) if len(audio_data.shape) == 1 else audio_data
        
        # Load and play the MP3 file using pygame mixer
        print("Starting playback...")
        
        # Run the Pygame Loop in the Main Thread
        main_loop(audio_data, audio_duration) # type: ignore

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        os._exit(1)
