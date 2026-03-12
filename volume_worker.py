import pygame

class volume_manager:
    def __init__(self, screen, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = screen
        # self.visualizer = visualizer
        self.current_volume = 1
        self.max_volume = 1

    def draw(self):
        self.current_bar_width = (self.current_volume / self.max_volume * (320 * ((self.screen_width/1920 + self.screen_height/1147) / 2)))
        self.bar_width_hight = 320 * ((self.screen_width/1920 + self.screen_height/1147) / 2)

        pygame.draw.rect(self.screen, (128, 128, 128), ((self.screen_width-(self.screen_width/5)), (self.screen_height-(self.bar_width_hight/19)*2), self.bar_width_hight, 6))
        pygame.draw.rect(self.screen, (64, 255, 64), ((self.screen_width-(self.screen_width/5)), (self.screen_height-(self.bar_width_hight/19)*2), self.current_bar_width, 6))
        Font = pygame.font.SysFont('Arial', 10)
        text_surface = Font.render(f'{int(self.current_volume/self.max_volume*100)}%', True, (255, 255, 255))
        self.screen.blit(text_surface, ((self.screen_width-(self.screen_width/5)+self.bar_width_hight)+10, (self.screen_height-(self.bar_width_hight/19)*2)-4))

        pygame.draw.circle(self.screen, (255, 255, 255), (((self.screen_width-(self.screen_width/5))+self.current_bar_width), (self.screen_height-(self.bar_width_hight/19)*2)+3), 6, )

    def adjust_volume(self, mouse_position):
        self.bar_width_hight = 320 * ((self.screen_width/1920 + self.screen_height/1147) / 2)

        # Calculate the new volume based on mouse position
        relative_x = mouse_position[0] - (self.screen_width-(self.screen_width/5))
        relative_x = max(-1, min(relative_x, self.bar_width_hight+2))  # Clamp to bar width
        relative_y = mouse_position[1] - ((self.screen_height-(self.bar_width_hight/19)*2))


        if 0 <= relative_y <= 6 and 0 <= relative_x <= self.bar_width_hight+1:  # Only adjust if mouse is within the bar heightf
            self.current_volume = (relative_x / self.bar_width_hight) * self.max_volume
            pygame.mixer_music.set_volume(self.current_volume)
        self.draw()

    def resize(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

# (((self.screen_width-self.screen_width/5)/2+self.screen_width/5)-self.bar_width_hight/2)