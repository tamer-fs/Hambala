import pygame
import pygame_gui
from scripts.uiElements.button_el import Button
from scripts.uiElements.input_entry_el import InputEntry

pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)
        
class CreateGameWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height), theme_path="scripts/windows/title_window.json")
        self.difficulties = ["Easy", "Medium", "Hard"]
        self.difficulty = 0
        # self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text="EXIT BUTTON", manager=self.manager)
        self.btn_h_percent = 7
        self.difficulty_btn = Button((66, "%"), (30, "%"), (28, "%"), (self.btn_h_percent, "%"), f"Game Difficulty: {self.difficulties[self.difficulty]}", self.manager, self.screen_width, self.screen_height)
        self.create_game_btn = Button((50, "%"), (50, "%"), (60, "%"), (self.btn_h_percent, "%"), "Create game...", self.manager, self.screen_width, self.screen_height)
        self.back_btn = Button((15, "%"), (92, "%"), (25, "%"), (self.btn_h_percent, "%"), "Back to main menu...", self.manager, self.screen_width, self.screen_height)
        title_rect = pygame.Rect((0, 0), (int(self.screen_width), int(200)))
        self.title = pygame_gui.elements.UILabel(manager=self.manager, text="CREATE GAME", relative_rect=title_rect, anchors={'left': 'left', 'right': 'right'})
        self.name_input = InputEntry((34, "%"), (30, "%"), (28, "%"), (self.btn_h_percent, "%"), "Game name...", self.manager, self.screen_width, self.screen_height)
        
    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time): 
        playing = True
        current_game_state = "CREATE"
        self.screen_width, self.screen_height = self.screen.get_size() 
        
        # if events != []:
        #     print(events)
        for event in events:
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_btn.button:
                    current_game_state = "TITLE"
                elif event.ui_element == self.create_game_btn.button:
                    current_game_state = "GAME"
                elif event.ui_element == self.difficulty_btn.button:
                    self.difficulty += 1
                    if self.difficulty > 2:
                        self.difficulty = 0
                    self.difficulty_btn.button.set_text(f"Game Difficulty: {self.difficulties[self.difficulty]}")
            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution((self.screen_width, self.screen_height))   
                self.create_game_btn.update_res(self.screen_width, self.screen_height)
                self.back_btn.update_res(self.screen_width, self.screen_height)
                self.difficulty_btn.update_res(self.screen_width, self.screen_height)
                self.name_input.update_res(self.screen_width, self.screen_height)

            self.manager.process_events(event)
            
        self.manager.update(delta_time)
        
        return playing, current_game_state

    def draw(self):
        self.manager.draw_ui(self.screen)
        
        