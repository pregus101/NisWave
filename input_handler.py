import pygame
from wave_renderer import WaveVisualizer
from get_metadata import get_cover_art
import os

def skip():
    STARTED = True
    play_pause = "play"
    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Change play/pause button to playing state when a new song is selected
    pygame.mixer.music.stop()  # Stop current music to allow next song to play immediately
    return STARTED, play_pause, play_pause_button_path

def previous(current_time_sec, currently_playing_folder_path, played_songs, queue_raw, queue, SIZE, visualizer, screen, total_length, play_pause, play_pause_button_path, visualizer_running, STARTED, PLAYING_SONG, render_size, cover_art_path, file_path):
    if current_time_sec != None and current_time_sec <= 10:
        try:
            file_path = os.path.join(currently_playing_folder_path, list(played_songs.keys())[-1])
            skip = False 
            play_pause = "play"
        except:
            skip = True
        
        if not skip:
            STARTED = True
            PLAYING_SONG = os.path.basename(file_path)

            queue_raw.insert(played_songs[PLAYING_SONG], PLAYING_SONG)  # Add current song back to the front of the queue_raw
            queue.insert(0, PLAYING_SONG)
            played_songs.pop(PLAYING_SONG, None) # Remove the song from played_songs dictionary
                
            # Get album cover art for the selected track
            render_size, cover_art_path = get_cover_art(file_path, SIZE)

            # CREATE AND START WAVE VISUALIZER
            visualizer = WaveVisualizer(file_path, 
                                        render_size[0], 
                                        render_size[1])
            # Set wave color to contrast with album cover
            visualizer.set_color_from_image(cover_art_path)
            visualizer.load_audio()
            visualizer.play()
            visualizer_running = True

            # Load the sound file as a Sound object to get its length
            temp_sound_object = pygame.mixer.Sound(file_path)
            total_length = temp_sound_object.get_length() # Length in seconds
            play_pause = "play"  # Ensure play/pause state is set to "play" when previous button is clicked
            play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Change play/pause button to playing state when a new song is selected

    else:
        # CREATE AND START WAVE VISUALIZER
        visualizer = WaveVisualizer(file_path, 
                                    render_size[0], 
                                    render_size[1])
        visualizer.load_audio()
        visualizer.play()
        visualizer_running = True
        play_pause = "play"  # Ensure play/pause state is set to "play" when previous button is clicked
        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Change play/pause button to playing state when a new song is selected
    return play_pause, played_songs, queue_raw, queue, play_pause_button_path, visualizer, STARTED, PLAYING_SONG, render_size, cover_art_path, total_length, visualizer_running
