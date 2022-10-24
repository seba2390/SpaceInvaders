import pygame
from pygame.locals import *
import numpy as np
from copy import deepcopy


# TODO: Make explosion anim start at same frame every time (FIXED)
# TODO: Add more levels
# TODO: Add game menu
# TODO: Add different enemies

class SpaceInvadersApp:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self._background_surf = None
        self._game_over_background_surf = None
        self.screen_size = self.screen_width, self.screen_height = 1353, 709

        self.x_velocity = 6
        self._ship_surf = None
        self._ship_react = None
        self.ship_size = self.ship_width, self.ship_height = 80, 80
        self.ship_surfs = None
        self.ship_reacts = None
        # For handling the update procedure of the spaceship sprites
        self.ship_anim_duration = 10  # Each sprite lasts 10 frames in main loop
        self.ship_anim_index = 0
        self.ship_anim_counter = 0

        self._ship_shot_surf = None
        self._ship_shot_react = None
        self._ship_shot_reacts = []
        self.ship_shot_size = self.ship_shot_width, self.ship_shot_height = 10, 35
        self.shot_y_velocity = 4

        self._nr_monsters = (3, 10)
        self._monster_surf = None
        self._monster_react = None
        self._monster_reacts = []
        self._monster_surfs = None
        self.monster_size = self.monster_width, self.monster_height = 45, 45
        self.monster_edge_distance = 350
        self.monster_right_edge_reached, self.monster_left_edge_reached = False, False
        self.monster_x_vel = 1

        self.monster_shot_size = self.monster_shot_width, self.monster_shot_height = 25, 25
        self.monster_shot_surf = None
        self.monster_shot_react = None
        self.monster_shot_reacts = []

        self.monster_explosion_size = self.monster_explosion_width, self.monster_explosion_height = 45, 45
        self.monster_explosion_surf = None
        self.monster_explosion_react = None
        self.monster_explosion_reacts = []
        self.monster_explosion_surfs = None
        self.monster_explosion_anim_surfs = []

        self.monster_explosion_frame_counters = []
        # For handling the update procedure of the monster explosion sprites
        self.monster_explosion_anim_duration = 4  # Each sprite lasts 5 frames in main loop
        self.monster_explosion_anim_index = 0
        self.monster_explosion_anim_counter = 0
        self.monster_explosion_anim_counters = []
        # For handling the update procedure of the monster sprites
        self.monster_anim_duration = 30  # Each sprite lasts 30 frames in main loop
        self.monster_anim_index = 0
        self.monster_anim_counter = 0

        self.ufo_size = self.ufo_width, self.ufo_height = 55, 55
        self.ufo_surf = None
        self.ufo_react = None
        self.ufo_reacts = []
        self.ufo_surfs = None
        self.ufo_direction_flag = None
        self.ufo_x_vel = 2
        # For handling the update procedure of the monster explosion sprites
        self.ufo_anim_duration = 25  # Each sprite lasts 30 frames in main loop
        self.ufo_anim_index = 0
        self.ufo_anim_counter = 0

        self.buffer = 20
        self.shot_buffer = 5
        self.monster_buffer = 5

        pygame.font.init()
        self.text_color = (255, 255, 255)  # White
        self.score_board_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 20)
        self.score_text_surface = self.score_board_font.render("score:", True, self.text_color, None)
        self.life_text_surface = self.score_board_font.render("life:", True, self.text_color, None)
        self.level_text_surface = self.score_board_font.render("level:", True, self.text_color, None)
        self.life_text_react = None
        self.score_text_react = None
        self.level_text_react = None

        self._game_over_display_surf = None
        self.game_over_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 40)
        self.game_over_text_surface = self.game_over_font.render("Game Over", True, self.text_color, None)
        self.game_over_text_react = self.game_over_text_surface.get_rect()
        self.game_over_text_react.centerx = int(self.screen_width/2) + 3
        self.game_over_text_react.centery = int(self.screen_height/2)
        self.game_over_anim_duration = 25
        self.game_over_anim_counter = 0
        self.game_over_position = "down"

        # light shade of the button
        self.restart_button_color_light = (170, 170, 170)
        # dark shade of the button
        self.restart_button_color_dark = (100, 100, 100)
        self.restart_button_width = 240
        self.restart_button_height = 60
        self.restart_button_dims = [self.screen_width / 2 - self.restart_button_width/2,
                                    self.screen_height / 2 + int(1.3*self.restart_button_height),
                                    self.restart_button_width,
                                    self.restart_button_height]

        self.restart_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 30)
        self.restart_text_surface = self.restart_font.render("restart", True, self.text_color, None)
        self.restart_text_react = self.restart_text_surface.get_rect()
        self.restart_text_react.centerx = int(self.screen_width/2) + 3
        self.restart_text_react.centery = int(self.screen_height/2) + int(1.85*self.restart_button_height)

        self._loading_display_surf = None
        self._loading_background_surf = None
        self.loading_font = pygame.font.Font("media/Space-Invaders-Font/space_invaders.ttf", 40)
        self.loading_text_surfaces = [
                                      self.loading_font.render("Loading next level .  ", True, self.text_color, None),
                                      self.loading_font.render("Loading next level .. ", True, self.text_color, None),
                                      self.loading_font.render("Loading next level ...", True, self.text_color, None),
                                      self.loading_font.render("Loading next level    ", True, self.text_color, None)]
        self.loading_text_react = self.loading_text_surfaces[0].get_rect()
        self.loading_text_react.centerx = int(self.screen_width/2) + 3
        self.loading_text_react.centery = int(self.screen_height/2)
        self.loading_text_anim_duration = 30
        self.loading_text_anim_counter = 0
        self.loading_text_frame_counter = 0
        self.loading_anim_completions = 0

        self.nr_lives = 3
        self.life_width = 35
        self.life_surfs = None
        self.life_surf = None
        self._life_react = None
        self._life_reacts = []  # For 3 lives
        self._life_surf = None
        # For handling the update procedure of the life sprites
        self.life_anim_duration = 10  # Each sprite lasts 10 frames in main loop
        self.life_anim_index = 0
        self.life_anim_counter = 0

        self.score_text_value_surface = None
        self.score_text_value_react = None
        self.level_text_value_surface = None
        self.level_text_value_react = None

        self.current_level = 1
        self.current_score = 0
        self.current_lifes = 3

        self.in_game = True

    def on_init(self):
        # Initializing pygame and loading in graphics for background
        pygame.init()
        self._running = True
        self._display_surf = pygame.display.set_mode(size=self.screen_size,
                                                     flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._background_surf = pygame.image.load("media/background.png").convert()

        self._game_over_display_surf = pygame.display.set_mode(size=self.screen_size,
                                                               flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._game_over_background_surf = pygame.image.load("media/background.png").convert()

        self._loading_display_surf = pygame.display.set_mode(size=self.screen_size,
                                                               flags=(pygame.HWSURFACE or pygame.DOUBLEBUF))
        self._loading_background_surf = pygame.image.load("media/background.png").convert()

        # Loading in graphics for ship
        self.ship_surfs = [pygame.image.load("media/spaceship/frame_0.png").convert_alpha(),
                           pygame.image.load("media/spaceship/frame_1.png").convert_alpha()]

        self._ship_surf = self.ship_surfs[0]
        self._ship_react = self._ship_surf.get_rect()

        # Placing ship at the middle of the bottom (-20) of the screen
        self._ship_react.centerx = int(self.screen_width / 2)
        self._ship_react.centery = self.screen_height - self.ship_width - self.buffer

        # Loading in graphics for shots fired by ship
        self._ship_shot_surf = pygame.image.load("media/shots/shot1.png")
        self._ship_shot_react = self._ship_shot_surf.get_rect()

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
        self._life_react = self._life_surf.get_rect()

        # Loading in graphics for ufo
        self.ufo_surfs = [pygame.image.load("media/ufo/frame_0.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_1.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_2.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_3.png").convert_alpha(),
                          pygame.image.load("media/ufo/frame_5.png").convert_alpha()]
        self.ufo_surf = self.ufo_surfs[0]
        self.ufo_react = self.ufo_surf.get_rect()

        # Loading in graphics for monsters
        self._monster_surfs = [pygame.image.load("media/enemy/frame_0.png").convert_alpha(),
                               pygame.image.load("media/enemy/frame_1.png").convert_alpha()]
        self._monster_surf = self._monster_surfs[0]
        self._monster_react = self._monster_surf.get_rect()

        # Loading in graphics for monster explosion
        self.monster_explosion_surfs = [pygame.image.load("media/monster_explosion/frame_0.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_1.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_2.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_3.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_4.png").convert_alpha(),
                                        pygame.image.load("media/monster_explosion/frame_5.png").convert_alpha()]
        self.monster_explosion_surf = self.monster_explosion_surfs[0]
        self.monster_explosion_react = self.monster_explosion_surf.get_rect()

        # Loading in graphics for shots fired by monsters
        self.monster_shot_surf = pygame.image.load("media/shots/shot2.png")
        self.monster_shot_react = self.monster_shot_surf.get_rect()

        # Text graphics
        self.score_text_react = self.score_text_surface.get_rect()
        self.score_text_react.centerx = 50
        self.score_text_react.centery = 25

        self.level_text_react = self.score_text_surface.get_rect()
        self.level_text_react.centerx = int(self.screen_width/2) - 20
        self.level_text_react.centery = 25

        self.life_text_react = self.life_text_surface.get_rect()
        self.life_text_react.centerx = 1200
        self.life_text_react.centery = 25

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.spawn_ship_shot()

    def update_ship_position(self):
        """ For updating position (left and right) of ship when pressing L/R or A/D"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self._ship_react.x > 0 + self.buffer:
                self._ship_react = self._ship_react.move(-self.x_velocity, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self._ship_react.x < self.screen_width - self.ship_width - self.buffer:
                self._ship_react = self._ship_react.move(self.x_velocity, 0)

    def spawn_ship_shot(self):
        """ For spawning shots in, when fired from ship"""
        self._ship_shot_react.centerx = self._ship_react.centerx
        self._ship_shot_react.centery = self._ship_react.centery - self.ship_height / 2 - self.ship_shot_height / 2 - self.shot_buffer
        self._ship_shot_reacts.append(self._ship_shot_react)

    def spawn_monsters(self):
        """ For spawning in monsters in beginning of game """
        for row in range(self._nr_monsters[0]):
            for col in range(self._nr_monsters[1]):
                current_rect = deepcopy(self._monster_react)
                x_distance = col * (self.monster_width + self.monster_buffer)
                y_distance = row * (self.monster_height + self.monster_buffer)
                current_rect.centerx = self.monster_width / 2 + self.monster_edge_distance + x_distance
                current_rect.centery = self.monster_height / 2 + 100 + y_distance
                self._monster_reacts.append(current_rect)

    def spawn_ufo(self):
        """ For spawning in monsters in beginning of game """
        direction_flag = np.random.binomial(n=1, p=0.5, size=1)
        if direction_flag == 1:
            self.ufo_direction_flag = "right"
        elif direction_flag == 0:
            self.ufo_direction_flag = "left"
        current_rect = deepcopy(self.ufo_react)
        if self.ufo_direction_flag == "right":
            current_rect.centerx = self.ufo_width
        elif self.ufo_direction_flag == "left":
            current_rect.centerx = self.screen_width - self.ufo_width
        current_rect.centery = self.ufo_height + 10
        self.ufo_reacts.append(current_rect)

    def spawn_lives(self):
        """ For spawning in lives in beginning of game """
        for life in range(self.nr_lives):
            current_rect = deepcopy(self._life_react)
            current_rect.centerx, current_rect.centery = 1252 + life * self.life_width, 22
            self._life_reacts.append(current_rect)

    def spawn_monster_shot(self, monster_index):
        """ For spawning shots in, when fired from ship"""
        shot_react = deepcopy(self.monster_shot_react)
        shot_react.centerx = self._monster_reacts[monster_index].centerx
        shot_react.centery = self._monster_reacts[monster_index].centery + self.monster_height / 2 + self.shot_buffer
        self.monster_shot_reacts.append(shot_react)

    def spawn_monster_explosion(self, monster_index):
        """ For spawning an explosion at monster when hit."""
        explosion_react = deepcopy(self.monster_explosion_react)
        explosion_react.centerx = self._monster_reacts[monster_index].centerx
        explosion_react.centery = self._monster_reacts[monster_index].centery
        self.monster_explosion_reacts.append(explosion_react)
        index = 0
        self.monster_explosion_anim_counters.append(index)
        self.monster_explosion_frame_counters.append(index)
        self.monster_explosion_anim_surfs.append(self.monster_explosion_surfs[index])

    def move_monsters_right(self):
        """ For moving monsters right """
        if self.monster_right_edge_reached is False:
            for i in range(len(self._monster_reacts)):
                self._monster_reacts[i] = self._monster_reacts[i].move(self.monster_x_vel, 0)

    def move_monsters_left(self):
        """ For moving monsters left """
        if self.monster_left_edge_reached is False:
            for i in range(len(self._monster_reacts)):
                self._monster_reacts[i] = self._monster_reacts[i].move(-self.monster_x_vel, 0)

    def update_monster_positions_flag(self):
        """ For updating flags when monsters reaches left/right side of screen"""

        # Checking of monster has reached right edge
        if self.monster_right_edge_reached is False:
            for i in range(len(self._monster_reacts)):
                if self._monster_reacts[i].centerx > self.screen_width - self.monster_width / 2 - self.buffer:
                    self.monster_right_edge_reached = True
                    self.monster_left_edge_reached = False

        # Checking of monster has reached left edge
        if self.monster_left_edge_reached is False:
            for i in range(len(self._monster_reacts)):
                if self._monster_reacts[i].centerx < self.monster_width / 2 + self.buffer:
                    self.monster_left_edge_reached = True
                    self.monster_right_edge_reached = False

    def shot_2_monster_collision_detect(self):
        """ For detecting collisions between shots fired from ships, and monsters
            which also updates list of monster rects and list of shot rects,
            when collision detected. (N.B. Also updates current score.)"""
        remove_shot_indices = []
        remove_monster_indices = []
        for monster in range(len(self._monster_reacts)):
            for ship_shot in range(len(self._ship_shot_reacts)):
                if pygame.Rect.colliderect(self._monster_reacts[monster], self._ship_shot_reacts[ship_shot]):
                    remove_shot_indices.append(ship_shot)
                    remove_monster_indices.append(monster)

        # Updating score
        for kill in range(len(remove_monster_indices)):
            self.current_score += 10

        # Spawning explosion at monster
        for kill in range(len(remove_monster_indices)):
            self.spawn_monster_explosion(remove_monster_indices[kill])

        updated_monster_rects = []
        for index in range(len(self._monster_reacts)):
            if index not in remove_monster_indices:
                updated_monster_rects.append(self._monster_reacts[index])
        updated_ship_shot_rects = []
        for index in range(len(self._ship_shot_reacts)):
            if index not in remove_shot_indices:
                updated_ship_shot_rects.append(self._ship_shot_reacts[index])

        self._monster_reacts = updated_monster_rects
        self._ship_shot_reacts = updated_ship_shot_rects

    def shot_2_ufo_collision_detect(self):
        """ For detecting collisions between shots fired from ships, and monsters
            which also updates list of monster rects and list of shot rects,
            when collision detected. (N.B. Also updates current score.)"""
        remove_shot_indices = []
        remove_ufo_indices = []
        for ufo in range(len(self.ufo_reacts)):
            for ship_shot in range(len(self._ship_shot_reacts)):
                if pygame.Rect.colliderect(self.ufo_reacts[ufo], self._ship_shot_reacts[ship_shot]):
                    remove_shot_indices.append(ship_shot)
                    remove_ufo_indices.append(ufo)

        # Updating score
        for kill in range(len(remove_ufo_indices)):
            self.current_score += 50

        updated_ufo_rects = []
        for index in range(len(self.ufo_reacts)):
            if index not in remove_ufo_indices:
                updated_ufo_rects.append(self.ufo_reacts[index])
        updated_ship_shot_rects = []
        for index in range(len(self._ship_shot_reacts)):
            if index not in remove_shot_indices:
                updated_ship_shot_rects.append(self._ship_shot_reacts[index])

        self.ufo_reacts = updated_ufo_rects
        self._ship_shot_reacts = updated_ship_shot_rects

    def shot_2_ship_collision_detect(self):
        """ For detecting collisions between shots fired from enemies, and ship
            which also updates list of shot rects and list of life rects
            when collision detected. (N.B. Also updates current life score.)"""
        remove_shot_indices = []
        for monster_shot in range(len(self.monster_shot_reacts)):
            if pygame.Rect.colliderect(self._ship_react, self.monster_shot_reacts[monster_shot]):
                remove_shot_indices.append(monster_shot)
                # Remove last life in life reacts
                self._life_reacts = self._life_reacts[:len(self._life_reacts) - 1]
                # Update score
                self.current_lifes -= 1

        updated_monster_shot_rects = []
        for index in range(len(self.monster_shot_reacts)):
            if index not in remove_shot_indices:
                updated_monster_shot_rects.append(self.monster_shot_reacts[index])

        self.monster_shot_reacts = updated_monster_shot_rects

    def generate_monsters_shots(self):
        """ For generating shots from monsters randomly. """
        shot_probability = 0.0003 * self.current_level  # Number in [0;1]
        if len(self._monster_reacts):
            for monster in range(len(self._monster_reacts)):
                shooting_flag = np.random.binomial(n=1, p=shot_probability, size=1)[0]  # Returns 1 w. prob. 'p'
                if shooting_flag == 1:
                    self.spawn_monster_shot(monster_index=monster)

    def generate_ufo(self):
        """ For generating ufo's randomly. (only 1 at a time on the screen) """
        if len(self.ufo_reacts) == 0:
            spawn_probability = 0.001  # Number in [0;1]
            spawn_flag = np.random.binomial(n=1, p=spawn_probability, size=1)[0]  # Returns 1 w. prob. 'p'
            if spawn_flag == 1:
                self.spawn_ufo()

    def update_ufo_position(self):
        if len(self.ufo_reacts) > 0:
            for i in range(len(self.ufo_reacts)):
                if self.ufo_direction_flag == 'right':
                    self.ufo_reacts[i] = self.ufo_reacts[i].move(self.ufo_x_vel, 0)
                elif self.ufo_direction_flag == 'left':
                    self.ufo_reacts[i] = self.ufo_reacts[i].move(-self.ufo_x_vel, 0)

    def update_ship_shots_position(self):
        """ For updating positions of shots fired from ship."""
        if len(self._ship_shot_reacts) > 0:
            for i in range(len(self._ship_shot_reacts)):
                self._ship_shot_reacts[i] = self._ship_shot_reacts[i].move(0, -self.shot_y_velocity)

    def update_monster_shots_position(self):
        """ For updating positions of shots fired from monsters. """
        if len(self.monster_shot_reacts) > 0:
            for i in range(len(self.monster_shot_reacts)):
                self.monster_shot_reacts[i] = self.monster_shot_reacts[i].move(0, self.shot_y_velocity)

    def update_ship_shot_reacts(self):
        """ For removing shots fired from ship that are out of screen. """
        if len(self._ship_shot_reacts) > 0:
            self._ship_shot_reacts = [r for r in self._ship_shot_reacts if r.centery >= self.ship_shot_height / 2]

    def update_monster_shot_reacts(self):
        """ For removing shots fired from monsters that are out of screen. """
        if len(self.monster_shot_reacts) > 0:
            self.monster_shot_reacts = [r for r in self.monster_shot_reacts if
                                        r.centery <= self.screen_height - self.ship_shot_height / 2]

    def update_ufo_reacts(self):
        """ Removing ufo that are out of screen"""
        if len(self.ufo_reacts) > 0:
            self.ufo_reacts = [r for r in self.ufo_reacts if
                               self.ufo_width < r.centerx < (self.screen_width - self.ufo_width)]

    def update_score(self):
        """ For updating score value text. """
        self.score_text_value_surface = self.score_board_font.render(" " + str(self.current_score), True,
                                                                     self.text_color, None)
        self.score_text_value_react = self.score_text_value_surface.get_rect()
        self.score_text_value_react.centerx = 120
        self.score_text_value_react.centery = 25

    def update_level(self):
        """ For updating level value text. """
        self.level_text_value_surface = self.score_board_font.render(" " + str(self.current_level), True,
                                                                     self.text_color, None)
        self.level_text_value_react = self.level_text_value_surface.get_rect()
        self.level_text_value_react.centerx = int(self.screen_width/2) + 40
        self.level_text_value_react.centery = 25

    def update_ship_react(self):
        """ For updating ship rect animation. """
        if self.ship_anim_counter == self.ship_anim_duration:
            self.ship_anim_counter = 0
            if self.ship_anim_index == len(self.ship_surfs):
                self.ship_anim_index = 0
            current_x, current_y = self._ship_react.centerx, self._ship_react.centery
            self._ship_surf = self.ship_surfs[self.ship_anim_index]
            self._ship_react = self._ship_surf.get_rect()
            self._ship_react.centerx = current_x
            self._ship_react.centery = current_y
            self.ship_anim_index += 1

    def update_life_reacts(self):
        """ For updating life animation. """
        if self.life_anim_counter == self.life_anim_duration:
            self.life_anim_counter = 0
            if self.life_anim_index == len(self.life_surfs):
                self.life_anim_index = 0
            for life in range(len(self._life_reacts)):
                current_x, current_y = self._life_reacts[life].centerx, self._life_reacts[life].centery
                self._life_surf = self.life_surfs[self.life_anim_index]
                self._life_reacts[life] = self._life_surf.get_rect()
                self._life_reacts[life].centerx = current_x
                self._life_reacts[life].centery = current_y
            self.life_anim_index += 1

    def update_monster_reacts(self):
        """ For updating monster animation. """
        if self.monster_anim_counter == self.monster_anim_duration:
            self.monster_anim_counter = 0
            if self.monster_anim_index == len(self._monster_surfs):
                self.monster_anim_index = 0
            for monster in range(len(self._monster_reacts)):
                current_x, current_y = self._monster_reacts[monster].centerx, self._monster_reacts[monster].centery
                self._monster_surf = self._monster_surfs[self.monster_anim_index]
                self._monster_reacts[monster] = self._monster_surf.get_rect()
                self._monster_reacts[monster].centerx = current_x
                self._monster_reacts[monster].centery = current_y
            self.monster_anim_index += 1

    def update_ufo_anim_reacts(self):
        """ For updating monster animation. """
        if self.ufo_anim_counter == self.ufo_anim_duration:
            self.ufo_anim_counter = 0
            if self.ufo_anim_index == len(self.ufo_surfs):
                self.ufo_anim_index = 0
            for ufo in range(len(self.ufo_reacts)):
                current_x, current_y = self.ufo_reacts[ufo].centerx, self.ufo_reacts[ufo].centery
                self.ufo_surf = self.ufo_surfs[self.ufo_anim_index]
                self.ufo_reacts[ufo] = self._monster_surf.get_rect()
                self.ufo_reacts[ufo].centerx = current_x
                self.ufo_reacts[ufo].centery = current_y
            self.ufo_anim_index += 1

    def update_monster_explosion_reacts(self):
        """ For updating monster explosion animation. """

        # Initially checking if any of the explosion surfs equals last frame surf and updating
        remove_indices = []
        for surf in range(len(self.monster_explosion_anim_surfs)):
            if self.monster_explosion_frame_counters[surf] == len(self.monster_explosion_surfs)-1:  # Last frame
                remove_indices.append(surf)

        updated_explosion_reacts, updated_anim_counters = [], []
        updated_surfs, updated_frame_counts = [], []
        for index in range(len(self.monster_explosion_reacts)):
            if index not in remove_indices:
                assert self.monster_explosion_frame_counters[index] < len(self.monster_explosion_surfs) - 1
                updated_explosion_reacts.append(self.monster_explosion_reacts[index])
                updated_anim_counters.append(self.monster_explosion_anim_counters[index])
                updated_surfs.append(self.monster_explosion_anim_surfs[index])
                updated_frame_counts.append(self.monster_explosion_frame_counters[index])
            else:
                assert self.monster_explosion_frame_counters[index] == len(self.monster_explosion_surfs) - 1

        if len(remove_indices) > 0:
            self.monster_explosion_reacts = updated_explosion_reacts
            self.monster_explosion_anim_counters = updated_anim_counters
            self.monster_explosion_anim_surfs = updated_surfs
            self.monster_explosion_frame_counters = updated_frame_counts

        update_indices = []
        for anim_counter_idx in range(len(self.monster_explosion_anim_counters)):
            if self.monster_explosion_anim_counters[anim_counter_idx] == self.monster_explosion_anim_duration:
                update_indices.append(anim_counter_idx)
                self.monster_explosion_anim_counters[anim_counter_idx] = 0
                self.monster_explosion_frame_counters[anim_counter_idx] += 1
            else:
                self.monster_explosion_anim_counters[anim_counter_idx] += 1
        for index in update_indices:
            self.monster_explosion_anim_surfs[index] = self.monster_explosion_surfs[self.monster_explosion_frame_counters[index]]

    def in_game_render(self):
        # Rendering background
        self._display_surf.blit(self._background_surf, (0, 0))
        # Rendering ship
        self._display_surf.blit(self._ship_surf, self._ship_react)
        # Rendering shots fired by ship
        for ship_shot_react in self._ship_shot_reacts:
            self._display_surf.blit(self._ship_shot_surf, ship_shot_react)
        # Rendering monsters
        for monster_react in self._monster_reacts:
            self._display_surf.blit(self._monster_surf, monster_react)
        # Rendering monster explosion reacts
        for monster_explosion in range(len(self.monster_explosion_reacts)):
            self._display_surf.blit(self.monster_explosion_anim_surfs[monster_explosion],
                                    self.monster_explosion_reacts[monster_explosion])
        # Rendering shots fired by monsters
        for monster_shot_react in self.monster_shot_reacts:
            self._display_surf.blit(self.monster_shot_surf, monster_shot_react)
        # Rendering life symbols
        for life in range(len(self._life_reacts)):
            self._display_surf.blit(self._life_surf, self._life_reacts[life])
        # Rendering ufp
        for ufo in range(len(self.ufo_reacts)):
            self._display_surf.blit(self.ufo_surf, self.ufo_reacts[ufo])
        # Rendering score text
        self._display_surf.blit(self.score_text_surface, self.score_text_react)
        self._display_surf.blit(self.score_text_value_surface, self.score_text_value_react)
        # Rendering level text
        self._display_surf.blit(self.level_text_surface, self.level_text_react)
        self._display_surf.blit(self.level_text_value_surface, self.level_text_value_react)
        # Rendering life text
        self._display_surf.blit(self.life_text_surface, self.life_text_react)
        pygame.display.flip()  # This is needed for image to show up ??

    def game_over_render(self):
        # Rendering background
        self._game_over_display_surf.blit(self._game_over_background_surf, (0, 0))
        self._game_over_display_surf.blit(self.game_over_text_surface, self.game_over_text_react)
        self._game_over_display_surf.blit(self.restart_text_surface, self.restart_text_react)
        pygame.display.flip()

    def loading_render(self):
        # Rendering background
        self._loading_display_surf.blit(self._loading_background_surf, (0, 0))
        self._loading_display_surf.blit(self.loading_text_surfaces[self.loading_text_frame_counter],
                                        self.loading_text_react)
        pygame.display.flip()

    def update_game_over_react(self):
        """ Animating game over text """
        if self.game_over_anim_counter == self.game_over_anim_duration:
            self.game_over_anim_counter = 0
            if self.game_over_position == 'down':
                self.game_over_text_react.centery += 5
                self.game_over_position = 'up'
            else:
                self.game_over_text_react.centery -= 5
                self.game_over_position = 'down'

    def update_loading_react(self):
        """ Animating game over text """
        if self.loading_text_frame_counter == len(self.loading_text_surfaces)-1:
            self.loading_text_frame_counter = 0
            self.loading_anim_completions += 1

        if self.loading_text_anim_counter == self.loading_text_anim_duration:
            self.loading_text_anim_counter = 0
            self.loading_text_frame_counter += 1
            current_x, current_y = self.loading_text_react.centerx, self.loading_text_react.centery
            self.loading_text_react = self.loading_text_surfaces[self.loading_text_frame_counter].get_rect()
            self.loading_text_react.centerx = current_x
            self.loading_text_react.centery = current_y

    def game_over_reset(self):
        self.current_lifes = 3
        self.current_level = 1
        self.current_score = 0

        self._monster_reacts = []
        self.ufo_reacts = []
        self._life_reacts = []
        self.monster_explosion_reacts = []
        self.monster_shot_reacts = []
        self._ship_shot_reacts = []
        self.spawn_monsters()
        self.spawn_lives()

    def new_level_reset(self):
        self.current_level += 1

        self.loading_anim_completions = 0
        self.loading_text_anim_counter = 0
        self.loading_text_frame_counter = 0
        self._monster_reacts = []
        self.ufo_reacts = []
        self.monster_explosion_reacts = []
        self.monster_shot_reacts = []
        self._ship_shot_reacts = []
        self.spawn_monsters()

    @staticmethod
    def on_cleanup():
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False

        self.spawn_monsters()
        self.spawn_lives()
        while self._running:
            pygame.time.delay(10)  # Is this needed ?
            for event in pygame.event.get():
                self.on_event(event)

            if self.current_lifes > 0:

                if len(self._monster_reacts) > 0:
                    # Initially moving monsters right
                    if not self.monster_right_edge_reached and not self.monster_left_edge_reached:
                        self.move_monsters_right()
                        self.update_monster_positions_flag()
                    # Shuffling between left and right
                    else:
                        self.update_monster_positions_flag()
                        if self.monster_right_edge_reached:
                            self.move_monsters_left()
                        if self.monster_left_edge_reached:
                            self.move_monsters_right()

                    self.generate_monsters_shots()
                    self.generate_ufo()

                    self.update_ufo_position()
                    self.update_ufo_reacts()
                    self.update_ufo_anim_reacts()

                    self.update_ship_position()
                    self.update_ship_react()

                    self.update_ship_shots_position()
                    self.update_ship_shot_reacts()

                    self.update_monster_shots_position()
                    self.update_monster_shot_reacts()

                    self.shot_2_ship_collision_detect()
                    self.shot_2_monster_collision_detect()
                    self.shot_2_ufo_collision_detect()

                    self.update_monster_reacts()

                    self.update_monster_explosion_reacts()

                    self.update_life_reacts()
                    self.update_score()
                    self.update_level()

                    self.in_game_render()

                    self.ship_anim_counter += 1
                    self.life_anim_counter += 1
                    self.monster_anim_counter += 1
                    self.ufo_anim_counter += 1
                else:
                    self.update_loading_react()
                    self.loading_render()
                    self.loading_text_anim_counter += 1
                    if self.loading_anim_completions == 2:
                        self.new_level_reset()
            else:
                mouse_position = pygame.mouse.get_pos()
                if self.restart_button_dims[0] <= mouse_position[0] <= self.restart_button_dims[0] + self.restart_button_width \
                        and self.restart_button_dims[1] <= mouse_position[1] <= self.restart_button_dims[1] + self.restart_button_height:
                    pygame.draw.rect(self._game_over_background_surf, self.restart_button_color_light, self.restart_button_dims)
                    left, middle, right = pygame.mouse.get_pressed()
                    if left:
                        self.game_over_reset()
                else:
                    pygame.draw.rect(self._game_over_background_surf, self.restart_button_color_dark, self.restart_button_dims)

                self.game_over_render()
                self.update_game_over_react()
                self.game_over_anim_counter += 1

        self.on_cleanup()


if __name__ == "__main__":
    theApp = SpaceInvadersApp()
    theApp.on_execute()
