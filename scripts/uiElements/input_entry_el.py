import pygame, pygame_gui

class InputEntry:
    def __init__(self, x, y, width, height, place_holder_text, manager, scr_w, scr_h):
        self.x, self.y, self.width, self.height = x, y, width, height # self.x = (100, "%") of self.x = ("100", "px")
        self.place_holder_text = place_holder_text # begint met niks
        self.manager = manager
        
        self.px_w = self.width[0] / 100 * scr_w if self.width[1] == "%" else self.width[0]
        self.px_h = self.height[0] / 100 * scr_h if self.height[1] == "%" else self.height[0]
        self.px_x = self.x[0] / 100 * scr_w - self.px_w / 2 if self.x[1] == "%" else self.x[0]
        self.px_y = self.y[0] / 100 * scr_h - self.px_h / 2 if self.y[1] == "%" else self.y[0]
        self.rect = pygame.Rect((self.px_x, self.px_y), (self.px_w, self.px_h))

        # self.button = pygame_gui.elements.UIButton(relative_rect=self.rect, text=self.text, manager=self.manager)
        self.input_entry = pygame_gui.elements.UITextEntryLine(relative_rect=self.rect, placeholder_text=self.place_holder_text, manager=self.manager)

    def update_res(self, scr_w, scr_h):
        self.px_w = self.width[0] / 100 * scr_w if self.width[1] == "%" else self.width[0]
        self.px_h = self.height[0] / 100 * scr_h if self.height[1] == "%" else self.height[0]
        self.px_x = self.x[0] / 100 * scr_w - self.px_w / 2 if self.x[1] == "%" else self.x[0]
        self.px_y = self.y[0] / 100 * scr_h - self.px_h / 2 if self.y[1] == "%" else self.y[0]
        self.rect = pygame.Rect((self.px_x, self.px_y), (self.px_w, self.px_h))

        self.input_entry.set_relative_position((self.px_x, self.px_y))
        self.input_entry.set_dimensions((self.px_w, self.px_h))
     
    def disable(self):
        self.input_entry.disable()