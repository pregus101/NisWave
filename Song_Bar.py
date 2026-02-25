import pygame
from wave_renderer import WaveVisualizer

class SongBar:
    def __init__(self, total_length, current_length, screen_width, screen_height, screen):
        self.total_length = total_length
        self.current_length = current_length
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = screen
    
    def update(self, current_length, total_length=None, screen_width=None, screen_height=None, screen=None):
        draw = False
        if current_length is not None:
            self.current_length = current_length
        if total_length is not None:
            self.total_length = total_length
            draw = True
        if screen_width is not None:
            self.screen_width = screen_width
            draw = True
        if screen_height is not None:
            self.screen_height = screen_height
            draw = True
        if draw:
            self.draw(self.total_length, self.current_length, self.screen_width, self.screen_height, screen)

    def draw(self, total_length, current_length, screen_width, screen_height, screen):
        if total_length > 0:
            self.current_bar_width = int(current_length / total_length * int(640 * ((screen_width/1920 + screen_height/1147) / 2)))
            self.bar_width_hight = 640 * ((screen_width/1920 + screen_height/1147) / 2)

            pygame.draw.rect(screen, (128, 128, 128), (int(((screen_width-screen_width/5)/2+screen_width/5)-self.bar_width_hight/2), int((screen_height/2+10+40*2)+self.bar_width_hight/2), self.bar_width_hight, 6))
            pygame.draw.rect(screen, (64, 255, 64), (int(((screen_width-screen_width/5)/2+screen_width/5)-self.bar_width_hight/2), int((screen_height/2+10+40*2)+self.bar_width_hight/2), self.current_bar_width, 6))
            Font = pygame.font.SysFont('Arial', 10)
            text_surface = Font.render(f"{int(current_length//60)}:{int(current_length%60):02d} / {int(total_length//60)}:{int(total_length%60):02d}", True, (255, 255, 255))
            screen.blit(text_surface, (int(((screen_width-screen_width/5)/2+screen_width/5)+self.bar_width_hight/2)+20, int((screen_height/2+10+40*2)+self.bar_width_hight/2)-4))

    def adjust_time(self, mouse_position, total_length, screen_width, screen_height, screen, visualizer=None):
        self.bar_width_hight = 640 * ((screen_width/1920 + screen_height/1147) / 2)

        # Calculate the new current_length based on mouse position
        relative_x = mouse_position[0] - int(((screen_width-screen_width/5)/2+screen_width/5)-self.bar_width_hight/2)
        relative_x = max(0, min(relative_x, self.bar_width_hight))  # Clamp to bar width
        relative_y = mouse_position[1] - int((screen_height/2+10+40*2)+self.bar_width_hight/2)
        if 0 <= relative_y <= 6:  # Only adjust if mouse is within the bar height
            new_current_length = (relative_x / self.bar_width_hight) * total_length
            if visualizer:
                visualizer.set_position(new_current_length)
            return new_current_length