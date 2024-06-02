import pygame
import pygame_gui


pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((800, 600), theme_path="menutest.json")

hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                            text='Print input',
                                            manager=manager)

text_input = pygame_gui.elements.UITextEntryBox(relative_rect=pygame.Rect((0, 0), (200, 100)), placeholder_text="voer in", manager=manager)
slider_input = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((400, 0), (200, 50)), start_value=0, value_range=(0, 50), manager=manager)


clock = pygame.time.Clock()
is_running = True

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == hello_button:
                print(text_input.get_text(), slider_input.get_current_value())
                text_input.clear()
        
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == text_input:
                characters = len(text_input.get_text())
                if characters > 10:
                    text_input.set_text(text_input.get_text()[:12])

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()