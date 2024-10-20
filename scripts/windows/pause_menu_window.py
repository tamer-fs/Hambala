import pygame
import pygame_gui
import os, json
from scripts.uiElements.button_el import Button
from scripts.uiElements.input_entry_el import InputEntry

pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)


class PauseMenuWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager(
            (self.screen_width, self.screen_height),
            theme_path="scripts/windows/title_window.json",
        )

        self.btn_h_percent = 7
        title_rect = pygame.Rect((0, 0), (int(self.screen_width), int(200)))
        self.title = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="GAME PAUSED",
            relative_rect=title_rect,
            anchors={"left": "left", "right": "right"},
        )
        self.continue_game_btn = Button(
            (50, "%"),
            (35, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Continue Game",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.save_game_btn = Button(
            (50, "%"),
            (50, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Save game",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.save_and_exit_btn = Button(
            (50, "%"),
            (60, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Save and Exit",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.save_to_title_btn = Button(
            (50, "%"),
            (70, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Save to title screen",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

    def update(self, events, delta_time):
        self.screen_width, self.screen_height = self.screen.get_size()

        show_window = True
        save_game = False
        quit_game = False
        to_title = False

        for event in events:

            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.continue_game_btn.button:
                    show_window = False
                elif event.ui_element == self.save_game_btn.button:
                    save_game = True
                    show_window = False
                elif event.ui_element == self.save_and_exit_btn.button:
                    save_game = True
                    quit_game = True
                    show_window = False
                elif event.ui_element == self.save_to_title_btn.button:
                    save_game = True
                    to_title = True
                    show_window = False

            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution(
                    (self.screen_width, self.screen_height)
                )

                self.continue_game_btn.update_res(self.screen_width, self.screen_height)
                self.save_game_btn.update_res(self.screen_width, self.screen_height)
                self.save_and_exit_btn.update_res(self.screen_width, self.screen_height)
                self.save_to_title_btn.update_res(self.screen_width, self.screen_height)

            self.manager.process_events(event)

        self.manager.update(delta_time)

        return show_window, save_game, quit_game, to_title

    def draw(self):
        self.manager.draw_ui(self.screen)
