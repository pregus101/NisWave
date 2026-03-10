import pygame
from wave_renderer import WaveVisualizer

class SongBar:
    
    def __init__(self, total_length, current_length, screen_width, screen_height, screen, visualizer):
        self.total_length = total_length
        self.current_length = current_length
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = screen
        self.visualizer = visualizer
    
    def update(self, current_length):
        draw = False
        if current_length is not None:
            self.current_length = current_length
            self.draw()

    def draw(self):
        if self.total_length > 0:
            self.current_bar_width = int(self.current_length / self.total_length * int(640 * ((self.screen_width/1920 + self.screen_height/1147) / 2)))
            self.bar_width_hight = 640 * ((self.screen_width/1920 + self.screen_height/1147) / 2)

            pygame.draw.rect(self.screen, (128, 128, 128), (int(((self.screen_width-self.screen_width/5)/2+self.screen_width/5)-self.bar_width_hight/2), int((self.screen_height/2+(120*((self.screen_width/1920 + self.screen_height/1147) / 2)))+self.bar_width_hight/2), self.bar_width_hight, 6))
            pygame.draw.rect(self.screen, (64, 255, 64), (int(((self.screen_width-self.screen_width/5)/2+self.screen_width/5)-self.bar_width_hight/2), int((self.screen_height/2+(120*((self.screen_width/1920 + self.screen_height/1147) / 2)))+self.bar_width_hight/2), self.current_bar_width, 6))
            Font = pygame.font.SysFont('Arial', 10)
            text_surface = Font.render(f"{int(self.current_length//60)}:{int(self.current_length%60):02d} / {int(self.total_length//60)}:{int(self.total_length%60):02d}", True, (255, 255, 255))
            self.screen.blit(text_surface, (int(((self.screen_width-self.screen_width/5)/2+self.screen_width/5)+self.bar_width_hight/2)+((self.screen_height/1147)*20), int((self.screen_height/2+((120)*((self.screen_width/1920 + self.screen_height/1147) / 2)))+self.bar_width_hight/2)-4))

    def adjust_time(self, mouse_position):
        self.bar_width_hight = 640 * ((self.screen_width/1920 + self.screen_height/1147) / 2)

        # Calculate the new current_length based on mouse position
        relative_x = mouse_position[0] - int(((self.screen_width-self.screen_width/5)/2+self.screen_width/5)-self.bar_width_hight/2)
        relative_x = max(0, min(relative_x, self.bar_width_hight))  # Clamp to bar width
        relative_y = mouse_position[1] - int((self.screen_height/2+(120*(self.screen_width/1920 + self.screen_height/1147) / 2))+self.bar_width_hight/2)
        if 0 <= relative_y <= 6:  # Only adjust if mouse is within the bar height
            new_current_length = (relative_x / self.bar_width_hight) * self.total_length
            if self.visualizer:
                self.visualizer.set_position(new_current_length)
            return new_current_length
        
    def resize(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height