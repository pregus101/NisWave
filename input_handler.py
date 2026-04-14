from wave_renderer import WaveVisualizer
import os
from wave_renderer import WaveVisualizer
from get_files import get_files
from queue_handler import new_shuffler, on_play_shuffle
import random
import pygame
from collections.abc import Callable
from typing import Any

class Buttons:

    def __init__(self, x: int, y: int, func: Callable[[Any], Any], parameters: list[Any], asset_path: str, asset_path_2: str | None = None, togglable: bool = False) -> None:
        self.x: int = x
        self.y: int = y
        self.func: Callable[[Any], Any] = func
        self.parameters: list[Any]
        self.image: pygame.Surface = pygame.image.load(asset_path).convert_alpha()
        self.image.set_alpha(128)
        self.image_rect: pygame.Rect = self.image.get_rect()
        if togglable:
            self.image_2: pygame.Surface = pygame.image.load(asset_path_2).convert_alpha()  # type: ignore
            self.image_2.set_alpha(128)
            self.image_2_rect: pygame.Rect = self.image_2.get_rect() 
            self.togglable: bool = True
            self.toggled: bool = False

    def check_hover(self, mouse_pos: list[int]) -> pygame.Surface:
        if self.image_rect.collidepoint(mouse_pos):
            self.image.set_alpha(256)
            return self.image
        elif self.togglable and self.toggled and self.image_2_rect.collidepoint(mouse_pos):
            self.image_2.set_alpha(256)
            return self.image_2
        elif self.toggled:
            self.image_2.set_alpha(128)
            return self.image_2
        else:
            self.image.set_alpha(128)
            return self.image
        
    def check_click(self, mouse_pos: list[int]) -> tuple[Any, pygame.Surface]:

        func_value: Any = self.func(self)

        if self.togglable:
            self.toggled != self.toggled # type: ignore

        if self.toggled:
            return func_value, self.image_2
        else:
            return func_value, self.image



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
        self.queue_add: int = 0

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
                    bar.total_length = 0 # type: ignore
                    bar.visualizer = None # type: ignore

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
                    bar.total_length = self.visualizer.audio_duration # type: ignore
                    bar.visualizer = self.visualizer  # type: ignore
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
                        bar.total_length = self.visualizer.audio_duration # type: ignore
                        bar.visualizer = self.visualizer  # type: ignore

            return self.visualizer
        return None

    def play(self, path: None | str = None, current_dir: None | str = None, bar: None | object = None) -> WaveVisualizer | None:
        if path != None:
            self.unshuffled, self.index, self.currently_dir = get_files(path) # type: ignore

            self.queue = self.unshuffled.copy()
            
            if self.shuffled:
                self.index = 0
                self.queue = on_play_shuffle(self.unshuffled, path.split("/")[-1])
                

            self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                            self.render[0],
                                            self.render[1])
            self.visualizer.load_audio()
            self.visualizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]
            if bar:
                bar.total_length = self.visualizer.audio_duration # type: ignore
                bar.visualizer = self.visualizer  # type: ignore

            return self.visualizer
        
        elif self.unshuffled:
            self.index = 0

            if self.shuffled:
                song_temp: str = random.choices(self.unshuffled)[0]
                self.queue = on_play_shuffle(self.unshuffled, song_temp)


            self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                            self.render[0],
                                            self.render[1])
            self.visualizer.load_audio()
            self.visualizer.play()
            self.playing = True
            self.playing_song = self.queue[self.index].split("/")[-1][:-4]

            if bar and self.visualizer != None: # type: ignore
                bar.total_length = self.visualizer.audio_duration # type: ignore
                bar.visualizer = self.visualizer  # type: ignore

            return self.visualizer
        else:
            self.playing = False
            self.playing_song = "None"

        return None

    def update_size(self, render: list[int]) -> None:
        self.render = render