#hallo dit is heel cool
import numpy

from func import *
import pygame

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
maxFps = 60

fps_font = pygame.font.Font("assets/Font/Main.ttf", 15)

screenWidth = 1000
screenHeight = 600

screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
pygame.display.set_caption("Hambala")
icon = pygame.image.load("assets/character/idle1.png").convert_alpha()
icon = pygame.transform.scale(icon, (60, 60))
pygame.display.set_icon(icon)
screenWidth = screen.get_width()
screenHeight = screen.get_height()
playing = True
plant_spawn_chance = 3

stamina_icon = pygame.image.load("assets/icons/stamina.png").convert_alpha()
hunger_icon = pygame.image.load("assets/icons/hunger_icon.png").convert_alpha()
health_icon = pygame.image.load("assets/icons/health_icon.png").convert_alpha()


scrollx = 0
scrolly = 0

map_w, map_h = 150, 150

plants, world, world_rotation = create_world(map_w, map_h, plant_spawn_chance)

player_sprint_bar = ValueBar(
    (screenWidth - 208, screenHeight - 33), (200, 25), 8, 100)

player_hunger_bar = ValueBar(
    (screenWidth - 208, screenHeight - 66 - 8), (200, 25), 8, 10000)

player_hp_bar = ValueBar((screenWidth / 2 - screenWidth / 8,
                         screenHeight - 33), (screenWidth / 4, 25), 8, 10)

main_inventory = Inventory((50, 400), (8, screenHeight / 2 - 200))
main_crafting_table = CraftingTable()
main_crafting_table.set_inventory(main_inventory)
main_inventory.set_crafting_table(main_crafting_table)

images = load_img()

particles = []

keys = pygame.key.get_pressed()
player = Player(images, ((map_w * 16) - 48) / 2, ((map_h * 16) - 48) / 2)
particle_perf = -1
player.get_inventory(main_inventory)
main_inventory.get_player(player)

deltaT = 0

prev_player_x = 0
prev_player_y = 0

scrollx = ((map_w * 16) - screenWidth) / 2
scrolly = ((map_h * 16) - screenHeight) / 2

cursor = pygame.image.load("assets/icons/cursor.png").convert_alpha()
pygame.mouse.set_visible(False)
cursor_rect = cursor.get_rect()

while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False

        if event.type == pygame.MOUSEWHEEL:
            main_inventory.mouse_update(event.y)

        if event.type == pygame.VIDEORESIZE:
            screenWidth, screenHeight = screen.get_size()
            player_sprint_bar.reset(
                (screenWidth - 208, screenHeight - 33), (200, 25), 8)
            player_hunger_bar.reset(
                (screenWidth - 208, screenHeight - 66 - 8), (200, 25), 8)
            player_hp_bar.reset(
                (screenWidth / 2 - screenWidth / 8, screenHeight - 33), (screenWidth / 4, 25), 8)
            player.set_window_size(screen)
            main_inventory.reset_pos((8, screenHeight / 2 - 200))
            main_crafting_table.reset()

    screen.fill((0, 0, 0))
    render_world(screen, world, plants, world_rotation, images,
                 scrollx, scrolly, screenWidth, screenHeight)

    player_sprint_bar.draw(
        screen, pygame.Color("#212529"),
        pygame.Color("#343a40"),
        pygame.Color("#F4D35E"),
        stamina_icon,
        (-25, 0),
        5
    )

    player_hunger_bar.draw(
        screen, pygame.Color("#212529"),
        pygame.Color("#343a40"),
        pygame.Color("#bc6c25"),
        hunger_icon,
        (-25, 0),
        5
    )

    player_hp_bar.draw(
        screen, pygame.Color("#212529"),
        pygame.Color("#343a40"),
        pygame.Color('#ae2012'),
        health_icon,
        (-28, -2),
        5
    )

    player_sprint_bar.update(player.energy_value)
    player_hunger_bar.update(player.food_value)
    player_hp_bar.update(player.health_value)
    keys = pygame.key.get_pressed()

    player.walking(keys, deltaT, pygame.mouse.get_pressed())
    player.update(plants, keys, screen)

    particles, particle_perf = spawn_particles(
        particle_perf, player, particles)

    del_list = []
    for i, particle in enumerate(particles):
        particle.update(scrollx, scrolly, deltaT, player, world)
        particle.draw(screen)
        if particle.delete_timer + 0.75 < time.perf_counter():
            del_list.append(i)

    for j in list(sorted(del_list))[::-1]:
        particles.pop(j)

    scrollx += int((player.x - int((screenWidth - 48) / 2) - scrollx) / 5)
    scrolly += int((player.y - int((screenHeight - 48) / 2) - scrolly) / 5)

    scrollx = max(scrollx, 0)
    scrollx = min(scrollx, 16 * map_w - screenWidth)
    scrolly = max(scrolly, 0)
    scrolly = min(scrolly, 16 * map_h - screenHeight)

    prev_player_x = player.x
    prev_player_y = player.y
    player.draw(screen, scrollx, scrolly)

    main_inventory.draw(screen, pygame.mouse.get_pos())
    main_inventory.update(pygame.mouse.get_pressed(), pygame.mouse.get_pos(), screen)

    main_crafting_table.draw(screen)
    main_crafting_table.update(keys, pygame.mouse.get_pos(), pygame.mouse.get_pressed())

    cursor_rect.topleft = pygame.mouse.get_pos()
    if not main_inventory.holding_item and not main_crafting_table.holding_item:
        screen.blit(cursor, cursor_rect)


    fps = clock.get_fps()
    screen.blit(fps_font.render(str(int(fps)), True, (0, 0, 0)), (10, 10))
    pygame.display.update()
    deltaT = clock.tick(60)

pygame.quit()
