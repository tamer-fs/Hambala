##############################
#         Place Item         #
##############################
import pygame


def place_item(plants, item_id, tile_x, tile_y, inventory, animals, enemies):
    if (
        not plants[tile_y, tile_x] in [61, 62, 48, 49] and not inventory.hovering_menu
    ):  # prevent placement on tree tile

        on_animal = False
        on_enemy = False

        # check animal
        for animal_key in animals.animal_dict:
            animal = animals.animal_dict[animal_key]
            animal_rect = animal[0]
            true_x = tile_x * 16
            true_y = tile_y * 16
            tile_rect = pygame.Rect(true_x, true_y, 16, 16)
            if animal_rect.colliderect(tile_rect):
                on_animal = True
                break

        # check enemy
        for enemy in enemies.alive_enemies:
            enemy_rect = enemy["rect"]
            true_x = tile_x * 16
            true_y = tile_y * 16
            tile_rect = pygame.Rect(true_x, true_y, 16, 16)
            if enemy_rect.colliderect(tile_rect):
                on_enemy = True
                break

        if not (on_animal or on_enemy):
            plants[tile_y, tile_x] = item_id
            return plants
        else:
            return False
    else:
        return False
