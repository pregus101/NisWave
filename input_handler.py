import pygame
from wave_renderer import WaveVisualizer
# from get_metadata import get_cover_art
import os
from wave_renderer import WaveVisualizer

screen = pygame.display.set_mode((400, 400), pygame.RESIZABLE)

def skip():
    STARTED = True
    play_pause = "play"
    play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Change play/pause button to playing state when a new song is selected
    pygame.mixer.music.stop()  # Stop current music to allow next song to play immediately
    return STARTED, play_pause, play_pause_button_path

def previous(current_time_sec, currently_playing_folder_path, played_songs, queue_raw, queue, visualizer, screen, total_length, play_pause, play_pause_button_path, visualizer_running, STARTED, PLAYING_SONG, render_size, cover_art_path, file_path, imageH):
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
            render_size, cover_art_path = imageH.update_image(file_path)

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
        file_path = os.path.join(currently_playing_folder_path, PLAYING_SONG)
        # CREATE AND START WAVE VISUALIZER
        visualizer = WaveVisualizer(file_path, 
                                    render_size[0], 
                                    render_size[1])
        visualizer.load_audio()
        visualizer.play()
        visualizer_running = True
        play_pause = "play"  # Ensure play/pause state is set to "play" when previous button is clicked
        play_pause_button_path = os.path.join(os.path.dirname(__file__), "assets/play_pause.jpg")  # Change play/pause button to playing state when a new song is selected
        # STARTED = True
    return play_pause, played_songs, queue_raw, queue, play_pause_button_path, visualizer, STARTED, PLAYING_SONG, render_size, cover_art_path, total_length, visualizer_running


class Inputs:

    def __init__(self, current_dir=""):
        self.unshuffled = []
        self.queue = ["Music/A collection of collections/♛ #cherryCrush ✮°｡⋆.mp3", "1985.mp3", "somewhere....mp3", "Sorry about my face - please, be quiet.mp3"]
        self.playing_song = ""
        self.playing = False
        self.shuffled = False
        self.visulizer = None
        self.currently_dir = current_dir
        self.index = 0
        self.render = [720, 720]

    def shuffle(self):
        self.shuffled = not(self.shuffled)
        if self.shuffled:
            pass
        else:
            for i, song in enumerate(self.unshuffled):
                if self.queue[self.index] == song:
                    self.index = i
    
    def next(self):
        if self.visulizer:
            if self.index + 1 == len(self.queue):
                self.index = 0
                self.playing = False
                self.playing_song = "None"
                self.visulizer.set_pause_state(True)
                self.visulizer = None
            else:
                self.index += 1
                self.visulizer = WaveVisualizer(self.currently_dir + self.queue[self.index],
                                                        self.render[0],
                                                        self.render[1])
                self.visulizer.load_audio()
                self.visulizer.play()
                self.playing = True 
                self.playing_song = self.queue[self.index].split("/")[-1][:-4]

            return self.visulizer

    def pause(self):
        if self.visulizer:
            self.playing = not(self.playing)
            self.visulizer.toggle_pause()
        else:
            self.play()

    def previous(self):
        if self.visulizer:
            if self.visulizer.get_position() >= 5:
                self.visulizer.set_position(0)
                self.playing = True
                self.playing_song = self.queue[self.index].split("/")[-1][:-4]
            else:
                if self.index - 1 >= 0:
                    self.index -= 1
                    self.visulizer = WaveVisualizer(self.currently_dir + self.queue[self.index],
                                                    self.render[0],
                                                    self.render[1])
                    self.visulizer.load_audio()
                    self.visulizer.play()
                    self.playing = True
                    self.playing_song = self.queue[self.index].split("/")[-1][:-4]
            return self.visulizer

    def play(self, path=None, current_dir=None):
        if path != None:
            self.visulizer = WaveVisualizer(path,
                                            self.render[0],
                                            self.render[1])
            self.visulizer.load_audio()
            self.visulizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]
            return self.visulizer
        
        else:
            self.index = 0
            self.visulizer = WaveVisualizer(self.currently_dir + self.queue[self.index],
                                            self.render[0],
                                            self.render[1])
            self.visulizer.load_audio()
            self.visulizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]


    def get_currently_playing(self):
        return self.playing_song


    def update_size(self, render):
        self.render = render

    def get_playing(self):
        return self.playing

# player = Inputs("/Volumes/Samsung/")

# player.play("/Volumes/Samsung/Music/A collection of collections/♛ #cherryCrush ✮°｡⋆.mp3")

# clock = pygame.time.Clock()

# pygame.font.init()
# font = pygame.font.SysFont(os.path.join(os.path.dirname(__file__), "/assets/Cyberbit.ttf"), 30)

# running = True

# while running:

#     clock.tick(5)


#     if not(pygame.mixer_music.get_busy()) and player.get_playing():
#         player.next()

#     screen.fill((0, 0, 0))
#     screen.blit(font.render(player.get_currently_playing(), True, (255, 255, 255)), (0, 0))
#     screen.blit(font.render("Paused: " + str(not(player.get_playing())), True, (255, 255, 255)), (0, 20))    
#     pygame.display.flip()

#     for event in pygame.event.get():
#         # Exit application when window is closed
#         if event.type == pygame.QUIT:
#             running = False
#             pygame.quit()

#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_LEFT:
#                 player.previous()

#             if event.key == pygame.K_RIGHT:
#                 player.next()

#             if event.key == pygame.K_SPACE:
#                 player.pause()

# "Music/A collection of collections/♛ #cherryCrush ✮°｡⋆.mp3", "1985.mp3", "somewhere....mp3", "Sorry about my face - please, be quiet.mp3"
