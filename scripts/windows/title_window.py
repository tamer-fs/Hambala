import pygame
import pygame_gui


pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)

class Button:
    def __init__(self, x, y, width, height, text, manager, scr_w, scr_h):
        self.x, self.y, self.width, self.height = x, y, width, height # self.x = (100, "%") of self.x = ("100", "px")
        self.text = text
        self.manager = manager
        
        self.px_w = self.width[0] / 100 * scr_w if self.width[1] == "%" else self.width[0]
        self.px_h = self.height[0] / 100 * scr_h if self.height[1] == "%" else self.height[0]
        self.px_x = self.x[0] / 100 * scr_w - self.px_w / 2 if self.x[1] == "%" else self.x[0]
        self.px_y = self.y[0] / 100 * scr_h - self.px_h / 2 if self.y[1] == "%" else self.y[0]
        self.rect = pygame.Rect((self.px_x, self.px_y), (self.px_w, self.px_h))

        self.button = pygame_gui.elements.UIButton(relative_rect=self.rect, text=self.text, manager=self.manager)

        print(self.rect)

    def update_res(self, scr_w, scr_h):
        self.px_w = self.width[0] / 100 * scr_w if self.width[1] == "%" else self.width[0]
        self.px_h = self.height[0] / 100 * scr_h if self.height[1] == "%" else self.height[0]
        self.px_x = self.x[0] / 100 * scr_w - self.px_w / 2 if self.x[1] == "%" else self.x[0]
        self.px_y = self.y[0] / 100 * scr_h - self.px_h / 2 if self.y[1] == "%" else self.y[0]
        self.rect = pygame.Rect((self.px_x, self.px_y), (self.px_w, self.px_h))

        self.button.set_relative_position((self.px_x, self.px_y))
        

class TitleWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height), theme_path="scripts/windows/title_window.json")
        # self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text="EXIT BUTTON", manager=self.manager)
        self.test_btn = Button((50, "%"), (25, "%"), (100, "px"), (50, "px"), "EXIT BUTTON", self.manager, self.screen_width, self.screen_height)


    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time): 
        playing = True
        
        self.screen_width, self.screen_height = self.screen.get_size() 
        
        # if events != []:
        #     print(events)
        for event in events:
            if event.type == pygame.QUIT:
                playing = False
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.test_btn.button:
                    playing = False
                
            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution((self.screen_width, self.screen_height))   
                self.test_btn.update_res(self.screen_width, self.screen_height)

            self.manager.process_events(event)
            
        self.manager.update(delta_time)
        
        return playing

    def draw(self):
        self.manager.draw_ui(self.screen)