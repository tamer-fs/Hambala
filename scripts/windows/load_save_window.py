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
            (35, "%"),
            (72, "%"),
            (30, "%"),
            (self.btn_h_percent, "%"),
            "Load Game",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

        self.delete_game_btn = Button(
            (65, "%"),
            (72, "%"),
            (30, "%"),
            (self.btn_h_percent, "%"),
            "Delete Game",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

        self.confirm_delete_window = pygame_gui.windows.UIConfirmationDialog(
            ((self.screen_width - 180) / 2, (self.screen_height - 180) / 2, 150, 150),
            manager=self.manager,
            window_title="Are You Sure?",
            action_long_desc="Are you sure you want to delete this save forever? (Forever is a long time!)",
            visible=False,
        )

        self.game_dirs = os.listdir(os.path.join("saves"))
        self.game_names = []
        self.game_names_to_dirs = {}

        self.game_selected = False

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

    def update_res(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.back_btn.update_res(self.screen_width, self.screen_height)
        self.search_input.update_res(self.screen_width, self.screen_height)
        self.load_game_btn.update_res(self.screen_width, self.screen_height)
        self.delete_game_btn.update_res(self.screen_width, self.screen_height)

        games_list_width = self.screen_width / 100 * 60
        window_free_space = (self.screen_width - games_list_width) / 2
        self.games_list_el.set_position((window_free_space, self.screen_height / 3))
        self.games_list_el.set_dimensions((games_list_width, self.screen_height / 3))
        self.confirm_delete_window.set_position(
            ((self.screen_width - 180) / 2, (self.screen_height - 180) / 2)
        )

        self.back_btn.button.rebuild()
        self.search_input.input_entry.rebuild()
        self.load_game_btn.button.rebuild()
        self.games_list_el.rebuild()
        self.title.rebuild()
        self.delete_game_btn.button.rebuild()
        self.confirm_delete_window.rebuild()

    def update_game_dirs(self, filter_text=""):
        self.game_dirs = os.listdir(os.path.join("saves"))
        self.game_names = []
        self.game_names_to_dirs = {}
        self.filtered_list = []

        for game_dir in self.game_dirs:
            with open(os.path.join("saves", game_dir, "save.json")) as f:
                string_save_data = f.read()
                save_data = json.loads(string_save_data)
                # voor een of andere rare reden wilt json niet json'en maar eval werkt wel
                self.game_names.append(save_data["game_name"])
                self.game_names_to_dirs[save_data["game_name"]] = str(game_dir)

        if filter_text != "":
            for game_name in self.game_names:
                if filter_text in game_name:
                    self.filtered_list.append(game_name)
        else:
            self.filtered_list = self.game_names

        self.games_list_el.set_item_list(self.filtered_list)

    def update(self, events, mouse_x, mouse_y, mouse_down, delta_time):
        playing = True
        current_game_state = "LOAD"
        selected_world = ""
        self.screen_width, self.screen_height = self.screen.get_size()

        if self.game_selected:
            self.load_game_btn.button.enable()
            self.delete_game_btn.button.enable()
        else:
            self.load_game_btn.button.disable()
            self.delete_game_btn.button.disable()

        for event in events:
            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.search_input.input_entry:
                    print("verandering cool", self.search_input.input_entry.get_text())
                    self.update_game_dirs(self.search_input.input_entry.get_text())

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_btn.button:
                    current_game_state = "TITLE"
                elif event.ui_element == self.load_game_btn.button:
                    current_game_state = "GAME"
                    selected_world = self.game_names_to_dirs[
                        self.games_list_el.get_single_selection()
                    ]

                    with open("last_played.txt", "w") as f:
                        f.write(selected_world)

                elif event.ui_element == self.delete_game_btn.button:
                    self.confirm_delete_window = pygame_gui.windows.UIConfirmationDialog(
                        (
                            (self.screen_width - 180) / 2,
                            (self.screen_height - 180) / 2,
                            150,
                            150,
                        ),
                        manager=self.manager,
                        window_title="Are You Sure?",
                        action_long_desc="Are you sure you want to delete this save forever? (Forever is a long time!)",
                        visible=False,
                    )
                    self.confirm_delete_window.show()

                    # vanaf hier load save dingen

            if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.games_list_el:
                    if self.games_list_el.get_single_selection() is not None:
                        self.game_selected = True

            if event.type == pygame_gui.UI_SELECTION_LIST_DROPPED_SELECTION:
                if event.ui_element == self.games_list_el:
                    if self.games_list_el.get_single_selection() is None:
                        self.game_selected = False

            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                if event.ui_element == self.confirm_delete_window:
                    delete_save = self.game_names_to_dirs[
                        self.games_list_el.get_single_selection()
                    ]
                    # delete the game selected
                    os.remove(os.path.join("saves", delete_save, "plants.txt"))
                    os.remove(os.path.join("saves", delete_save, "save.json"))
                    os.remove(os.path.join("saves", delete_save, "world_rotation.txt"))
                    os.remove(os.path.join("saves", delete_save, "world.txt"))
                    os.rmdir(os.path.join("saves", delete_save))

                    # reload saves list
                    self.update_game_dirs()
                    self.game_selected = False

            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution(
                    (self.screen_width, self.screen_height)
                )
                self.back_btn.update_res(self.screen_width, self.screen_height)
                self.search_input.update_res(self.screen_width, self.screen_height)
                self.load_game_btn.update_res(self.screen_width, self.screen_height)
                self.delete_game_btn.update_res(self.screen_width, self.screen_height)

                games_list_width = self.screen_width / 100 * 60
                window_free_space = (self.screen_width - games_list_width) / 2
                self.games_list_el.set_position(
                    (window_free_space, self.screen_height / 3)
                )
                self.games_list_el.set_dimensions(
                    (games_list_width, self.screen_height / 3)
                )
                self.confirm_delete_window.set_position(
                    ((self.screen_width - 180) / 2, (self.screen_height - 180) / 2)
                )

                self.back_btn.button.rebuild()
                self.search_input.input_entry.rebuild()
                self.load_game_btn.button.rebuild()
                self.games_list_el.rebuild()
                self.title.rebuild()
                self.delete_game_btn.button.rebuild()
                self.confirm_delete_window.rebuild()

            self.manager.process_events(event)

        self.manager.update(delta_time)

        return playing, current_game_state, selected_world

    def draw(self):
        self.manager.draw_ui(self.screen)
