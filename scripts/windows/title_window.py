import pygame
import pygame_gui

pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)

class TitleWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height), theme_path="scripts/windows/title_window.json")
        self.hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen_width/2-50, self.screen_height/2-25), (100, 50)),
                                                    text='Print input',
                                                    manager=self.manager)
        
    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time): 
        playing = True
        
        self.screen_width, self.screen_height = self.screen.get_size() 
        
        for event in events:
            if event.type == pygame.QUIT:
                playing = False
            elif event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution((self.screen_width, self.screen_height))   
                
                self.hello_button.set_dimensions((self.screen_width/2, 50))         
                hello_width = self.hello_button.get_abs_rect().w
                hello_height = self.hello_button.get_abs_rect().h
                self.hello_button.set_position((self.screen_width/2-hello_width/2, self.screen_height/2-hello_height/2))
                

        self.manager.update(delta_time)
        
        return playing

    def draw(self):
        self.manager.draw_ui(self.screen)