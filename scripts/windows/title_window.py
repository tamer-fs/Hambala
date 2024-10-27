import pygame
import pygame_gui
from scripts.uiElements.button_el import Button


pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)


class TitleWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager(
            (self.screen_width, self.screen_height),
            theme_path="scripts/windows/title_window.json",
        )
        # self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text="EXIT BUTTON", manager=self.manager)
        self.btn_h_percent = 7
        self.play_last_saved_btn = Button(
            (50, "%"),
            (30, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Play last saved...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.load_game_btn = Button(
            (50, "%"),
            (40, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Load game...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.create_game_btn = Button(
            (50, "%"),
            (55, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Create new game ...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.settings_btn = Button(
            (35, "%"),
            (90, "%"),
            (30, "%"),
            (self.btn_h_percent, "%"),
            "SETTINGS",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.quit_btn = Button(
            (65, "%"),
            (90, "%"),
            (30, "%"),
            (self.btn_h_percent, "%"),
            "QUIT GAME",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

        title_rect = pygame.Rect((0, 0), (int(self.screen_width), int(200)))
        self.title = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="HAMBALA",
            relative_rect=title_rect,
            anchors={"left": "left", "right": "right"},
        )

        self.has_save = True

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.play_last_saved_btn.update_res(self.screen_width, self.screen_height)
        self.load_game_btn.update_res(self.screen_width, self.screen_height)
        self.create_game_btn.update_res(self.screen_width, self.screen_height)
        self.quit_btn.update_res(self.screen_width, self.screen_height)
        self.settings_btn.update_res(self.screen_width, self.screen_height)

    def update_res(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.play_last_saved_btn.update_res(self.screen_width, self.screen_height)
        self.load_game_btn.update_res(self.screen_width, self.screen_height)
        self.create_game_btn.update_res(self.screen_width, self.screen_height)
        self.quit_btn.update_res(self.screen_width, self.screen_height)
        self.settings_btn.update_res(self.screen_width, self.screen_height)

    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time):
        playing = True
        current_game_state = "TITLE"

        self.screen_width, self.screen_height = self.screen.get_size()

        # if events != []:
        #     print(events)
        for event in events:
            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.quit_btn.button:
                    playing = False
                if event.ui_element == self.create_game_btn.button:
                    current_game_state = "CREATE"
                if event.ui_element == self.load_game_btn.button:
                    current_game_state = "LOAD"

            if not self.has_save:
                self.load_game_btn.disable()
                self.play_last_saved_btn.disable()

            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution(
                    (self.screen_width, self.screen_height)
                )
                self.play_last_saved_btn.update_res(
                    self.screen_width, self.screen_height
                )
                self.load_game_btn.update_res(self.screen_width, self.screen_height)
                self.create_game_btn.update_res(self.screen_width, self.screen_height)
                self.quit_btn.update_res(self.screen_width, self.screen_height)
                self.settings_btn.update_res(self.screen_width, self.screen_height)

                self.load_game_btn.button.rebuild()
                self.create_game_btn.button.rebuild()
                self.quit_btn.button.rebuild()
                self.settings_btn.button.rebuild()
                self.title.rebuild()
                self.play_last_saved_btn.button.rebuild()

            self.manager.process_events(event)

        self.manager.update(delta_time)

        return playing, current_game_state

    def draw(self):
        self.manager.draw_ui(self.screen)
