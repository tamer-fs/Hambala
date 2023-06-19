import pygame
from pygame.locals import *

pygame.init()
window = pygame.display.set_mode((1000, 1000), pygame.RESIZABLE)
clock = pygame.time.Clock()
x, y = window.get_rect().center

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:
                joystick.rumble(100, 200, 100)

    axis_x, axis_y = (joystick.get_axis(0), joystick.get_axis(1))
    if abs(axis_x) > 0.1:
        x = (x + round(7 * axis_x)) % window.get_width()
    if abs(axis_y) > 0.1:
        y = (y + round(7 * axis_y)) % window.get_height()

    window.fill(0)
    pygame.draw.circle(window, (255, 0, 0), (x, y), 10)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
exit()
