import pygame
import pygame_gui
import os, json
from scripts.uiElements.button_el import Button
from scripts.uiElements.input_entry_el import InputEntry
from pygame_gui.core import ObjectID

pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)


class DeathMenuWindow:
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
            text="YOU DIED",
            relative_rect=title_rect,
            anchors={"left": "left", "right": "right"},
        )
        description_rect = pygame.Rect((0, 80), (int(self.screen_width), int(200)))
        self.description = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="NIGHTS SURVIVED: _",
            relative_rect=description_rect,
            object_id=ObjectID(object_id="#smallTitle"),
            anchors={"left": "left", "right": "right"},
        )
        # self.continue_game_btn = Button(
        #     (50, "%"),
        #     (35, "%"),
        #     (60, "%"),
        #     (self.btn_h_percent, "%"),
        #     "Continue Game",
        #     self.manager,
        #     self.screen_width,
        #     self.screen_height,
        # )
        # self.save_game_btn = Button(
        #     (50, "%"),
        #     (50, "%"),
        #     (60, "%"),
        #     (self.btn_h_percent, "%"),
        #     "Save game",
        #     self.manager,
        #     self.screen_width,
        #     self.screen_height,
        # )
        self.restart_world_btn = Button(
            (50, "%"),
            (50, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Restart this world",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.exit_to_title_btn = Button(
            (50, "%"),
            (60, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Exit to title screen",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

    def update_res(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.restart_world_btn.update_res(self.screen_width, self.screen_height)
        self.exit_to_title_btn.update_res(self.screen_width, self.screen_height)

        self.restart_world_btn.button.rebuild()
        self.exit_to_title_btn.button.rebuild()
        self.title.rebuild()
        self.description.rebuild()

    def update(self, events, delta_time, night_count):
        self.screen_width, self.screen_height = self.screen.get_size()

        if night_count == 1:
            self.description.set_text(f"You survived {night_count} night!")
        else:
            self.description.set_text(f"You survived {night_count} nights!")

        show_window = True
        restart_game = False
        to_title = False

        for event in events:

            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.restart_world_btn.button:
                    restart_game = True
                    show_window = False
                elif event.ui_element == self.exit_to_title_btn.button:
                    to_title = True
                    show_window = False

            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution(
                    (self.screen_width, self.screen_height)
                )

                self.restart_world_btn.update_res(self.screen_width, self.screen_height)
                self.exit_to_title_btn.update_res(self.screen_width, self.screen_height)
                self.restart_world_btn.button.rebuild()
                self.exit_to_title_btn.button.rebuild()
                self.title.rebuild()

                self.description.rebuild()

            self.manager.process_events(event)

        self.manager.update(delta_time)

        return show_window, restart_game, to_title

    def draw(self):
        self.manager.draw_ui(self.screen)
