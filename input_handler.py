import pygame
from wave_renderer import WaveVisualizer
import os
from wave_renderer import WaveVisualizer
from get_files import get_files
from queue_handler import new_shuffler

# screen = pygame.display.set_mode((400, 400), pygame.RESIZABLE)

class Inputs:

    def __init__(self, current_dir: str = "") -> None:
        self.unshuffled: list[str] = []
        self.queue: list[str] = []
        self.playing_song: str = "None"
        self.playing: bool = False
        self.shuffled: bool = False
        self.visualizer: WaveVisualizer | None = None
        self.currently_dir: str = current_dir
        self.index: int = 0
        self.render: list[int] = [720, 720]

    def shuffle(self) -> None:
        self.shuffled = not self.shuffled
        if self.shuffled:
            self.queue = new_shuffler(self.index, self.unshuffled)
            return None
        
        for i, song in enumerate(self.unshuffled):
            if self.queue[self.index] == song:
                self.index = i
                self.queue = self.unshuffled.copy()
        return None
    
    def next(self, bar: None | object = None) -> WaveVisualizer | None:
        if self.visualizer:
            if self.index + 1 >= len(self.queue):
                self.index = 0
                self.playing = False
                self.playing_song = "None"
                self.visualizer.set_pause_state(True)
                self.visualizer = None
                if bar: 
                    bar.total_length = 0
                    bar.visualizer = None

            else:
                self.index += 1
                self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                                        self.render[0],
                                                        self.render[1])
                self.visualizer.load_audio()
                self.visualizer.play()
                self.playing = True 
                self.playing_song = self.queue[self.index].split("/")[-1][:-4]
                if bar:
                    bar.total_length = self.visualizer.audio_duration
                    bar.visualizer = self.visualizer
            return self.visualizer

    def pause(self, bar: None | object = None) -> None:
        if self.visualizer:
            self.playing = not self.playing
            self.visualizer.toggle_pause()
        elif bar:
            self.play(bar=bar)
        else:
            self.play()
        
        return None

    def previous(self, bar: None | object = None) -> WaveVisualizer | None:
        if self.visualizer:
            if self.visualizer.get_position() >= 3.5:
                self.visualizer.set_position(0)

                if not self.playing:
                    self.pause()

            else:
                if self.index - 1 >= 0:
                    self.index -= 1
                    self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                                    self.render[0],
                                                    self.render[1])
                    self.visualizer.load_audio()
                    self.visualizer.play()
                    self.playing = True
                    self.playing_song = self.queue[self.index].split("/")[-1][:-4]
                    if bar:
                        bar.total_length = self.visualizer.audio_duration
                        bar.visualizer = self.visualizer

            return self.visualizer
        return None

    def play(self, path: None | str = None, current_dir: None | str = None, bar: None | object = None) -> WaveVisualizer | None:
        if path != None:
            self.unshuffled, self.index, self.currently_dir = get_files(path)
            if not(self.shuffled):
                self.queue = self.unshuffled.copy()
            else:
                self.queue = new_shuffler(self.index, self.unshuffled)

            self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                            self.render[0],
                                            self.render[1])
            self.visualizer.load_audio()
            self.visualizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]
            if bar:
                bar.total_length = self.visualizer.audio_duration
                bar.visualizer = self.visualizer

            return self.visualizer
        
        elif self.queue:
            if not(self.shuffled):
                self.index = 0
            self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                            self.render[0],
                                            self.render[1])
            self.visualizer.load_audio()
            self.visualizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]

            if bar and self.visualizer != None:
                bar.total_length = self.visualizer.audio_duration
                bar.visualizer = self.visualizer

            return self.visualizer
        else:
            self.playing = False
            self.playing_song = "None"

        return None

    def update_size(self, render: list[int]) -> None:
        self.render = render