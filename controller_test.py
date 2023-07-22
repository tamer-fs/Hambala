import pygame
from pygame.locals import *
import time

pygame.init()
window = pygame.display.set_mode((1000, 1000), pygame.RESIZABLE)
clock = pygame.time.Clock()
x, y = window.get_rect().center
shoot_delay = time.perf_counter()
speed = 7
max_speed_add = 0
last_press_time = time.perf_counter()
time_diff = 0

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
            if event.button == 0:
                max_speed_add = 20
                time_diff = time.perf_counter() - last_press_time
                last_press_time = time.perf_counter()

        if event.type == pygame.JOYHATMOTION:
            print(event)

    if not joystick.get_button(0):
        max_speed_add -= time_diff * 3
        max_speed_add = max(max_speed_add, 0)

    axis_x, axis_y = (joystick.get_axis(0), joystick.get_axis(1))
    if abs(axis_x) > 0.1:
        x = (x + round((7 + max_speed_add) * axis_x)) % window.get_width()
    if abs(axis_y) > 0.1:
        y = (y + round((7 + max_speed_add) * axis_y)) % window.get_height()

    shooting = True if joystick.get_axis(5) > -0.5 else False

    if shooting:
        if time.perf_counter() - shoot_delay > 0.5:
            joystick.rumble(0, 20, 150)
            shoot_delay = time.perf_counter()

    window.fill(0)
    pygame.draw.circle(window, (255, 0, 0), (x, y), 10)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
exit()
