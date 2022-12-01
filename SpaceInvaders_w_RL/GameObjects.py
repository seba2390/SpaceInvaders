from Util import *
import pygame
from copy import deepcopy


class Ufo:
    def __init__(self, height: int, width: int,
                 screen_width: int, screen_height: int, display_gameplay: bool):

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = self.width, self.height = width, height
        self.surf = None
        self.rect = None
        self.rects = []
        self.surfss = None
        self.direction_flag = None
        self.x_vel = 2
        self.display_gameplay = display_gameplay

        # For handling the update procedure of the monster explosion sprites
        self.anim_duration = 25  # Each sprite lasts 30 frames in main loop
        self.anim_index = 0
        self.anim_counter = 0

        if self.display_gameplay:
            # Loading in graphics for ufo
            self.surfs = [pygame.image.load("media/ufo/frame_0.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_1.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_2.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_3.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_5.png").convert_alpha()]
            self.surf = self.surfs[0]
            self.rect = self.surf.get_rect()
        else:
            self.rect = FakeRect(height=self.height, width=self.width)

    def spawn_ufo(self):
        """ For spawning in monsters in beginning of game """
        _direction_flag = np.random.binomial(n=1, p=0.5, size=1)
        if _direction_flag == 1:
            self.direction_flag = "right"
        elif _direction_flag == 0:
            self.direction_flag = "left"
        current_rect = deepcopy(self.rect)
        if self.direction_flag == "right":
            current_rect.centerx = self.width
        elif self.direction_flag == "left":
            current_rect.centerx = self.screen_width - self.width
        current_rect.centery = self.height + 10
        self.rects.append(current_rect)

    def generate_ufo(self):
        """ For generating ufo's randomly. (only 1 at a time on the screen) """
        if len(self.rects) == 0:
            spawn_probability = 0.001  # Number in [0;1]
            spawn_flag = np.random.binomial(n=1, p=spawn_probability, size=1)[0]  # Returns 1 w. prob. 'p'
            if spawn_flag == 1:
                self.spawn_ufo()

    def update_ufo_position(self):
        if len(self.rects) > 0:
            for i in range(len(self.rects)):
                if self.direction_flag == 'right':
                    self.rects[i] = self.rects[i].move(self.x_vel, 0)
                elif self.direction_flag == 'left':
                    self.rects[i] = self.rects[i].move(-self.x_vel, 0)

    def update_ufo_rects(self):
        """ Removing ufo that are out of screen"""
        if len(self.rects) > 0:
            self.rects = [r for r in self.rects if self.width < r.centerx < (self.screen_width - self.width)]


class MonsterShots:
    def __init__(self, height: int, width: int, display_gameplay):
        self.height = height
        self.width = width
        self.display_gameplay = display_gameplay

        self.y_velocity = 4
        self.shot_buffer = 5
        self.rect = None

        self.shots = []
        if self.display_gameplay:
            # Loading in graphics for shots fired by monsters
            self.surf = pygame.image.load("media/shots/shot2.png")
            self.rect = self.surf.get_rect()
        else:
            self.rect = FakeRect(height=self.height, width=self.width)

    def spawn_monster_shot(self, centerx, centery, monster_height):
        """ For spawning shots in, when fired from ship
            Needs centerx of monster that shoots, and monster rect height. """
        shot_rect = deepcopy(self.rect)
        shot_rect.centerx = centerx
        shot_rect.centery = centery + monster_height / 2 + self.shot_buffer
        self.shots.append(shot_rect)


class ShipShots:
    def __init__(self, height: int, width: int, display_gameplay):
        self.height = height
        self.width = width
        self.display_gameplay = display_gameplay

        self.y_velocity = 4
        self.shot_buffer = 5
        self.rect = None

        self.shots = []
        if self.display_gameplay:
            # Loading in graphics for shots fired by ship
            self.surf = pygame.image.load("media/shots/shot1.png")
            self.rect = self.surf.get_rect()
        else:
            self.rect = FakeRect(height=self.height, width=self.width)

    def spawn_ship_shot(self, centerx, centery, ship_height):
        """ For spawning shots in, when fired from ship"""
        self.rect.centerx = centerx
        self.rect.centery = centery - ship_height / 2 - self.height / 2 - self.shot_buffer
        self.shots.append(deepcopy(self.rect))


class SpaceShip:
    def __init__(self, height: int, width: int,
                 screen_width: int, screen_height: int, display_gameplay: bool) -> None:

        self.buffer = 20
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.height = height
        self.width = width
        self.rect = None
        self.x_velocity = 6

        self.anim_counter = 0
        self.anim_duration = 10
        self.anim_index = 0

        self.display_gameplay = display_gameplay

        self.shots = ShipShots(height=35, width=10, display_gameplay=self.display_gameplay)

        if self.display_gameplay:
            self.surfs = [pygame.image.load("media/spaceship/frame_0.png").convert_alpha(),
                          pygame.image.load("media/spaceship/frame_1.png").convert_alpha()]

            self.surf = self.surfs[0]
            self.rect = self.surf.get_rect()
        else:
            self.rect = FakeRect(height=self.height, width=self.width)

    def initialize(self):
        if self.display_gameplay:
            # Placing ship at the middle of the bottom (-20) of the screen
            self.rect.centerx = int(self.screen_width / 2)
            self.rect.centery = self.screen_height - self.width - self.buffer
        else:
            self.rect.left = np.random.uniform(0, 1) * (self.screen_width - self.width - 1.2 * self.x_velocity)
            self.rect.centery = self.screen_height - self.width - self.buffer
            assert self.rect.left >= 0
            assert self.rect.right <= self.screen_width - 1.2 * self.x_velocity

    def move(self, v_x, v_y):
        self.rect = self.rect.move(x=v_x, y=v_y)

    def update_ship_shot_rects(self):
        """ For removing shots fired from ship that are out of screen. """
        if len(self.shots.shots) > 0:
            self.shots.shots = [r for r in self.shots.shots if r.centery >= self.shots.height / 2]

    def update_ship_shots_position(self):
        """ For updating positions of shots fired from ship."""
        if len(self.shots.shots) > 0:
            for i in range(len(self.shots.shots)):
                self.shots.shots[i] = self.shots.shots[i].move(0, -self.shots.y_velocity)

    def update_ship_rect(self):
        """ For updating ship rect animation. """
        if self.anim_counter == self.anim_duration:
            self.anim_counter = 0
            if self.anim_index == len(self.surfs):
                self.anim_index = 0
            current_x, current_y = self.rect.centerx, self.rect.centery
            self.surf = self.surfs[self.anim_index]
            self.rect = self.surf.get_rect()
            self.rect.centerx = current_x
            self.rect.centery = current_y
            self.anim_index += 1


class Monsters:
    def __init__(self, height: int, width: int,
                 screen_width: int, screen_height: int, display_gameplay: bool) -> None:

        self.nr_rows, self.nr_cols = 3, 10
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.height = height
        self.width = width
        self.rect = None

        self.anim_duration = 30  # Each sprite lasts 30 frames in main loop
        self.anim_index = 0
        self.anim_counter = 0

        self.buffer = 20
        self.monster_buffer = 5
        self.edge_distance = 350

        self.x_velocity = 1
        self.right_edge_reached, self.left_edge_reached = False, False

        self.display_gameplay = display_gameplay

        self.monsters = []
        self.shots = MonsterShots(height=25, width=25, display_gameplay=self.display_gameplay)

        if self.display_gameplay:
            # Loading in graphics for monsters
            self.surfs = [pygame.image.load("media/enemy/frame_0.png").convert_alpha(),
                          pygame.image.load("media/enemy/frame_1.png").convert_alpha()]
            self.surf = self.surfs[0]
            self.rect = self.surf.get_rect()
        else:
            self.rect = FakeRect(height=self.height, width=self.width)

    def initialize(self):
        """ For spawning in monsters in beginning of game """
        for row in range(self.nr_rows):
            for col in range(self.nr_cols):
                current_rect = deepcopy(self.rect)
                x_distance = col * (self.width + self.monster_buffer)
                y_distance = row * (self.height + self.monster_buffer)
                current_rect.centerx = self.width / 2 + self.edge_distance + x_distance
                current_rect.centery = self.height / 2 + 100 + y_distance
                self.monsters.append(current_rect)

    def move_monsters_right(self):
        """ For moving monsters right """
        if self.right_edge_reached is False:
            for i in range(len(self.monsters)):
                assert self.monsters[i].right <= 0 + 1.2 * self.screen_width - 1.2 * self.x_velocity
                self.monsters[i] = self.monsters[i].move(self.x_velocity, 0)

    def move_monsters_left(self):
        """ For moving monsters left """
        if self.left_edge_reached is False:
            for i in range(len(self.monsters)):
                assert self.monsters[i].left >= 0 + 1.2 * self.x_velocity
                self.monsters[i] = self.monsters[i].move(-self.x_velocity, 0)

    def update_monster_positions_flag(self):
        """ For updating flags when monsters reaches left/right side of screen"""

        # Checking of monster has reached right edge
        if self.right_edge_reached is False:
            for i in range(len(self.monsters)):
                if self.monsters[i].centerx > self.screen_width - self.width / 2 - self.buffer:
                    self.right_edge_reached = True
                    self.left_edge_reached = False

        # Checking of monster has reached left edge
        if self.left_edge_reached is False:
            for i in range(len(self.monsters)):
                if self.monsters[i].centerx < self.width / 2 + self.buffer:
                    self.left_edge_reached = True
                    self.right_edge_reached = False

    def move(self):
        # Initially moving monsters right
        if not self.right_edge_reached and not self.left_edge_reached:
            self.move_monsters_right()
            self.update_monster_positions_flag()
        # Shuffling between left and right
        else:
            self.update_monster_positions_flag()
            if self.right_edge_reached:
                self.move_monsters_left()
            if self.left_edge_reached:
                self.move_monsters_right()

    def generate_monsters_shots(self, current_level):
        """ For generating shots from monsters randomly. """
        shot_probability = 0.0003 * current_level  # Number in [0;1]
        if len(self.monsters):
            for monster in range(len(self.monsters)):
                shooting_flag = np.random.binomial(n=1, p=shot_probability, size=1)[0]  # Returns 1 w. prob. 'p'
                if shooting_flag:
                    x, y = self.monsters[monster].centerx, self.monsters[monster].centery
                    self.shots.spawn_monster_shot(centerx=x, centery=y, monster_height=self.height)

    def update_monster_shot_rects(self):
        """ For removing shots fired from monsters that are out of screen. """
        if len(self.shots.shots) > 0:
            self.shots.shots = [r for r in self.shots.shots if r.centery <= self.screen_height - self.shots.height / 2]

    def update_monster_shots_position(self):
        """ For updating positions of shots fired from monsters. """
        if len(self.shots.shots) > 0:
            for i in range(len(self.shots.shots)):
                self.shots.shots[i] = self.shots.shots[i].move(0, self.shots.y_velocity)

    def update_monster_rects(self):
        """ For updating monster animation. """
        if self.anim_counter == self.anim_duration:
            self.anim_counter = 0
            if self.anim_index == len(self.surfs):
                self.anim_index = 0
            for monster in range(len(self.monsters)):
                current_x, current_y = self.monsters[monster].centerx, self.monsters[monster].centery
                self.surf = self.surfs[self.anim_index]
                if self.display_gameplay:
                    self.monsters[monster] = self.surf.get_rect()
                else:
                    self.monsters[monster] = FakeRect(height=self.height, width=self.width)
                self.monsters[monster].centerx = current_x
                self.monsters[monster].centery = current_y
            self.anim_index += 1


class PygameGraphics:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_size = self.screen_width, self.screen_height

        self.ship_anim_duration = 10
        self.ship_anim_index = 0
        self.ship_anim_counter = 0

        self.ufo_anim_counter = 0
        self.ufo_anim_duration = 25
        self.ufo_anim_index = 0

        self.monster_anim_duration = 30
        self.monster_anim_index = 0
        self.monster_anim_counter = 0

        self._display_surf = None
        self._background_surf = None
        self._game_over_background_surf = None

        pygame.init()
        pygame.font.init()

        self._display_surf = pygame.display.set_mode(size=self.screen_size,
                                                     flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._background_surf = pygame.image.load("media/background.png").convert()

        self._game_over_display_surf = pygame.display.set_mode(size=self.screen_size,
                                                               flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._game_over_background_surf = pygame.image.load("media/background.png").convert()

        self._loading_display_surf = pygame.display.set_mode(size=self.screen_size,
                                                             flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._loading_background_surf = pygame.image.load("media/background.png").convert()
        self.text_color = (255, 255, 255)  # White
        self.score_board_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 20)
        self.score_text_surface = self.score_board_font.render("score:", True, self.text_color, None)
        self.life_text_surface = self.score_board_font.render("life:", True, self.text_color, None)
        self.level_text_surface = self.score_board_font.render("level:", True, self.text_color, None)
        self.life_text_rect = None
        self.score_text_rect = None
        self.level_text_rect = None

        self._game_over_display_surf = None
        self.game_over_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 40)
        self.game_over_text_surface = self.game_over_font.render("Game Over", True, self.text_color, None)
        self.game_over_text_rect = self.game_over_text_surface.get_rect()
        self.game_over_text_rect.centerx = int(self.screen_width / 2) + 3
        self.game_over_text_rect.centery = int(self.screen_height / 2)
        self.game_over_anim_duration = 25
        self.game_over_anim_counter = 0
        self.game_over_position = "down"

        # light shade of the button
        self.restart_button_color_light = (170, 170, 170)
        # dark shade of the button
        self.restart_button_color_dark = (100, 100, 100)
        self.restart_button_width = 240
        self.restart_button_height = 60
        self.restart_button_dims = [self.screen_width / 2 - self.restart_button_width / 2,
                                    self.screen_height / 2 + int(1.3 * self.restart_button_height),
                                    self.restart_button_width,
                                    self.restart_button_height]

        self.restart_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 30)
        self.restart_text_surface = self.restart_font.render("restart", True, self.text_color, None)
        self.restart_text_rect = self.restart_text_surface.get_rect()
        self.restart_text_rect.centerx = int(self.screen_width / 2) + 3
        self.restart_text_rect.centery = int(self.screen_height / 2) + int(1.85 * self.restart_button_height)

        self._loading_display_surf = None
        self._loading_background_surf = None
        self.loading_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 40)
        self.loading_text_surfaces = [
            self.loading_font.render("Loading next level .  ", True, self.text_color, None),
            self.loading_font.render("Loading next level .. ", True, self.text_color, None),
            self.loading_font.render("Loading next level ...", True, self.text_color, None),
            self.loading_font.render("Loading next level    ", True, self.text_color, None)]
        self.loading_text_rect = self.loading_text_surfaces[0].get_rect()
        self.loading_text_rect.centerx = int(self.screen_width / 2) + 3
        self.loading_text_rect.centery = int(self.screen_height / 2)
        self.loading_text_anim_duration = 30
        self.loading_text_anim_counter = 0
        self.loading_text_frame_counter = 0
        self.loading_anim_completions = 0

        self.life_width = 35
        self.life_surfs = None
        self.life_surf = None
        self._life_rect = None
        self._life_rects = []  # For 3 lives
        self._life_surf = None
        # For handling the update procedure of the life sprites
        self.life_anim_duration = 10  # Each sprite lasts 10 frames in main loop
        self.life_anim_index = 0
        self.life_anim_counter = 0

        self.score_text_value_surface = None
        self.score_text_value_rect = None
        self.level_text_value_surface = None
        self.level_text_value_rect = None

        # Text graphics
        self.score_text_rect = self.score_text_surface.get_rect()
        self.score_text_rect.centerx = 50
        self.score_text_rect.centery = 25

        self.level_text_rect = self.score_text_surface.get_rect()
        self.level_text_rect.centerx = int(self.screen_width / 2) - 20
        self.level_text_rect.centery = 25

        self.life_text_rect = self.life_text_surface.get_rect()
        self.life_text_rect.centerx = 1200
        self.life_text_rect.centery = 25

        # Loading in graphics for life indicators
        self.life_surfs = [pygame.image.load("media/life/frame_0.png").convert_alpha(),
                           pygame.image.load("media/life/frame_1.png").convert_alpha(),
                           pygame.image.load("media/life/frame_2.png").convert_alpha(),
                           pygame.image.load("media/life/frame_3.png").convert_alpha(),
                           pygame.image.load("media/life/frame_4.png").convert_alpha(),
                           pygame.image.load("media/life/frame_5.png").convert_alpha(),
                           pygame.image.load("media/life/frame_6.png").convert_alpha(),
                           pygame.image.load("media/life/frame_7.png").convert_alpha()]
        self._life_surf = self.life_surfs[0]
        self._life_rect = self._life_surf.get_rect()

        self.monster_explosion_size = self.monster_explosion_width, self.monster_explosion_height = 45, 45
        self.monster_explosion_surf = None
        self.monster_explosion_rect = None
        self.monster_explosion_rects = []
        self.monster_explosion_surfs = None
        self.monster_explosion_anim_surfs = []

        self.monster_explosion_frame_counters = []
        # For handling the update procedure of the monster explosion sprites
        self.monster_explosion_anim_duration = 4  # Each sprite lasts 5 frames in main loop
        self.monster_explosion_anim_index = 0
        self.monster_explosion_anim_counter = 0
        self.monster_explosion_anim_counters = []

        self._display_surf = pygame.display.set_mode(size=self.screen_size,
                                                     flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._background_surf = pygame.image.load("media/background.png").convert()

        self._game_over_display_surf = pygame.display.set_mode(size=self.screen_size,
                                                               flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._game_over_background_surf = pygame.image.load("media/background.png").convert()

        self._loading_display_surf = pygame.display.set_mode(size=self.screen_size,
                                                             flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._loading_background_surf = pygame.image.load("media/background.png").convert()

        # Loading in graphics for monster explosion
        self.monster_explosion_surfs = [pygame.image.load("media/monster_explosion/frame_0.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_1.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_2.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_3.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_4.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_5.png").convert_alpha()]
        self.monster_explosion_surf = self.monster_explosion_surfs[0]
        self.monster_explosion_rect = self.monster_explosion_surf.get_rect()

    def spawn_lives(self, nr_lives):
        """ For spawning in lives in beginning of game """
        for life in range(nr_lives):
            current_rect = deepcopy(self._life_rect)
            current_rect.centerx, current_rect.centery = 1252 + life * self.life_width, 22
            self._life_rects.append(current_rect)

    def spawn_monster_explosion(self, monsters: Monsters, monster_index):
        """ For spawning an explosion at monster when hit."""
        explosion_rect = deepcopy(self.monster_explosion_rect)
        explosion_rect.centerx = monsters.monsters[monster_index].centerx
        explosion_rect.centery = monsters.monsters[monster_index].centery
        self.monster_explosion_rects.append(explosion_rect)
        index = 0
        self.monster_explosion_anim_counters.append(index)
        self.monster_explosion_frame_counters.append(index)
        self.monster_explosion_anim_surfs.append(self.monster_explosion_surfs[index])

    def update_score(self, current_score: int):
        """ For updating score. Updates text score if gameplay is being displayed"""
        self.score_text_value_surface = self.score_board_font.render(" " + str(current_score), True,
                                                                     self.text_color, None)
        self.score_text_value_rect = self.score_text_value_surface.get_rect()
        self.score_text_value_rect.centerx = 120
        self.score_text_value_rect.centery = 25

    def update_level(self, current_level: int):
        """ For updating level value text. """
        self.level_text_value_surface = self.score_board_font.render(" " + str(current_level), True,
                                                                     self.text_color, None)
        self.level_text_value_rect = self.level_text_value_surface.get_rect()
        self.level_text_value_rect.centerx = int(self.screen_width / 2) + 40
        self.level_text_value_rect.centery = 25

    def update_life_rects(self):
        """ For updating life animation. """
        if self.life_anim_counter == self.life_anim_duration:
            self.life_anim_counter = 0
            if self.life_anim_index == len(self.life_surfs):
                self.life_anim_index = 0
            for life in range(len(self._life_rects)):
                current_x, current_y = self._life_rects[life].centerx, self._life_rects[life].centery
                self._life_surf = self.life_surfs[self.life_anim_index]
                self._life_rects[life] = self._life_surf.get_rect()
                self._life_rects[life].centerx = current_x
                self._life_rects[life].centery = current_y
            self.life_anim_index += 1

    def update_monster_explosion_rects(self):
        """ For updating monster explosion animation. """

        # Initially checking if any of the explosion surfs equals last frame surf and updating
        remove_indices = []
        for surf in range(len(self.monster_explosion_anim_surfs)):
            if self.monster_explosion_frame_counters[surf] == len(self.monster_explosion_surfs) - 1:  # Last frame
                remove_indices.append(surf)

        updated_explosion_rects, updated_anim_counters = [], []
        updated_surfs, updated_frame_counts = [], []
        for index in range(len(self.monster_explosion_rects)):
            if index not in remove_indices:
                assert self.monster_explosion_frame_counters[index] < len(self.monster_explosion_surfs) - 1
                updated_explosion_rects.append(self.monster_explosion_rects[index])
                updated_anim_counters.append(self.monster_explosion_anim_counters[index])
                updated_surfs.append(self.monster_explosion_anim_surfs[index])
                updated_frame_counts.append(self.monster_explosion_frame_counters[index])
            else:
                assert self.monster_explosion_frame_counters[index] == len(self.monster_explosion_surfs) - 1

        if len(remove_indices) > 0:
            self.monster_explosion_rects = updated_explosion_rects
            self.monster_explosion_anim_counters = updated_anim_counters
            self.monster_explosion_anim_surfs = updated_surfs
            self.monster_explosion_frame_counters = updated_frame_counts

    def update_game_over_rect(self):
        """ Animating game over text """
        if self.game_over_anim_counter == self.game_over_anim_duration:
            self.game_over_anim_counter = 0
            if self.game_over_position == 'down':
                self.game_over_text_rect.centery += 5
                self.game_over_position = 'up'
            else:
                self.game_over_text_rect.centery -= 5
                self.game_over_position = 'down'

    def update_loading_rect(self):
        """ Animating game over text """
        if self.loading_text_frame_counter == len(self.loading_text_surfaces) - 1:
            self.loading_text_frame_counter = 0
            self.loading_anim_completions += 1

        if self.loading_text_anim_counter == self.loading_text_anim_duration:
            self.loading_text_anim_counter = 0
            self.loading_text_frame_counter += 1
            current_x, current_y = self.loading_text_rect.centerx, self.loading_text_rect.centery
            self.loading_text_rect = self.loading_text_surfaces[self.loading_text_frame_counter].get_rect()
            self.loading_text_rect.centerx = current_x
            self.loading_text_rect.centery = current_y

    def game_over_render(self):
        # Rendering background
        self._game_over_display_surf.blit(self._game_over_background_surf, (0, 0))
        self._game_over_display_surf.blit(self.game_over_text_surface, self.game_over_text_rect)
        self._game_over_display_surf.blit(self.restart_text_surface, self.restart_text_rect)
        pygame.display.flip()

    def loading_render(self):
        # Rendering background
        self._loading_display_surf.blit(self._loading_background_surf, (0, 0))
        self._loading_display_surf.blit(self.loading_text_surfaces[self.loading_text_frame_counter],
                                        self.loading_text_rect)
        pygame.display.flip()

    def update_ufo_anim_rects(self, _ufo: Ufo):
        """ For updating monster animation. """
        if self.ufo_anim_counter == self.ufo_anim_duration:
            self.ufo_anim_counter = 0
            if self.ufo_anim_index == len(_ufo.surfs):
                self.ufo_anim_index = 0
            for ufo in range(len(_ufo.rects)):
                current_x, current_y = _ufo.rects[ufo].centerx, _ufo.rects[ufo].centery
                _ufo.surf = _ufo.surfs[self.ufo_anim_index]
                _ufo.rects[ufo] = _ufo.surf.get_rect()
                _ufo.rects[ufo].centerx = current_x
                _ufo.rects[ufo].centery = current_y
            self.ufo_anim_index += 1

        update_indices = []
        for anim_counter_idx in range(len(self.monster_explosion_anim_counters)):
            if self.monster_explosion_anim_counters[anim_counter_idx] == self.monster_explosion_anim_duration:
                update_indices.append(anim_counter_idx)
                self.monster_explosion_anim_counters[anim_counter_idx] = 0
                self.monster_explosion_frame_counters[anim_counter_idx] += 1
            else:
                self.monster_explosion_anim_counters[anim_counter_idx] += 1
        for index in update_indices:
            self.monster_explosion_anim_surfs[index] = self.monster_explosion_surfs[
                self.monster_explosion_frame_counters[index]]