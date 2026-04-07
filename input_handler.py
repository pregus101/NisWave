import pygame
from wave_renderer import WaveVisualizer
# from get_metadata import get_cover_art
import os
from wave_renderer import WaveVisualizer
from get_files import get_files
from queue_handler import new_shuffler

screen = pygame.display.set_mode((400, 400), pygame.RESIZABLE)

class Inputs:

    def __init__(self, current_dir=""):
        self.unshuffled = []
        self.queue = []
        self.playing_song = "None"
        self.playing = False
        self.shuffled = False
        self.visulizer = None
        self.currently_dir = current_dir
        self.index = 0
        self.render = [720, 720]

    def shuffle(self):
        self.shuffled = not(self.shuffled)
        if self.shuffled:
            self.queue = new_shuffler(self.index, self.unshuffled)
        else:
            for i, song in enumerate(self.unshuffled):
                if self.queue[self.index] == song:
                    self.index = i
                    self.queue = self.unshuffled.copy()
    
    def next(self, bar=None):
        if self.visulizer:
            if self.index + 1 >= len(self.queue):
                self.index = 0
                self.playing = False
                self.playing_song = "None"
                self.visulizer.set_pause_state(True)
                self.visulizer = None
                if bar: 
                    bar.total_length = 0
                    bar.visualizer = None

            else:
                self.index += 1
                self.visulizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                                        self.render[0],
                                                        self.render[1])
                self.visulizer.load_audio()
                self.visulizer.play()
                self.playing = True 
                self.playing_song = self.queue[self.index].split("/")[-1][:-4]
                if bar:
                    bar.total_length = pygame.mixer.Sound(os.path.join(self.currently_dir, self.queue[self.index])).get_length()
                    bar.visualizer = self.visulizer
            return self.visulizer

    def pause(self, bar=None):
        if self.visulizer:
            self.playing = not(self.playing)
            self.visulizer.toggle_pause()
        elif bar:
            self.play(bar=bar)
        else:
            self.play()

    def previous(self, bar=None):
        if self.visulizer:
            if self.visulizer.get_position() >= 3.5:
                self.visulizer.set_position(0)
                self.playing = True
                self.playing_song = self.queue[self.index].split("/")[-1][:-4]
            else:
                if self.index - 1 >= 0:
                    self.index -= 1
                    self.visulizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                                    self.render[0],
                                                    self.render[1])
                    self.visulizer.load_audio()
                    self.visulizer.play()
                    self.playing = True
                    self.playing_song = self.queue[self.index].split("/")[-1][:-4]
                    if bar:
                        bar.total_length = pygame.mixer.Sound(os.path.join(self.currently_dir, self.queue[self.index])).get_length()
                        bar.visualizer = self.visulizer

            return self.visulizer

    def play(self, path=None, current_dir=None, bar=None):
        if path != None:
            self.unshuffled, self.index, self.currently_dir = get_files(path)
            if not(self.shuffled):
                self.queue = self.unshuffled.copy()
            else:
                self.queue = new_shuffler(self.index, self.unshuffled)

            self.visulizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                            self.render[0],
                                            self.render[1])
            self.visulizer.load_audio()
            self.visulizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]
            if bar:
                bar.total_length = pygame.mixer.Sound(os.path.join(self.currently_dir, self.queue[self.index])).get_length()
                bar.visualizer = self.visulizer

            return self.visulizer
        
        elif self.queue:
            if not(self.shuffled):
                self.index = 0
            self.visulizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                            self.render[0],
                                            self.render[1])
            self.visulizer.load_audio()
            self.visulizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]

            if bar and self.visulizer != None:
                bar.total_length = pygame.mixer.Sound(os.path.join(self.currently_dir, self.queue[self.index])).get_length()
                bar.visualizer = self.visulizer

            return self.visulizer
        else:
            self.playing = False
            self.playing_song = "None"

    def update_size(self, render):
        self.render = render

# player = Inputs()

# player.play("/Volumes/Samsung/Music/Breakcore for breakfast/【『機動戦士Gundam GQuuuuuuX』アニメMV】「水槽の街から」／照井順政, みきまりあ（NOMELON NOLEMON）.mp3")

# clock = pygame.time.Clock()

# pygame.font.init()
# font = pygame.font.SysFont(os.path.join(os.path.dirname(__file__), "/assets/Cyberbit.ttf"), 30)

# running = True

# while running:

#     clock.tick(5)


#     if not(pygame.mixer_music.get_busy()) and player.playing:
#         player.next()

#     screen.fill((0, 0, 0))
#     screen.blit(font.render(player.playing_song, True, (255, 255, 255)), (0, 0))
#     screen.blit(font.render("Paused: " + str(not(player.playing)), True, (255, 255, 255)), (0, 20))    
#     screen.blit(font.render("Shuffled: " + str(player.shuffled), True, (255, 255, 255)), (0, 40))    
#     screen.blit(font.render("Index: " + str(player.index), True, (255, 255, 255)), (0, 60))    
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

#             if event.key == pygame.K_RETURN:
#                 player.shuffle()
