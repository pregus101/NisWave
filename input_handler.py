from pathlib import Path
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

    def __init__(self, x: int, y: int, func: Callable[[Any], Any], parameters: list[Any], asset_path: str, asset_path_2: str | None = None, togglable: bool = False, screen: pygame.Surface | None = None) -> None:
        self.x: int = x
        self.y: int = y
        self.func: Callable[[Any], Any] = func
        self.parameters: list[Any] = parameters
        self.image: pygame.Surface = pygame.image.load(asset_path).convert_alpha()
        self.image.set_alpha(128)
        self.image_rect: pygame.Rect = self.image.get_rect()
        self.image_rect.center = (x, y)
        self.screen: pygame.Surface | None = screen
        self.window_size: list[int] = screen.get_size() if screen else [0, 0] # type: ignore
        self.togglable: bool = togglable
        if togglable:
            self.image_2: pygame.Surface = pygame.image.load(asset_path_2).convert_alpha()  # type: ignore
            self.image_2.set_alpha(128)
            self.image_2_rect: pygame.Rect = self.image_2.get_rect() 
            self.image_2_rect.center = (x, y)
            self.togglable: bool = True
            self.toggled: bool = False

    def check_hover(self, mouse_pos: list[int]) -> pygame.Surface: # type: ignore
        if self.image_rect.collidepoint(mouse_pos) or (self.togglable and self.image_2_rect.collidepoint(mouse_pos)):
            self.image.set_alpha(256)
            if self.togglable:
                self.image_2.set_alpha(256)
        else:
            self.image.set_alpha(128)
            if self.togglable:
                self.image_2.set_alpha(128)
        
    def check_click(self, mouse_pos: list[int]) -> tuple[Any, pygame.Surface]: # type: ignore
        if self.image_rect.collidepoint(mouse_pos) or (self.togglable and self.toggled and self.image_2_rect.collidepoint(mouse_pos)):
            if self.parameters:
                func_value: Any = self.func(self.parameters)
            else:
                func_value: Any = self.func() # type: ignore

            if self.togglable:
                self.toggled = not self.toggled

                if self.toggled:
                    return func_value, self.image_2 # type: ignore
                else:
                    return func_value, self.image # type: ignore
        
    def update_position(self) -> None:
        self.x -= self.window_size[0] - self.screen.get_width() if self.screen else 0
        self.y -= self.window_size[1] - self.screen.get_height() if self.screen else 0
        self.window_size = self.screen.get_size() if self.screen else self.window_size # type: ignore
        self.image_rect.center = (self.x, self.y)
        if self.togglable:
            self.image_2_rect.center = (self.x, self.y)

    def get_position(self) -> list[int]:
        return [self.x, self.y]
    
    def draw_button(self) -> None:
        if self.screen:
            if self.togglable and self.toggled:
                self.screen.blit(self.image_2, self.image_2_rect)
            else:
                self.screen.blit(self.image, self.image_rect)

    def set_button_toggled(self, toggled: bool) -> None:
        if self.togglable:
            self.toggled = toggled



class Inputs:

    def __init__(self, current_dir: str = "", bar: None | object = None) -> None:
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
        self.nav_dir: str = current_dir
        self.bar: None | object = None
        self.toggle_bar: bool = True

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
    
    def toggle_bars(self) -> None:
        self.toggle_bar = not self.toggle_bar
        if self.visualizer:
            self.visualizer.toggle_bars()
        
    
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
                elif self.bar:
                    self.bar.total_length = 0 # type: ignore
                    self.bar.visualizer = None # type: ignore
                return None

            else:
                self.index += 1
                self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                                        self.render[0],
                                                        self.render[1],
                                                        render_bars=self.toggle_bar)
                self.visualizer.load_audio()
                self.visualizer.play()
                self.playing = True 
                self.playing_song = Path(self.queue[self.index]).name
                if bar:
                    bar.total_length = self.visualizer.audio_duration # type: ignore
                    bar.visualizer = self.visualizer  # type: ignore
                elif self.bar:
                    self.bar.total_length = self.visualizer.audio_duration # type: ignore
                    self.bar.visualizer = self.visualizer  # type: ignore
            return self.visualizer

    def pause(self, bar: None | object = None) -> None | WaveVisualizer:
        if self.visualizer:
            self.playing = not self.playing
            self.visualizer.toggle_pause()
        elif bar:
            return self.play(bar=bar)
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
                                                    self.render[1],
                                                    render_bars=self.toggle_bar)
                    self.visualizer.load_audio()
                    self.visualizer.play()
                    self.playing = True
                    self.playing_song = Path(self.queue[self.index]).name
                    if bar:
                        bar.total_length = self.visualizer.audio_duration # type: ignore
                        bar.visualizer = self.visualizer  # type: ignore
                    elif self.bar:
                        self.bar.total_length = self.visualizer.audio_duration # type: ignore
                        self.bar.visualizer = self.visualizer  # type: ignore

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
                                            self.render[1],
                                            render_bars=self.toggle_bar)
            self.visualizer.load_audio()
            self.visualizer.play()
            self.playing = True
            self.playing_song = Path(self.queue[self.index]).name
            if bar:
                bar.total_length = self.visualizer.audio_duration # type: ignore
                bar.visualizer = self.visualizer  # type: ignore
            elif self.bar:
                self.bar.total_length = self.visualizer.audio_duration # type: ignore
                self.bar.visualizer = self.visualizer  # type: ignore

            return self.visualizer
        
        else:
            self.currently_dir = self.nav_dir

            self.index = 0
            
            self.unshuffled = get_files(self.nav_dir, folder_type=True) # type: ignore
            self.queue = self.unshuffled.copy()

            if self.shuffled:
                self.index = random.randint(0, len(self.queue)-1)
                self.queue = on_play_shuffle(self.unshuffled, self.queue[self.index].split("/")[-1])

            if self.queue:
                self.visualizer = WaveVisualizer(os.path.join(self.currently_dir, self.queue[self.index]),
                                                self.render[0],
                                                self.render[1],
                                                render_bars=self.toggle_bar)
                self.visualizer.load_audio()
                self.visualizer.play()
                self.playing = True
                self.playing_song = Path(self.queue[self.index]).name
                if bar:
                    bar.total_length = self.visualizer.audio_duration # type: ignore
                    bar.visualizer = self.visualizer  # type: ignore
                elif self.bar:
                    self.bar.total_length = self.visualizer.audio_duration # type: ignore
                    self.bar.visualizer = self.visualizer  # type: ignore
                
                return self.visualizer

        return None

    def update_size(self, render: list[int]) -> None:
        self.render = render

    def get_image_path(self) -> str:
        if self.visualizer:
            return os.path.join(self.currently_dir, self.queue[self.index])
        return ""