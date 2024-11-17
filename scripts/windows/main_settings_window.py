import pygame
import pygame_gui
from scripts.uiElements.button_el import Button
from pygame_gui.core import ObjectID
import os


pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)


class MainSettingsWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager(
            (self.screen_width, self.screen_height),
            theme_path="scripts/windows/title_window.json",
        )
        # self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text="EXIT BUTTON", manager=self.manager)

        self.btn_h_percent = 7

        self.selected_settings = "GAME"

        self.settings_container_rect = pygame.Rect(0, 0, 500, 500)

        self.back_btn = Button(
            (15, "%"),
            (92, "%"),
            (25, "%"),
            (self.btn_h_percent, "%"),
            "Back to main menu...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

        # section buttons

        self.audio_settings_btn = Button(
            (15, "%"),
            (50, "%"),
            (25, "%"),
            (self.btn_h_percent, "%"),
            "Audio",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.video_settings_btn = Button(
            (15, "%"),
            (40, "%"),
            (25, "%"),
            (self.btn_h_percent, "%"),
            "Video",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.game_settings_btn = Button(
            (15, "%"),
            (30, "%"),
            (25, "%"),
            (self.btn_h_percent, "%"),
            "Game",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

        title_rect = pygame.Rect((0, 0), (int(self.screen_width), int(200)))
        self.title = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="SETTINGS",
            relative_rect=title_rect,
            anchors={"left": "left", "right": "right"},
        )

        self.settings_title_rect = pygame.Rect(
            (0, 0), (int(self.settings_container_rect.w), int(200))
        )
        self.settings_title = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="Game Settings",
            relative_rect=self.settings_title_rect,
            anchors={"left": "left", "right": "right"},
            object_id=ObjectID(object_id="#smallTitle"),
        )

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.back_btn.update_res(self.screen_width, self.screen_height)
        self.video_settings_btn.update_res(self.screen_width, self.screen_height)
        self.audio_settings_btn.update_res(self.screen_width, self.screen_height)
        self.game_settings_btn.update_res(self.screen_width, self.screen_height)

    def update_res(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.back_btn.update_res(self.screen_width, self.screen_height)
        self.video_settings_btn.update_res(self.screen_width, self.screen_height)
        self.audio_settings_btn.update_res(self.screen_width, self.screen_height)
        self.game_settings_btn.update_res(self.screen_width, self.screen_height)

        game_dirs = os.listdir(os.path.join("saves"))
        button_enabled = len(game_dirs) > 0

        if not button_enabled:
            self.play_last_saved_btn.button.disable()
        else:
            self.play_last_saved_btn.button.enable()

    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time):
        playing = True
        current_game_state = "SETTINGS"
        selected_world = ""

        self.screen_width, self.screen_height = self.screen.get_size()

        # if events != []:
        #     print(events)
        for event in events:
            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_btn.button:
                    current_game_state = "TITLE"
                elif event.ui_element == self.game_settings_btn.button:
                    self.selected_settings = "GAME"
                elif event.ui_element == self.video_settings_btn.button:
                    self.selected_settings = "VIDEO"
                elif event.ui_element == self.audio_settings_btn.button:
                    self.selected_settings = "AUDIO"

            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution(
                    (self.screen_width, self.screen_height)
                )

                self.back_btn.update_res(self.screen_width, self.screen_height)
                self.video_settings_btn.update_res(
                    self.screen_width, self.screen_height
                )
                self.audio_settings_btn.update_res(
                    self.screen_width, self.screen_height
                )
                self.game_settings_btn.update_res(self.screen_width, self.screen_height)

                self.title.rebuild()
                self.settings_title.rebuild()

                self.back_btn.button.rebuild()
                self.game_settings_btn.button.rebuild()
                self.video_settings_btn.button.rebuild()
                self.audio_settings_btn.button.rebuild()

            self.manager.process_events(event)

        self.manager.update(delta_time)

        return playing, current_game_state, selected_world

    def draw(self):

        self.settings_container_rect.y = int(
            (self.screen_height / 100) * 30
            - (self.screen_height / 100) * self.btn_h_percent / 2
        )
        self.settings_container_rect.x = int(self.screen_width / 100 * 30)
        self.settings_container_rect.w = int(self.screen_width / 100 * 67)
        self.settings_container_rect.h = int(self.screen_height / 100 * 68.5)

        gray_surface = pygame.Surface(
            (self.settings_container_rect.w, self.settings_container_rect.h),
            pygame.SRCALPHA,
        )
        gray_surface.fill((0, 0, 0))
        gray_surface.set_alpha(150)
        self.screen.blit(
            gray_surface,
            (self.settings_container_rect.x, self.settings_container_rect.y),
        )

        self.settings_title_rect = pygame.Rect(
            (0, 0), (int(self.settings_container_rect.w), int(50))
        )

        pygame.draw.rect(
            self.screen,
            rect=self.settings_container_rect,
            width=2,
            color=(177, 148, 112),
        )
        self.manager.draw_ui(self.screen)
