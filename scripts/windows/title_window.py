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
        
        
        self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (50, 100)), text="TEST BUTTON", manager=self.manager)
        
    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time): 
        playing = True
        
        self.screen_width, self.screen_height = self.screen.get_size() 
        
        if events != []:
            print(events)
        for event in events:
            if event.type == pygame.QUIT:
                playing = False
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                print("TESTBUTTON")
                
            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution((self.screen_width, self.screen_height))   

            self.manager.process_events(event)
                
                # if event.ui_element == self.test_btn.button:    
                    
        # self.test_btn.update(delta_time)
        self.manager.update(delta_time)
        
        return playing

    def draw(self):
        # self.test_btn.draw(self.scre)
        self.manager.draw_ui(self.screen)