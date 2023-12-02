##############################
#         Place Item         #
##############################


def place_item(plants, item_id, tile_x, tile_y, inventory):
    if (
        not plants[tile_y, tile_x] in [61, 62, 48, 49] and not inventory.hovering_menu
    ):  # prevent placement on tree tile
        plants[tile_y, tile_x] = item_id
        return plants
    else:
        return False
