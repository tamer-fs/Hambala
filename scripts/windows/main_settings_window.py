import pygame
import pygame_gui
from scripts.uiElements.button_el import Button
from pygame_gui.core import ObjectID
import os
import json


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
        self.setting_font = pygame.font.Font(
            os.path.join("assets", "Font", "SpaceMono-Regular.ttf"), 18
        )

        self.btn_h_percent = 7

        self.selected_settings = "GAME"

        self.settings_container_rect = pygame.Rect(0, 0, 500, 500)

        self.back_btn = Button(
            (15, "%"),
            (92, "%"),
            (25, "%"),
            (self.btn_h_percent, "%"),
            "Save & Back to title screen",
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
            (0, 0), (int(self.settings_container_rect.w), int(50))
        )
        self.settings_title = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="Game Settings",
            relative_rect=self.settings_title_rect,
            object_id=ObjectID(object_id="#smallTitle"),
            anchors={
                "left": "left",
            },
        )

        # setting elements
        self.max_fps_slider_rect = pygame.Rect((0, 0), (200, 50))
        self.max_fps_slider = pygame_gui.elements.UIHorizontalSlider(
            manager=self.manager,
            relative_rect=self.max_fps_slider_rect,  # >:(
            start_value=0,
            value_range=[0, 360],
            visible=False,
        )

        self.particles_quality_slider_rect = pygame.Rect((0, 0), (200, 50))
        self.particles_quality_slider = pygame_gui.elements.UIHorizontalSlider(
            manager=self.manager,
            relative_rect=self.particles_quality_slider_rect,
            start_value=0,
            value_range=[0, 3],
            visible=False,
        )

        self.screen_shake_slider_rect = pygame.Rect((0, 0), (200, 50))
        self.screen_shake_slider = pygame_gui.elements.UIHorizontalSlider(
            manager=self.manager,
            relative_rect=self.screen_shake_slider_rect,
            start_value=0,
            value_range=[0, 3],
            visible=False,
        )

        self.master_volume_slider_rect = pygame.Rect((0, 0), (200, 50))
        self.master_volume_slider = pygame_gui.elements.UIHorizontalSlider(
            manager=self.manager,
            relative_rect=self.master_volume_slider_rect,
            start_value=0,
            value_range=[0, 100],
            visible=False,
        )

        self.music_volume_slider_rect = pygame.Rect((0, 0), (200, 50))
        self.music_volume_slider = pygame_gui.elements.UIHorizontalSlider(
            manager=self.manager,
            relative_rect=self.music_volume_slider_rect,
            start_value=0,
            value_range=[0, 100],
            visible=False,
        )

        self.effects_volume_slider_rect = pygame.Rect((0, 0), (200, 50))
        self.effects_volume_slider = pygame_gui.elements.UIHorizontalSlider(
            manager=self.manager,
            relative_rect=self.effects_volume_slider_rect,
            start_value=0,
            value_range=[0, 100],
            visible=False,
        )

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.back_btn.update_res(self.screen_width, self.screen_height)
        self.video_settings_btn.update_res(self.screen_width, self.screen_height)
        self.audio_settings_btn.update_res(self.screen_width, self.screen_height)
        self.game_settings_btn.update_res(self.screen_width, self.screen_height)

        self.load_settings()

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

    def load_settings(self):
        with open(os.path.join("settings.json"), "r") as f:
            ret_json = json.load(f)
            self.max_fps_slider.set_current_value(ret_json["max_fps"])
            self.particles_quality_slider.set_current_value(
                ret_json["particles_quality"]
            )
            self.screen_shake_slider.set_current_value(ret_json["screen_shake"])
            self.master_volume_slider.set_current_value(
                ret_json["master_volume"]
            )
            self.music_volume_slider.set_current_value(ret_json["music_volume"])
            self.effects_volume_slider.set_current_value(
                ret_json["effects_volume"]
            )

    def save_settings(self):
        with open(os.path.join("settings.json"), "w") as f:
            settings = {
                # Video
                "max_fps": self.max_fps_slider.get_current_value(),
                "particles_quality": self.particles_quality_slider.get_current_value(),
                "screen_shake": self.screen_shake_slider.get_current_value(),
                # Audio
                "master_volume": self.master_volume_slider.get_current_value(),
                "music_volume": self.music_volume_slider.get_current_value(),
                "effects_volume": self.effects_volume_slider.get_current_value(),
            }
            json.dump(settings, f)

    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time):
        playing = True
        current_game_state = "SETTINGS"
        selected_world = ""

        self.screen_width, self.screen_height = self.screen.get_size()

        for event in events:
            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                self.save_settings()
                if event.ui_element == self.back_btn.button:
                    current_game_state = "TITLE"
                elif event.ui_element == self.game_settings_btn.button:
                    self.selected_settings = "GAME"
                    self.settings_title.set_text("Game Settings")

                    self.max_fps_slider.hide()
                    self.particles_quality_slider.hide()
                    self.screen_shake_slider.hide()

                    self.music_volume_slider.hide()
                    self.master_volume_slider.hide()
                    self.effects_volume_slider.hide()

                elif event.ui_element == self.video_settings_btn.button:
                    self.selected_settings = "VIDEO"
                    self.settings_title.set_text("Video Settings")

                    self.max_fps_slider.show()
                    self.particles_quality_slider.show()
                    self.screen_shake_slider.show()

                    self.music_volume_slider.hide()
                    self.master_volume_slider.hide()
                    self.effects_volume_slider.hide()

                elif event.ui_element == self.audio_settings_btn.button:
                    self.selected_settings = "AUDIO"
                    self.settings_title.set_text("Audio Settings")

                    self.max_fps_slider.hide()
                    self.particles_quality_slider.hide()
                    self.screen_shake_slider.hide()

                    self.music_volume_slider.show()
                    self.master_volume_slider.show()
                    self.effects_volume_slider.show()

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.max_fps_slider:
                    # self.max_fps_text.set_text(
                    #     f"Max FPS: {self.max_fps_slider.get_current_value()}"
                    # )
                    pass
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

                self.setting_font = pygame.font.Font(
                    os.path.join("assets", "Font", "SpaceMono-Regular.ttf"),
                    int((self.screen_height / 100) * 3),
                )

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

        # self.settings_title.set_position(
        #     (
        #         int(self.screen_width / 100 * 30),
        #         int(
        #             (self.screen_height / 100) * 30
        #             - (self.screen_height / 100) * self.btn_h_percent / 2
        #         ),
        #     )
        # )

        self.settings_title_rect = pygame.Rect(
            (0, 0), (int(self.settings_container_rect.w), int(50))
        )
        self.settings_title_rect.x = int((self.screen_width / 100) * 30)
        self.settings_title_rect.y = int((self.screen_height / 100) * 30)

        self.settings_title.set_position(
            (self.settings_title_rect.x - 125, self.settings_title_rect.y)
        )

        ##################
        # VIDEO SETTINGS #
        ##################
        if self.selected_settings == "VIDEO":
            self.max_fps_slider.set_position(
                (
                    self.settings_container_rect.x
                    + self.settings_container_rect.w
                    - self.max_fps_slider_rect.w
                    - 25,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 14),
                )
            )

            self.max_fps_slider.set_dimensions(
                (
                    int((self.screen_width / 100) * 20),
                    int((self.screen_height / 100) * 6),
                )
            )
            self.max_fps_slider_rect.w = int((self.screen_width / 100) * 20)

            self.particles_quality_slider.set_position(
                (
                    self.settings_container_rect.x
                    + self.settings_container_rect.w
                    - self.particles_quality_slider_rect.w
                    - 25,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 22),
                )
            )

            self.particles_quality_slider.set_dimensions(
                (
                    int((self.screen_width / 100) * 20),
                    int((self.screen_height / 100) * 6),
                )
            )
            self.particles_quality_slider_rect.w = int((self.screen_width / 100) * 20)

            self.screen_shake_slider.set_position(
                (
                    self.settings_container_rect.x
                    + self.settings_container_rect.w
                    - self.screen_shake_slider_rect.w
                    - 25,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 30),
                )
            )

            self.screen_shake_slider.set_dimensions(
                (
                    int((self.screen_width / 100) * 20),
                    int((self.screen_height / 100) * 6),
                )
            )
            self.screen_shake_slider_rect.w = int((self.screen_width / 100) * 20)

            # text!!!
            self.max_fps_text = self.setting_font.render(
                f"Max FPS: {self.max_fps_slider.get_current_value()}",
                True,
                (255, 255, 255),
            )
            self.screen.blit(
                self.max_fps_text,
                (
                    self.settings_container_rect.x + 30,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 14),
                ),
            )

            self.particles_text = {
                0: "Potato quality",
                1: "Meh quality",
                2: "OK quality",
                3: "Nasa quality",
            }[self.particles_quality_slider.get_current_value()]
            self.particles_quality_text = self.setting_font.render(
                f"Particles: {self.particles_text}",
                True,
                (255, 255, 255),
            )
            self.screen.blit(
                self.particles_quality_text,
                (
                    self.settings_container_rect.x + 30,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 22),
                ),
            )

            self.screen_shake_text_str = {
                0: "No screen shake",
                1: "Some screen shake",
                2: "Nice screen shake",
                3: "Too much screen shake",
            }[self.screen_shake_slider.get_current_value()]
            self.screen_shake_text = self.setting_font.render(
                f"Screen shake: {self.screen_shake_text_str}",
                True,
                (255, 255, 255),
            )
            self.screen.blit(
                self.screen_shake_text,
                (
                    self.settings_container_rect.x + 30,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 30),
                ),
            )

        ################
        # AUDIO SETTINGS#
        ################
        if self.selected_settings == "AUDIO":
            self.master_volume_slider.set_position(
                (
                    self.settings_container_rect.x
                    + self.settings_container_rect.w
                    - self.master_volume_slider_rect.w
                    - 25,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 14),
                )
            )

            self.master_volume_slider.set_dimensions(
                (
                    int((self.screen_width / 100) * 20),
                    int((self.screen_height / 100) * 6),
                )
            )
            self.master_volume_slider_rect.w = int((self.screen_width / 100) * 20)

            self.music_volume_slider.set_position(
                (
                    self.settings_container_rect.x
                    + self.settings_container_rect.w
                    - self.music_volume_slider_rect.w
                    - 25,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 22),
                )
            )

            self.music_volume_slider.set_dimensions(
                (
                    int((self.screen_width / 100) * 20),
                    int((self.screen_height / 100) * 6),
                )
            )
            self.music_volume_slider_rect.w = int((self.screen_width / 100) * 20)

            self.effects_volume_slider.set_position(
                (
                    self.settings_container_rect.x
                    + self.settings_container_rect.w
                    - self.effects_volume_slider_rect.w
                    - 25,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 30),
                )
            )

            self.effects_volume_slider.set_dimensions(
                (
                    int((self.screen_width / 100) * 20),
                    int((self.screen_height / 100) * 6),
                )
            )
            self.effects_volume_slider_rect.w = int((self.screen_width / 100) * 20)

            # text!!!
            self.master_volume_text = self.setting_font.render(
                f"Master volume: {self.master_volume_slider.get_current_value()}%",
                True,
                (255, 255, 255),
            )
            self.screen.blit(
                self.master_volume_text,
                (
                    self.settings_container_rect.x + 30,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 14),
                ),
            )

            self.music_volume_text = self.setting_font.render(
                f"Music volume: {self.music_volume_slider.get_current_value()}%",
                True,
                (255, 255, 255),
            )
            self.screen.blit(
                self.music_volume_text,
                (
                    self.settings_container_rect.x + 30,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 22),
                ),
            )

            self.effects_volume_text = self.setting_font.render(
                f"Effects volume: {self.effects_volume_slider.get_current_value()}%",
                True,
                (255, 255, 255),
            )
            self.screen.blit(
                self.effects_volume_text,
                (
                    self.settings_container_rect.x + 30,
                    self.settings_container_rect.y
                    + int((self.screen_height / 100) * 30),
                ),
            )

        pygame.draw.rect(
            self.screen,
            rect=self.settings_container_rect,
            width=2,
            color=(177, 148, 112),
        )

        self.manager.draw_ui(self.screen)
