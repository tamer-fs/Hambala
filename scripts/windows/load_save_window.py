import pygame
import pygame_gui
import os, json
from scripts.uiElements.button_el import Button
from scripts.uiElements.input_entry_el import InputEntry

pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)


class LoadSaveWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager(
            (self.screen_width, self.screen_height),
            theme_path="scripts/windows/title_window.json",
        )
        # self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text="EXIT BUTTON", manager=self.manager)
        self.btn_h_percent = 7
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
        title_rect = pygame.Rect((0, 0), (int(self.screen_width), int(200)))
        self.title = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="LOAD GAME",
            relative_rect=title_rect,
            anchors={"left": "left", "right": "right"},
        )
        self.search_input = InputEntry(
            (50, "%"),
            (28, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Find save...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.load_game_btn = Button(
            (50, "%"),
            (72, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Load Game",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

        self.game_dirs = os.listdir(os.path.join("saves"))
        self.game_names = []
        self.game_names_to_dirs = {}

        for game_dir in self.game_dirs:
            with open(os.path.join("saves", game_dir, "save.json")) as f:
                string_save_data = f.read()
                save_data = json.loads(string_save_data)
                # voor een of andere rare reden wilt json niet json'en maar eval werkt wel
                self.game_names.append(save_data["game_name"])
                self.game_names_to_dirs[save_data["game_name"]] = str(game_dir)

        games_list_width = self.screen_width / 100 * 60
        window_free_space = (self.screen_width - games_list_width) / 2
        self.games_list_el = None
        self.games_list_el = pygame_gui.elements.UISelectionList(
            manager=self.manager,
            relative_rect=pygame.Rect(
                window_free_space,
                self.screen_height / 3,
                games_list_width,
                self.screen_height / 3,
            ),
            item_list=self.game_names,
        )

    def update_game_dirs(self):
        self.game_dirs = os.listdir(os.path.join("saves"))
        self.game_names = []
        self.game_names_to_dirs = {}

        for game_dir in self.game_dirs:
            with open(os.path.join("saves", game_dir, "save.json")) as f:
                string_save_data = f.read()
                save_data = json.loads(string_save_data)
                # voor een of andere rare reden wilt json niet json'en maar eval werkt wel
                self.game_names.append(save_data["game_name"])
                self.game_names_to_dirs[save_data["game_name"]] = str(game_dir)

        self.games_list_el.set_item_list(self.game_names)

    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time):
        playing = True
        current_game_state = "LOAD"
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
                elif event.ui_element == self.load_game_btn.button:
                    current_game_state = "GAME"
                    selected_world = self.game_names_to_dirs[
                        self.games_list_el.get_single_selection()
                    ]
                    print(selected_world)

                    # vanaf hier load save dingen

            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution(
                    (self.screen_width, self.screen_height)
                )
                self.back_btn.update_res(self.screen_width, self.screen_height)
                self.search_input.update_res(self.screen_width, self.screen_height)
                self.load_game_btn.update_res(self.screen_width, self.screen_height)

                games_list_width = self.screen_width / 100 * 60
                window_free_space = (self.screen_width - games_list_width) / 2
                self.games_list_el.set_position(
                    (window_free_space, self.screen_height / 3)
                )
                self.games_list_el.set_dimensions(
                    (games_list_width, self.screen_height / 3)
                )

            self.manager.process_events(event)

        self.manager.update(delta_time)

        return playing, current_game_state, selected_world

    def draw(self):
        self.manager.draw_ui(self.screen)
