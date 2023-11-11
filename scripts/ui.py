import pygame
import time
from func import *
from scripts.particle import *

##############################
#         Value bar          #
##############################


class ValueBar:
    def __init__(self, pos, size, margin, max_value):
        self.background = pygame.Rect(pos, size)
        self.foreground = pygame.Rect(
            (pos[0] + margin / 2, pos[1] + margin / 2),
            (size[0] - margin, size[1] - margin),
        )
        self.shadow = pygame.Rect(
            (pos[0] + margin / 2, pos[1] + margin / 2),
            (size[0] - margin, size[1] - margin),
        )
        self.value = 0
        self.max_value = max_value
        self.width = self.foreground.w
        self.pos = pos

    def draw(self, screen, bg_color, shadow_color, fg_color, icon, padding, radius):
        pygame.draw.rect(screen, bg_color, self.background, border_radius=radius)
        pygame.draw.rect(screen, shadow_color, self.shadow, border_radius=radius - 2)
        pygame.draw.rect(screen, fg_color, self.foreground, border_radius=radius - 2)
        screen.blit(icon, (self.pos[0] + padding[0], self.pos[1] + padding[1]))

    def reset(self, pos, size, margin):
        self.pos = pos
        self.background = pygame.Rect(pos, size)
        self.foreground = pygame.Rect(
            (pos[0] + margin / 2, pos[1] + margin / 2),
            (size[0] - margin, size[1] - margin),
        )
        self.shadow = pygame.Rect(
            (pos[0] + margin / 2, pos[1] + margin / 2),
            (size[0] - margin, size[1] - margin),
        )
        self.width = self.foreground.w

    def update(self, value):
        self.foreground.w = value * (self.width / self.max_value)


##############################
#         Inventory          #
##############################


class Inventory:
    def __init__(self, size, pos):
        self.player = None
        self.crafting_table = None
        self.size = size
        self.pos = pos
        self.bar = pygame.Rect(pos, (size[0], size[1] + 2))
        self.block = pygame.Rect((pos[0] + 8, pos[1] - 8), (size[0] - 16, size[1] - 8))
        self.backpack_margin = 55
        self.bar_backback = pygame.Rect(
            (pos[0] + self.backpack_margin, pos[1]), (size[0] * 2 - 2, size[1] + 2)
        )
        self.backpack_block = pygame.Rect(
            (pos[0] + 8 + self.backpack_margin, pos[1] - 8), (size[0] - 16, size[1] - 8)
        )
        self.blocks = []  # 9 normal always visible slots
        self.backpack_blocks = []  # 9 backback slots
        self.block_y = 0
        self.backpack_block_y = 0
        self.colors = ["orange", "grey", "black"]
        self.color = "orange"
        self.block_color = pygame.Color("#343a40")
        self.selected_block = 0
        self.backpack_visible = False
        self.last_time = 0
        self.item_direction = -1
        self.item_speed = 0.3

        self.placeable_items = ["torch ", "tomato "]
        self.can_place_item = False  # if currently held item can be placed or not

        self.pic_dict = {}
        self.pic_dict_small = {}
        self.items_dict = {
            "tomato ": ["assets/floor/tile127.png", 30],
            "flower ": ["assets/floor/tile011.png", 30],
            "sword ": ["assets/tools/Sword-1.png", 37],
            "stone ": ["assets/floor/tile010.png", 30],
            "axe ": ["assets/tools/axe.png", 33],
            "log ": ["assets/floor/tile131.png", 33],
            "meat ": ["assets/food/26.png", 30],
            "tomato ": ["assets/floor/tile127.png", 30],
            "flower ": ["assets/floor/tile011.png", 30],
            "cookie ": ["assets/food/00.png", 30],
            "pickaxe ": ["assets/tools/pickaxe.png", 33],
            "rat's tail ": ["assets/food/73.png", 30],
            "lantern ": ["assets/tools/lantern.png", 30],
            "coal ": ["assets/ores/coal.png", 30],
            "torch ": ["assets/tools/torch.png", 30],
        }

        self.items_dict_small = {
            "tomato ": ["assets/floor/tile127.png", 15],
            "flower ": ["assets/floor/tile011.png", 15],
            "sword ": ["assets/tools/Sword-1.png", 12],
            "stone ": ["assets/floor/tile010.png", 15],
            "axe ": ["assets/tools/axe.png", 18],
            "log ": ["assets/floor/tile131.png", 18],
            "meat ": ["assets/food/26.png", 15],
            "tomato ": ["assets/floor/tile127.png", 15],
            "flower ": ["assets/floor/tile011.png", 15],
            "cookie ": ["assets/food/00.png", 15],
            "pickaxe ": ["assets/tools/pickaxe.png", 18],
            "rat's tail ": ["assets/food/73.png", 15],
            "lantern ": ["assets/tools/lantern.png", 15],
            "coal ": ["assets/ores/coal.png", 16],
            "torch ": ["assets/tools/torch.png", 16],
        }

        for item in self.items_dict:
            self.pic_dict[item] = pygame.image.load(
                f"{self.items_dict[item][0]}"
            ).convert_alpha()
            self.pic_dict[item] = pygame.transform.scale(
                self.pic_dict[item],
                (self.items_dict[item][1], self.items_dict[item][1]),
            )

        for item in self.items_dict_small:
            self.pic_dict_small[item] = pygame.transform.scale(
                pygame.image.load(f"{self.items_dict_small[item][0]}").convert_alpha(),
                (self.items_dict_small[item][1], self.items_dict_small[item][1]),
            )

        # self.tomato_img = pygame.image.load("assets/floor/tile127.png").convert_alpha()
        # self.flower_img = pygame.image.load("assets/floor/tile011.png").convert_alpha()
        # self.sword_img = pygame.image.load("assets/tools/Sword-1.png").convert_alpha()
        # self.stone_img = pygame.image.load("assets/floor/tile010.png").convert_alpha()
        # self.pickaxe_img = pygame.image.load("assets/tools/pickaxe.png").convert_alpha()
        # self.axe_img = pygame.image.load("assets/tools/axe.png").convert_alpha()
        # self.log_img = pygame.image.load("assets/floor/tile131.png").convert_alpha()
        # self.meat_img = pygame.image.load("assets/food/26.png").convert_alpha()
        # self.meat_img = pygame.transform.scale(self.meat_img, (30, 30))
        # self.cookie_img = pygame.image.load("assets/food/00.png").convert_alpha()
        # self.tomato_img = pygame.transform.scale(self.tomato_img, (30, 30))
        # self.flower_img = pygame.transform.scale(self.flower_img, (30, 30))
        # self.stone_img = pygame.transform.scale(self.stone_img, (30, 30))
        # self.sword_img = pygame.transform.scale(self.sword_img, (37, 37))
        # self.pickaxe_img = pygame.transform.scale(self.pickaxe_img, (33, 33))
        # self.axe_img = pygame.transform.scale(self.axe_img, (33, 33))
        # self.log_img = pygame.transform.scale(self.log_img, (33, 33))
        # self.cookie_img = pygame.transform.scale(self.cookie_img, (30, 30))

        self.description = ""
        self.font = pygame.font.Font("assets/Font/SpaceMono-Regular.ttf", 12)
        self.clicked_item = ""
        self.holding_item = False
        self.can_fill = True
        self.eating_sound = pygame.mixer.Sound("assets/sounds/eating.wav")
        self.hovering_menu = False
        self.holding_pickaxe = False
        self.holding_axe = False
        self.dropped_items = []
        self.given_items = {
            0: "axe ",
            1: "pickaxe ",
            2: "lantern ",
            3: "coal ",
            4: "sword ",
            5: "",
            6: "",
            7: "",
            8: "",
            9: "",
            10: "",
            11: "",
        }
        self.block_fill = {}
        self.dropped_items = {}
        for i in range(27):
            self.block_fill[i] = self.given_items[i] if i in self.given_items else ""

        self.item_code_dict = {"torch ": 138, "tomato ": 110}

        self.full_key_dict = {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: False,
            6: False,
            7: False,
            8: False,
            9: False,
            10: False,
            11: False,
            12: False,
            13: False,
            14: False,
            15: False,
            16: False,
            17: False,
            18: False,
            19: False,
            20: False,
            21: False,
            22: False,
            23: False,
            24: False,
            25: False,
            26: False,
        }

        self.create_blocks()

    def create_blocks(self):
        for x in range(9):
            self.blocks.append(
                pygame.Rect(
                    self.pos[0] + 8,
                    self.pos[1] + self.block_y + 8,
                    self.size[0] - 16,
                    self.size[1] / 10.5 - 8,
                )
            )
            self.block_y += self.size[1] / 9

        for x in range(9):
            self.blocks.append(
                pygame.Rect(
                    self.pos[0] + 8 + self.backpack_margin,
                    self.pos[1] + self.backpack_block_y + 8,
                    self.size[0] - 16,
                    self.size[1] / 10.5 - 8,
                )
            )
            self.backpack_block_y += self.size[1] / 9

        self.backpack_block_y = 0

        for x in range(9):
            self.blocks.append(
                pygame.Rect(
                    self.pos[0] + self.backpack_margin * 2,
                    self.pos[1] + self.backpack_block_y + 8,
                    self.size[0] - 16,
                    self.size[1] / 10.5 - 8,
                )
            )
            self.backpack_block_y += self.size[1] / 9

    def add_item(self, item):
        if not bool(self.block_fill[self.selected_block]):
            self.block_fill[self.selected_block] = item
        else:
            for x in range(27):
                if not bool(self.block_fill[x]):
                    self.block_fill[x] = item
                    break

    def get_player(self, player):
        self.player = player

    def set_crafting_table(self, crafting_table):
        self.crafting_table = crafting_table

    def reset_pos(self, pos):
        self.bar = pygame.Rect(pos, (self.size[0], self.size[1] + 2))

        self.block_y = 0
        self.blocks = []

        for x in range(9):
            self.blocks.append(
                pygame.Rect(
                    pos[0] + 8,
                    pos[1] + self.block_y + 8,
                    self.size[0] - 16,
                    self.size[1] / 10.5 - 8,
                )
            )
            self.block_y += self.size[1] / 9

        self.backpack_margin = 55
        self.bar_backback = pygame.Rect(
            (pos[0] + self.backpack_margin, pos[1]),
            (self.size[0] * 2 - 2, self.size[1] + 2),
        )
        self.backpack_block = pygame.Rect(
            (pos[0] + 8 + self.backpack_margin, pos[1] - 8),
            (self.size[0] - 16, self.size[1] - 8),
        )
        self.backpack_block_y = 0

        self.block_y = 0

        for x in range(9):
            self.blocks.append(
                pygame.Rect(
                    pos[0] + 8 + self.backpack_margin,
                    pos[1] + self.block_y + 8,
                    self.size[0] - 16,
                    self.size[1] / 10.5 - 8,
                )
            )
            self.block_y += self.size[1] / 9

        self.backpack_block_y = 0

        for x in range(9):
            self.blocks.append(
                pygame.Rect(
                    pos[0] + self.backpack_margin * 2,
                    pos[1] + self.backpack_block_y + 8,
                    self.size[0] - 16,
                    self.size[1] / 10.5 - 8,
                )
            )
            self.backpack_block_y += self.size[1] / 9

    def draw(self, screen, pos, scrollx, scrolly):
        pygame.draw.rect(screen, pygame.Color("#212529"), self.bar, border_radius=8)
        if self.backpack_visible:
            pygame.draw.rect(
                screen, pygame.Color("#212529"), self.bar_backback, border_radius=8
            )

        # for index, block in enumerate(self.blocks):
        #
        #     pygame.draw.rect(screen, self.block_color, block, border_radius=4)
        #
        #     if block.collidepoint(pos[0], pos[1]) and (self.holding_item or self.crafting_table.holding_item):
        #         pygame.draw.rect(screen, (150, 150, 150), block, border_radius=4)
        #
        #
        #     if self.block_fill[index] != '':
        #         screen.blit(self.pic_dict[self.block_fill[index]], block)

        for i in self.dropped_items:
            item = self.dropped_items[i]
            image_code = item[0]
            screen.blit(
                self.pic_dict_small[image_code], (item[1] - scrollx, item[2] - scrolly)
            )
            if time.perf_counter() - self.last_time > 0.5:
                self.last_time = time.perf_counter()
                if self.item_direction == 1:
                    self.item_direction = -1
                else:
                    self.item_direction = 1

            item[2] += self.item_direction * self.item_speed

            if (
                get_distance(item[1], item[2], self.player.x + 12, self.player.y + 12)
                < 50
            ):
                item[1] -= (item[1] - self.player.x - 12) / 5
                item[2] -= (item[2] - self.player.y) / 5
                if (
                    get_distance(
                        item[1], item[2], self.player.x + 12, self.player.y + 12
                    )
                    < 17
                ):
                    self.add_item(item[0])
                    self.dropped_items.pop(i)
                    break

            if time.perf_counter() - item[3] > 60 * 5:  # 5 minutes
                self.dropped_items.pop(i)
                break

        for index, block in enumerate(self.blocks):
            if not index > 8:
                if index == self.selected_block:
                    pygame.draw.rect(screen, (200, 200, 200), block, border_radius=4)
                else:
                    pygame.draw.rect(screen, self.block_color, block, border_radius=4)

                if block.collidepoint(pos[0], pos[1]) and (
                    self.holding_item or self.crafting_table.holding_item
                ):
                    pygame.draw.rect(screen, (150, 150, 150), block, border_radius=4)
            elif self.backpack_visible:
                if index == self.selected_block:
                    pygame.draw.rect(screen, (200, 200, 200), block, border_radius=4)
                else:
                    pygame.draw.rect(screen, self.block_color, block, border_radius=4)

                if block.collidepoint(pos[0], pos[1]) and (
                    self.holding_item or self.crafting_table.holding_item
                ):
                    pygame.draw.rect(screen, (150, 150, 150), block, border_radius=4)

            # if self.block_fill[index] == "tomato ":
            #     screen.blit(self.tomato_img, block)
            #
            # if self.block_fill[index] == "flower ":
            #     screen.blit(self.flower_img, block)
            #
            # if self.block_fill[index] == "sword ":
            #     screen.blit(self.sword_img, block)
            #
            # if self.block_fill[index] == "stone ":
            #     screen.blit(self.stone_img, block)
            #
            # if self.block_fill[index] == "pickaxe ":
            #     screen.blit(self.pickaxe_img, block)
            #
            # if self.block_fill[index] == "axe ":
            #     screen.blit(self.axe_img, block)
            #
            # if self.block_fill[index] == "log ":
            #     screen.blit(self.log_img, block)
            #
            # if self.block_fill[index] == "cookie ":
            #     screen.blit(self.cookie_img, block)
            #
            # if self.block_fill[index] == "meat ":
            #     screen.blit(self.meat_img, block)

            if not index > 8:
                if self.block_fill[index] != "":
                    screen.blit(self.pic_dict[self.block_fill[index]], block)
            elif self.backpack_visible:
                if self.block_fill[index] != "":
                    screen.blit(self.pic_dict[self.block_fill[index]], block)

            self.color = random.choice(self.colors)

    def update(
        self, keys, pos, screen, keyboard, joystick_input, joystick, scroll, plants
    ):
        holding_item = False
        clicked_item = ""

        keys = list(keys)

        if joystick_input:
            keys[2] = eval(joystick_btn_dict["west-btn"])
            keys[1] = eval(joystick_btn_dict["east-btn"])
            keys[0] = eval(joystick_btn_dict["south-btn"])

        if self.can_place_item and self.block_fill[self.selected_block] != "":
            mouse_tile = (
                int((scroll[0] + pos[0]) / 16),
                int((scroll[1] + pos[1]) / 16),
            )
            # plants[mouse_tile[1]][mouse_tile[0]] = 11

            # print(self.pic_dict_small["torch "])

            surf = pygame.Surface(
                self.pic_dict_small[self.block_fill[self.selected_block]].get_size(),
                pygame.SRCALPHA,
            )
            surf.blit(self.pic_dict_small[self.block_fill[self.selected_block]], (0, 0))
            surf.set_alpha(110)

            screen.blit(
                surf,
                (mouse_tile[0] * 16 - scroll[0], mouse_tile[1] * 16 - scroll[1]),
            )

            if keys[0]:
                plants = place_item(
                    plants,
                    self.item_code_dict[self.block_fill[self.selected_block]],
                    mouse_tile[0],
                    mouse_tile[1],
                )
                self.block_fill[self.selected_block] = ""

        if self.bar.collidepoint(pos[0], pos[1]) or self.bar_backback.collidepoint(pos):
            self.hovering_menu = True
        else:
            self.hovering_menu = False
            self.description = ""

        for key in self.block_fill:
            if bool(self.block_fill[key]):
                self.full_key_dict[key] = True
            else:
                self.full_key_dict[key] = False

        if all(value == True for value in self.full_key_dict.values()):
            self.can_fill = False
        else:
            self.can_fill = True

        for index, block in enumerate(self.blocks):
            current_block = pygame.Rect((-500, 0), (0, 0))

            if self.block_fill[self.selected_block] in self.placeable_items:
                self.can_place_item = True
            else:
                self.can_place_item = False

            self.player.holding_lantern = (
                True if self.block_fill[self.selected_block] == "lantern " else False
            )

            if self.block_fill[self.selected_block] == "tomato ":
                if keys[2] and not self.player.on_interact:
                    if (
                        keys[2]
                        and self.player.food_value < 10000 - self.player.tomato_feeding
                    ):
                        self.player.food_value += self.player.tomato_feeding
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.food_value < 10000:
                        self.player.food_value = 10000
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "cookie ":
                if keys[2] and not self.player.on_interact:
                    if (
                        keys[2]
                        and self.player.food_value < 10000 - self.player.cookie_feeding
                    ):
                        self.player.food_value += self.player.cookie_feeding
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.food_value < 10000:
                        self.player.food_value = 10000
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "meat ":
                if keys[2] and not self.player.on_interact:
                    if (
                        keys[2]
                        and self.player.food_value < 10000 - self.player.cookie_feeding
                    ):
                        self.player.food_value += self.player.cookie_feeding
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.food_value < 10000:
                        self.player.food_value = 10000
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "flower ":
                if keys[2] and not self.player.on_interact:
                    if (
                        keys[2]
                        and self.player.energy_value < 100 - self.player.flower_power
                    ):
                        self.player.energy_value += self.player.flower_power
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.energy_value < 100:
                        self.player.energy_value = 100
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "sword ":
                self.player.sword_selected = True
            else:
                self.player.sword_selected = False

            if self.block_fill[self.selected_block] == "pickaxe ":
                self.holding_pickaxe = True
            else:
                self.holding_pickaxe = False

            if self.block_fill[self.selected_block] == "axe ":
                self.holding_axe = True
            else:
                self.holding_axe = False

            if block.collidepoint(pos[0], pos[1]):
                if not index > 8 or self.backpack_visible:
                    current_block = block
                    current_index = index
                    if not index > 8:
                        if keys[0]:
                            self.selected_block = current_index
                    if self.block_fill[index] == "tomato ":
                        self.description = (
                            "Tomato's will make you less hungry  |  [RMB] to consume"
                        )
                    elif self.block_fill[index] == "flower ":
                        self.description = (
                            "Flowers refill your energy  |  [RMB] to consume"
                        )
                    elif self.block_fill[index] == "sword ":
                        self.description = "With the sword you can attack living things  |  [LMB] to attack"
                    elif self.block_fill[index] == "pickaxe ":
                        self.description = (
                            "With a pickaxe you can mine stone  |  [E] to mine"
                        )
                    elif self.block_fill[index] == "stone ":
                        self.description = "You can use stone to craft items  |  [TAB] to open crafting table"
                    elif self.block_fill[index] == "axe ":
                        self.description = (
                            "With an axe you can cut down trees  |  [E] to cut"
                        )
                    elif self.block_fill[index] == "log ":
                        self.description = "With logs you can craft items |  [TAB] to open crafting table"
                    elif self.block_fill[index] == "cookie ":
                        self.description = (
                            "Cookies are a great source of food  |  [RMB] to consume"
                        )
                    elif self.block_fill[index] == "meat ":
                        self.description = "Meat is a very nutritious type of food  |  [RMB] to consume"
                    elif self.block_fill[index] == "rat's tail ":
                        self.description = "With a rat's tail you're able to make different types of potions, not an edible product... | [TAB] to open crafting table"
                    elif self.block_fill[index] == "lantern ":
                        self.description = "With a lantern you can see in the dark."
                    elif self.block_fill[index] == "coal ":
                        self.description = "A handy ore."
                    elif self.block_fill[index] == "torch ":
                        self.description = "Primaly used to scare away zombies."
                    else:
                        self.description = ""
            else:
                self.description = ""

            if not index > 8 or self.backpack_visible:
                if self.holding_item:
                    screen.blit(self.pic_dict[self.clicked_item], (pos[0], pos[1]))

                if (
                    keys[1]
                    and block.collidepoint(pos[0], pos[1])
                    and bool(self.block_fill[index])
                    and not self.holding_item
                ):
                    clicked_block = index
                    clicked_item = self.block_fill[clicked_block]
                    self.clicked_item = clicked_item
                    self.block_fill[clicked_block] = ""
                    self.holding_item = True

                # if keys[0] and block.collidepoint(pos[0], pos[1]) and not bool(
                #         self.block_fill[index]) and self.holding_item:
                if (
                    keys[0]
                    and block.collidepoint(pos[0], pos[1])
                    and self.block_fill[index] in ["", " "]
                    and self.holding_item
                ):
                    self.block_fill[index] = self.clicked_item
                    self.holding_item = False
                # elif keys[0] and block.collidepoint(pos[0], pos[1]):
                #    print(f"/{self.block_fill[index]}/", self.holding_item)

                if (
                    keys[0]
                    and block.collidepoint(pos[0], pos[1])
                    and bool(self.block_fill[index])
                    and self.holding_item
                ):
                    item = self.block_fill[index]
                    self.block_fill[index] = self.clicked_item
                    self.clicked_item = item
                    self.holding_item = True
                    time.sleep(0.1)

                if (
                    keys[0]
                    and block.collidepoint(pos[0], pos[1])
                    and not bool(self.block_fill[index])
                    and self.crafting_table.holding_item
                ):
                    self.block_fill[index] = self.crafting_table.interacted_item
                    self.crafting_table.holding_item = False

                if (
                    self.holding_item
                    and keys[0]
                    and not self.hovering_menu
                    and not self.crafting_table.opened
                ):
                    if not self.clicked_item == "":
                        self.dropped_items[len(self.dropped_items)] = [
                            self.clicked_item,
                            self.player.x + random.choice([-60, 60, 55, -55]),
                            self.player.y + random.choice([-60, 60, 55, -55]),
                            time.perf_counter(),
                        ]
                        self.clicked_item = ""
                        self.holding_item = False

                if (
                    keyboard[pygame.K_q]
                    and not self.block_fill[self.selected_block] == ""
                ):
                    self.dropped_items[len(self.dropped_items)] = [
                        self.block_fill[self.selected_block],
                        self.player.x + random.choice([-60, 60, 55, -55]),
                        self.player.y + random.choice([-60, 60, 55, -55]),
                        time.perf_counter(),
                    ]
                    self.block_fill[self.selected_block] = ""

            if bool(self.description):
                text_w, text_h = self.font.size(self.description)
                text_render = self.font.render(self.description, True, "white")
                bg_rect = pygame.Rect(
                    (current_block.x + 50, current_block.y), (text_w + 15, text_h + 15)
                )
                shadow_rect = pygame.Rect(
                    (current_block.x + 52, current_block.y + 2),
                    (text_w + 15, text_h + 15),
                )
                pygame.draw.rect(
                    screen, pygame.Color("#30363b"), shadow_rect, border_radius=8
                )
                pygame.draw.rect(
                    screen, pygame.Color("#212529"), bg_rect, border_radius=8
                )
                screen.blit(
                    text_render, (current_block.x + 50 + 7, current_block.y + 7)
                )

    def draw_holding_items(self, screen, scroll):
        if not self.block_fill[self.selected_block] in [
            "sword ",
            "pickaxe ",
            "axe ",
            "",
        ]:
            if self.player.direction == "RIGHT" or self.player.direction_xy == "RIGHT":
                screen.blit(
                    self.pic_dict_small[self.block_fill[self.selected_block]],
                    (self.player.x - scroll[0] + 35, self.player.y - scroll[1] + 10),
                )
            else:
                screen.blit(
                    self.pic_dict_small[self.block_fill[self.selected_block]],
                    (self.player.x - scroll[0] - 5, self.player.y - scroll[1] + 10),
                )

    def mouse_update(self, mouse, joystick_input, joystick):
        if not joystick_input:  # no joystick connected
            if mouse > 0:
                if self.selected_block == 0:
                    self.selected_block = 8
                else:
                    self.selected_block -= 1
            elif mouse < 0:
                if self.selected_block == 8:
                    self.selected_block = 0
                else:
                    self.selected_block += 1
        else:  # joystick connected and used
            if eval(joystick_btn_dict["d-pad-up"]):  # DPAD Up
                if self.selected_block == 0:
                    self.selected_block = 8
                else:
                    self.selected_block -= 1
            elif eval(joystick_btn_dict["d-pad-down"]):  # DPAD Down
                if self.selected_block == 8:
                    self.selected_block = 0
                else:
                    self.selected_block += 1


##############################
#       Crafting table       #
##############################


class CraftingTable:
    def __init__(self):
        self.opened = False
        self.screen_width, self.screen_height = pygame.display.get_window_size()
        self.inventory = None
        self.hovering = False
        self.holding_item = False
        self.interacted_item = ""
        self.mouse_pos = None
        self.last_index = 0
        self.scroll = (0, 0)

        self.log_img = pygame.image.load("assets/floor/tile131.png").convert_alpha()
        self.log_img = pygame.transform.scale(self.log_img, (150, 150))

        self.stone_img = pygame.image.load("assets/floor/tile010.png").convert_alpha()
        self.stone_img = pygame.transform.scale(self.stone_img, (150, 150))

        self.tomato_img = pygame.image.load("assets/floor/tile127.png").convert_alpha()
        self.tomato_img = pygame.transform.scale(self.tomato_img, (150, 150))

        self.flower_img = pygame.image.load("assets/floor/tile011.png").convert_alpha()
        self.flower_img = pygame.transform.scale(self.flower_img, (150, 150))

        self.large_pic_dict = {}
        self.items_dict = {
            "tomato ": ["assets/floor/tile127.png", 30],
            "flower ": ["assets/floor/tile011.png", 30],
            "sword ": ["assets/tools/Sword-1.png", 37],
            "stone ": ["assets/floor/tile010.png", 30],
            "axe ": ["assets/tools/axe.png", 33],
            "log ": ["assets/floor/tile131.png", 33],
            "meat ": ["assets/food/26.png", 30],
            "tomato ": ["assets/floor/tile127.png", 30],
            "flower ": ["assets/floor/tile011.png", 30],
            "cookie ": ["assets/food/00.png", 30],
            "pickaxe ": ["assets/tools/pickaxe.png", 33],
            "coal ": ["assets/ores/coal.png", 30],
            "lantern ": ["assets/tools/lantern.png", 30],
            "torch ": ["assets/tools/torch.png", 30],
        }

        for item in self.items_dict:
            self.large_pic_dict[item] = pygame.image.load(
                f"{self.items_dict[item][0]}"
            ).convert_alpha()
            self.large_pic_dict[item] = pygame.transform.scale(
                self.large_pic_dict[item],
                (self.items_dict[item][1] * 5, self.items_dict[item][1] * 5),
            )

        self.bg_width = 500
        self.bg_height = 500
        self.bg_color = pygame.Color("#212529")
        self.background = pygame.Rect(
            (
                self.screen_width / 2 - self.bg_width / 2,
                self.screen_height / 2 - self.bg_height / 2,
            ),
            (self.bg_width, self.bg_height),
        )
        self.block_color = pygame.Color("#343a40")
        self.blocks = []
        self.block_fill = {
            0: "",
            1: "",
            2: "",
            3: "",
            4: "",
            5: "",
            6: "",
            7: "",
            8: "",
            9: "",
        }

        self.preview_block = pygame.Rect(
            (
                self.background.right + 30,
                self.background.centery - int(self.bg_height / 3 - 16) / 2,
            ),
            (int(self.bg_width / 3 - 16), int(self.bg_height / 3 - 16)),
        )

        padding = 10
        self.preview_background = pygame.Rect(
            (self.preview_block.x - padding, self.preview_block.y - padding),
            (
                self.preview_block.width + padding * 2,
                self.preview_block.height + padding * 2,
            ),
        )

        self.recipes = {  # left to bottom, left one right to bottom, right to bottom
            "s  slls  ": "pickaxe ",
            "   ssl   ": "sword ",
            "ssl      ": "sword ",
            "      ssl": "sword ",
            "ss sll   ": "axe ",
            "tff      ": "cookie ",
            "   tff   ": "cookie ",
            "      tff": "cookie ",
            "lllccllll": "lantern ",
            "cl       ": "torch ",
            " cl      ": "torch ",
            "   cl    ": "torch ",
            "    cl   ": "torch ",
            "      cl ": "torch ",
            "       cl": "torch ",
        }
        self.mask_surf = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA, 32
        )
        self.mask_surf.fill((0, 0, 0, 100))

        for x in range(3):
            for y in range(3):
                self.blocks.append(
                    pygame.Rect(
                        (
                            self.background.x + x * int(self.bg_width / 3) + 8,
                            8 + self.background.y + y * (int(self.bg_height) / 3),
                        ),
                        (int(self.bg_width / 3 - 16), int(self.bg_height / 3 - 16)),
                    )
                )

    def draw(
        self, screen, scrollx, scrolly, keyboard, joystick_input, joystick, plants
    ):
        if self.opened:
            screen.blit(self.mask_surf, (0, 0))
            pygame.draw.rect(screen, self.bg_color, self.background, border_radius=16)
            for index, block in enumerate(self.blocks):
                if not block.collidepoint(self.mouse_pos[0], self.mouse_pos[1]):
                    pygame.draw.rect(screen, self.block_color, block, border_radius=8)
                else:
                    pygame.draw.rect(screen, (200, 200, 200), block, border_radius=8)

                if self.block_fill[index] in self.large_pic_dict:
                    screen.blit(self.large_pic_dict[self.block_fill[index]], block)

            recipe = ""
            for index, block in enumerate(self.blocks):
                if bool(self.block_fill[index]):
                    recipe += self.block_fill[index][0]
                else:
                    recipe += " "
            pygame.draw.rect(
                screen, self.bg_color, self.preview_background, border_radius=16
            )
            if not self.preview_block.collidepoint(
                self.mouse_pos[0], self.mouse_pos[1]
            ):
                pygame.draw.rect(
                    screen, self.block_color, self.preview_block, border_radius=8
                )
            else:
                pygame.draw.rect(
                    screen, (200, 200, 200), self.preview_block, border_radius=8
                )

            if recipe in self.recipes:
                preview_item = self.recipes[recipe]
                screen.blit(self.large_pic_dict[preview_item], self.preview_block)

            self.inventory.draw(screen, pygame.mouse.get_pos(), scrollx, scrolly)
            self.inventory.update(
                pygame.mouse.get_pressed(),
                pygame.mouse.get_pos(),
                screen,
                keyboard,
                joystick_input,
                joystick,
                self.scroll,
                plants,
            )

            if self.holding_item:
                if self.interacted_item in self.inventory.pic_dict:
                    screen.blit(
                        self.inventory.pic_dict[self.interacted_item],
                        (self.mouse_pos[0], self.mouse_pos[1]),
                    )

    def set_inventory(self, inventory):
        self.inventory = inventory

    def reset(self):
        self.screen_width, self.screen_height = pygame.display.get_window_size()

        self.mask_surf = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA, 32
        )
        self.mask_surf.fill((0, 0, 0, 100))

        self.background = pygame.Rect(
            (
                self.screen_width / 2 - self.bg_width / 2,
                self.screen_height / 2 - self.bg_height / 2,
            ),
            (self.bg_width, self.bg_height),
        )

        self.preview_block = pygame.Rect(
            (
                self.background.right + 30,
                self.background.centery - int(self.bg_height / 3 - 16) / 2,
            ),
            (int(self.bg_width / 3 - 16), int(self.bg_height / 3 - 16)),
        )

        padding = 10
        self.preview_background = pygame.Rect(
            (self.preview_block.x - padding, self.preview_block.y - padding),
            (
                self.preview_block.width + padding * 2,
                self.preview_block.height + padding * 2,
            ),
        )

        self.blocks = []

        for x in range(3):
            for y in range(3):
                self.blocks.append(
                    pygame.Rect(
                        (
                            self.background.x + x * int(self.bg_width / 3) + 8,
                            8 + self.background.y + y * (int(self.bg_height) / 3),
                        ),
                        (int(self.bg_width / 3 - 16), int(self.bg_height / 3 - 16)),
                    )
                )

    def update(self, keys, mouse_pos, mouse_click, joystick_input, joystick, scroll):
        self.scroll = scroll
        self.mouse_pos = mouse_pos
        if not joystick_input:
            if keys[pygame.K_TAB]:
                if not self.opened:
                    self.opened = True
                    time.sleep(0.15)
                else:
                    self.opened = False
                    for key in self.block_fill:
                        if bool(self.block_fill[key]):
                            self.inventory.add_item(self.block_fill[key])
                            self.block_fill[key] = ""

                    if self.holding_item:
                        self.inventory.add_item(self.interacted_item)
                        self.holding_item = False
                    time.sleep(0.15)

        else:
            if eval(joystick_btn_dict["crafting_table"]):
                if not self.opened:
                    self.opened = True
                    time.sleep(0.15)
                else:
                    self.opened = False
                    for key in self.block_fill:
                        if bool(self.block_fill[key]):
                            self.inventory.add_item(self.block_fill[key])
                            self.block_fill[key] = ""

                    if self.holding_item:
                        self.inventory.add_item(self.interacted_item)
                        self.holding_item = False
                    time.sleep(0.15)

        if self.background.collidepoint(mouse_pos[0], mouse_pos[1]):  # TODO: croizent
            self.hovering = True
        else:
            self.hovering = False

        mouse_click = list(mouse_click)
        if joystick_input:
            mouse_click[0] = eval(joystick_btn_dict["south-btn"])
            mouse_click[1] = eval(joystick_btn_dict["east-btn"])
            mouse_click[2] = eval(joystick_btn_dict["west-btn"])
        for index, block in enumerate(self.blocks):
            if block.collidepoint(mouse_pos[0], mouse_pos[1]):
                if mouse_click[0] and self.inventory.holding_item:
                    if self.inventory.clicked_item[:2] in [
                        "st",
                        "lo",
                        "to",
                        "fl",
                        "co",
                    ]:
                        if bool(self.block_fill[index]):
                            item = self.block_fill[index]
                            self.block_fill[index] = self.inventory.clicked_item
                            self.inventory.clicked_item = ""
                            self.interacted_item = item
                            self.holding_item = True
                        else:
                            self.block_fill[index] = self.inventory.clicked_item
                        self.inventory.holding_item = False
                # pick up item from crafting table
                if (
                    mouse_click[1]
                    and not self.holding_item
                    and not self.inventory.holding_item
                ):
                    self.interacted_item = self.block_fill[index]
                    self.block_fill[index] = ""
                    self.holding_item = True

                # when placing item into crafting table
                if (
                    mouse_click[0]
                    and self.holding_item
                    and not bool(self.block_fill[index])
                ):
                    self.block_fill[index] = self.interacted_item
                    self.interacted_item = ""
                    self.holding_item = False

                # switching item in crafting table and inventory holding item
                # elif (
                #     mouse_click[0]
                #     and self.inventory.holding_item
                #     and bool(self.block_fill[index])
                #     and not self.holding_item
                # ):
                #     crafting_table_item = self.block_fill[index]
                #     holding_item = self.inventory.clicked_item
                #     self.block_fill[index] = holding_item
                #     self.interacted_item = crafting_table_item
                #     self.holding_item = True
                #     time.sleep(0.1)

                # switching item in crafting table with crafting table
                elif (
                    mouse_click[0]
                    and self.holding_item
                    and bool(self.block_fill[index])
                ):
                    item = self.block_fill[index]
                    self.block_fill[index] = self.interacted_item
                    self.interacted_item = item
                    self.holding_item = True
                    time.sleep(0.1)

        if (
            self.preview_block.collidepoint(self.mouse_pos[0], self.mouse_pos[1])
            and mouse_click[1]
        ):
            recipe = ""
            for index, block in enumerate(self.blocks):
                if bool(self.block_fill[index]):
                    recipe += self.block_fill[index][0]
                else:
                    recipe += " "

                if recipe in self.recipes:
                    self.inventory.clicked_item = f"{self.recipes[recipe]}"
                    self.inventory.holding_item = True
                    self.block_fill = {
                        0: "",
                        1: "",
                        2: "",
                        3: "",
                        4: "",
                        5: "",
                        6: "",
                        7: "",
                        8: "",
                        9: "",
                    }

        if keys[pygame.K_RETURN]:
            recipe = ""
            for index, block in enumerate(self.blocks):
                if bool(self.block_fill[index]):
                    recipe += self.block_fill[index][0]
                else:
                    recipe += " "

            if recipe in self.recipes:
                self.inventory.add_item(self.recipes[recipe])
                self.block_fill = {
                    0: "",
                    1: "",
                    2: "",
                    3: "",
                    4: "",
                    5: "",
                    6: "",
                    7: "",
                    8: "",
                    9: "",
                }

            time.sleep(0.1)
