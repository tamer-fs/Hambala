import pygame
import pygame_gui
from scripts.uiElements.button_el import Button
from scripts.uiElements.input_entry_el import InputEntry

pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)
        
class LoadSaveWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height), theme_path="scripts/windows/title_window.json")
        # self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text="EXIT BUTTON", manager=self.manager)
        self.btn_h_percent = 7
        self.load_game_btn = Button((50, "%"), (50, "%"), (60, "%"), (self.btn_h_percent, "%"), "Load game...", self.manager, self.screen_width, self.screen_height)
        self.back_btn = Button((15, "%"), (92, "%"), (25, "%"), (self.btn_h_percent, "%"), "Back to main menu...", self.manager, self.screen_width, self.screen_height)
        title_rect = pygame.Rect((0, 0), (int(self.screen_width), int(200)))
        self.title = pygame_gui.elements.UILabel(manager=self.manager, text="LOAD GAME", relative_rect=title_rect, anchors={'left': 'left', 'right': 'right'})
        self.search_input = InputEntry((50, "%"), (30, "%"), (60, "%"), (self.btn_h_percent, "%"), "Find save...", self.manager, self.screen_width, self.screen_height)
        
    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time): 
        playing = True
        current_game_state = "LOAD"
        self.screen_width, self.screen_height = self.screen.get_size() 
        
        # if events != []:
        #     print(events)
        for event in events:
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_btn.button:
                    current_game_state = "TITLE"
                elif event.ui_element == self.load_game_btn.button:
                    current_game_state = "GAME"

            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution((self.screen_width, self.screen_height))   
                self.load_game_btn.update_res(self.screen_width, self.screen_height)
                self.back_btn.update_res(self.screen_width, self.screen_height)
                self.search_input.update_res(self.screen_width, self.screen_height)

            self.manager.process_events(event)
            
        self.manager.update(delta_time)
        
        return playing, current_game_state

    def draw(self):
        self.manager.draw_ui(self.screen)
        
        