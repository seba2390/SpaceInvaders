import pygame
import torch
from pygame.locals import *
import numpy as np
from copy import deepcopy
from Util import *
from GameObjects import *
import time


class SpaceInvadersApp:
    def __init__(self, display_gameplay, seed, neural_net=None):
        np.random.seed(seed)

        self.maxIter = 1500
        self.maxCounter = 0
        self.monsters_killed = 0
        self.ufos_killed = 0
        self.display_gameplay = display_gameplay
        self.is_training = not self.display_gameplay

        self.neural_net = neural_net
        self._running = True
        self._resolution = 50
        self.screen_size = self.screen_width, self.screen_height = 1353, 709

        self.buffer = 20
        self.shot_buffer = 5
        self.monster_buffer = 5

        self.is_dead = False
        self.death_punishment = -10
        self.hit_punishment = -0.33
        self.killed_enemy_reward = 1
        self.killed_ufo_reward = 1

        self.nr_lives = 3
        self.current_level = 1
        self.current_score = 0
        self.current_lifes = 3
        self.current_reward = 0
        self.in_game = True

        if display_gameplay:
            pygame.init()
            self.pygame_gfx = PygameGraphics(screen_width=self.screen_width, screen_height=self.screen_height)
        else:
            self.pygame_gfx = None

        self.monsters = Monsters(height=45, width=45, screen_width=self.screen_width,
                                 screen_height=self.screen_height, display_gameplay=self.display_gameplay)

        self.ship = SpaceShip(height=80, width=80, screen_width=self.screen_width,
                              screen_height=self.screen_height, display_gameplay=self.display_gameplay)

        self.ufo = Ufo(height=55,width=55,display_gameplay=self.display_gameplay,
                       screen_height=self.screen_height,screen_width=self.screen_width)

    def on_init(self):
        # Initializing pygame and loading in graphics for background
        pygame.init()
        self._running = True
        if self.display_gameplay:
            self.pygame_gfx = PygameGraphics(screen_width=self.screen_width, screen_height=self.screen_height)

    def _set_action(self, action: int) -> None:
        int_2_action = {0: "left", 1: "right", 2: "leftShoot", 3: "rightShoot", 4: "shoot", 5: "DoNothing"}
        action = int_2_action[action]
        assert self.ship.rect.left >= 0, "before"
        assert self.ship.rect.right <= self.screen_width, "before"
        if action == "left" and self.ship.rect.left >= 0 + 1.2 * self.ship.x_velocity:
            self.ship.rect = self.ship.rect.move(-self.ship.x_velocity, 0)
        if action == "right" and self.ship.rect.right <= self.screen_width - 1.2 * self.ship.x_velocity:
            self.ship.rect = self.ship.rect.move(self.ship.x_velocity, 0)
        if action == "leftShoot" and self.ship.rect.left >= 0 + 1.2 * self.ship.x_velocity:
            self.ship.rect = self.ship.rect.move(-self.ship.x_velocity, 0)
            self.ship.shots.spawn_ship_shot(centerx=self.ship.rect.centerx,
                                            centery=self.ship.rect.centery,
                                            ship_height=self.ship.height)
        if action == "shoot":
            self.ship.shots.spawn_ship_shot(centerx=self.ship.rect.centerx,
                                            centery=self.ship.rect.centery,
                                            ship_height=self.ship.height)
        if action == "rightShoot" and self.ship.rect.right <= self.screen_width - 1.2 * self.ship.x_velocity:
            self.ship.rect = self.ship.rect.move(self.ship.x_velocity, 0)
            self.ship.shots.spawn_ship_shot(centerx=self.ship.rect.centerx,
                                            centery=self.ship.rect.centery,
                                            ship_height=self.ship.height)
        if action == "DoNothing":
            pass

        assert self.ship.rect.left >= 0, "after"
        assert self.ship.rect.right <= self.screen_width, "after"

    def get_state(self) -> torch.Tensor:
        col_width = int(self.screen_width / self._resolution)

        state0 = [0 for i in range(self._resolution)]
        for i in range(0, self._resolution):
            for monster in self.monsters.monsters:
                if i * col_width <= self.ship.rect.centerx <= (i + 1) * col_width:
                    state0[i] = 1

        num_monster_rows = 3
        num_current_shots = len(self.monsters.shots.shots)
        state1 = [0 for i in range(self._resolution)]
        for i in range(0, self._resolution):
            for monster in self.monsters.monsters:
                if i * col_width <= monster.centerx <= (i + 1) * col_width:
                    state1[i] += 1.0 / num_monster_rows

        state2 = [0 for i in range(self._resolution)]
        for i in range(0, self._resolution):
            for shot in self.monsters.shots.shots:
                if i * col_width <= shot.centerx <= (i + 1) * col_width:
                    state2[i] += 1.0 / num_current_shots

        state = torch.tensor(state0 + state1 + state2, dtype=torch.float32).reshape(1, -1)
        return state

    def on_event(self, event):
        if event is not None:
            if event.type == pygame.QUIT:
                self._running = False

        if self.neural_net is None:
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.ship.shots.spawn_ship_shot(centerx=self.ship.rect.centerx,
                                                    centery=self.ship.rect.centery,ship_height=self.ship.height)

    def update_ship_position(self, action=None):
        """ For updating position (left and right) of ship when pressing L/R or A/D"""
        if action is None:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.ship.rect.x > 0 + self.buffer:
                    self.ship.rect = self.ship.rect.move(-self.ship.x_velocity, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.ship.rect.x < self.screen_width - self.ship.width - self.buffer:
                    self.ship.rect = self.ship.rect.move(self.ship.x_velocity, 0)
        else:
            self._set_action(action=action)

    def shot_2_monster_collision_detect(self):
        """ For detecting collisions between shots fired from ships, and monsters
            which also updates list of monster rects and list of shot rects,
            when collision detected. (N.B. Also updates current score.)"""
        remove_shot_indices = []
        remove_monster_indices = []
        for monster in range(len(self.monsters.monsters)):
            for ship_shot in range(len(self.ship.shots.shots)):
                check_collision = pygame.Rect.colliderect if not self.is_training else monster_detect_collision
                if check_collision(self.monsters.monsters[monster], self.ship.shots.shots[ship_shot]):
                    remove_shot_indices.append(ship_shot)
                    remove_monster_indices.append(monster)
                    break

        nr_kils = len(remove_monster_indices)
        initial = len(self.monsters.monsters)

        # Updating score
        for kill in range(len(remove_monster_indices)):
            self.current_score += 10
            self.current_reward += self.killed_enemy_reward
            self.monsters_killed += 1

        # Spawning explosion at monster
        if self.display_gameplay:
            for kill in range(len(remove_monster_indices)):
                self.pygame_gfx.spawn_monster_explosion(self.monsters, remove_monster_indices[kill])

        updated_monster_rects = []
        for index in range(len(self.monsters.monsters)):
            if index not in remove_monster_indices:
                updated_monster_rects.append(self.monsters.monsters[index])
        updated_ship_shot_rects = []
        for index in range(len(self.ship.shots.shots)):
            if index not in remove_shot_indices:
                updated_ship_shot_rects.append(self.ship.shots.shots[index])

        self.monsters.monsters = updated_monster_rects
        self.ship.shots.shots = updated_ship_shot_rects
        final = len(self.monsters.monsters)
        assert initial - nr_kils == final

    def shot_2_ufo_collision_detect(self):
        """ For detecting collisions between shots fired from ships, and monsters
            which also updates list of monster rects and list of shot rects,
            when collision detected. (N.B. Also updates current score.)"""
        remove_shot_indices = []
        remove_ufo_indices = []
        for ufo in range(len(self.ufo.rects)):
            for ship_shot in range(len(self.ship.shots.shots)):
                # check_collision = pygame.Rect.colliderect if not self.is_training else detect_collision
                # if check_collision(self.ufo_rects[ufo], self._ship_shot_rects[ship_shot]):
                #    remove_shot_indices.append(ship_shot)
                #    remove_ufo_indices.append(ufo)
                pass

        # Updating score
        for kill in range(len(remove_ufo_indices)):
            self.current_score += 50
            self.current_reward += self.killed_ufo_reward

        updated_ufo_rects = []
        for index in range(len(self.ufo.rects)):
            if index not in remove_ufo_indices:
                updated_ufo_rects.append(self.ufo.rects[index])
        updated_ship_shot_rects = []
        for index in range(len(self.ship.shots.shots)):
            if index not in remove_shot_indices:
                updated_ship_shot_rects.append(self.ship.shots.shots[index])

        self.ufo.rects = updated_ufo_rects
        self.ship.shots.shots = updated_ship_shot_rects

    def shot_2_ship_collision_detect(self):
        """ For detecting collisions between shots fired from enemies, and ship
            which also updates list of shot rects and list of life rects
            when collision detected. (N.B. Also updates current life score.)"""
        remove_shot_indices = []
        for monster_shot in range(len(self.monsters.shots.shots)):
            check_collision = pygame.Rect.colliderect if not self.is_training else ship_detect_collision
            if check_collision(self.ship.rect, self.monsters.shots.shots[monster_shot]):
                remove_shot_indices.append(monster_shot)
                # Remove last life in life rects
                if self.display_gameplay:
                    self.pygame_gfx._life_rects = self.pygame_gfx._life_rects[:len(self.pygame_gfx._life_rects) - 1]
                # Update score
                self.current_lifes -= 1
                self.current_reward += self.hit_punishment

        updated_monster_shot_rects = []
        for index in range(len(self.monsters.shots.shots)):
            if index not in remove_shot_indices:
                updated_monster_shot_rects.append(self.monsters.shots.shots[index])
        self.monsters.shots.shots = updated_monster_shot_rects

    def in_game_render(self):
        # Rendering background
        self.pygame_gfx._display_surf.blit(self.pygame_gfx._background_surf, (0, 0))
        # Rendering ship
        self.pygame_gfx._display_surf.blit(self.ship.surf, self.ship.rect)
        # Rendering shots fired by ship
        for ship_shot_rect in self.ship.shots.shots:
            self.pygame_gfx._display_surf.blit(self.ship.shots.surf, ship_shot_rect)
        # Rendering monsters
        for monster_rect in self.monsters.monsters:
            self.pygame_gfx._display_surf.blit(self.monsters.surf, monster_rect)
        # Rendering monster explosion rects
        for monster_explosion in range(len(self.pygame_gfx.monster_explosion_rects)):
            self.pygame_gfx._display_surf.blit(self.pygame_gfx.monster_explosion_anim_surfs[monster_explosion],
                                    self.pygame_gfx.monster_explosion_rects[monster_explosion])
        # Rendering shots fired by monsters
        for monster_shot_rect in self.monsters.shots.shots:
            self.pygame_gfx._display_surf.blit(self.monsters.shots.surf, monster_shot_rect)
        # Rendering life symbols
        for life in range(len(self.pygame_gfx._life_rects)):
            self.pygame_gfx._display_surf.blit(self.pygame_gfx._life_surf, self.pygame_gfx._life_rects[life])
        # Rendering ufp
        for ufo in range(len(self.ufo.rects)):
            self.pygame_gfx._display_surf.blit(self.ufo.surf, self.ufo.rects[ufo])
        # Rendering score text
        self.pygame_gfx._display_surf.blit(self.pygame_gfx.score_text_surface, self.pygame_gfx.score_text_rect)
        self.pygame_gfx._display_surf.blit(self.pygame_gfx.score_text_value_surface, self.pygame_gfx.score_text_value_rect)
        # Rendering level text
        self.pygame_gfx._display_surf.blit(self.pygame_gfx.level_text_surface, self.pygame_gfx.level_text_rect)
        self.pygame_gfx._display_surf.blit(self.pygame_gfx.level_text_value_surface, self.pygame_gfx.level_text_value_rect)
        # Rendering life text
        self.pygame_gfx._display_surf.blit(self.pygame_gfx.life_text_surface, self.pygame_gfx.life_text_rect)
        pygame.display.flip()  # This is needed for image to show up ??

    def game_over_reset(self):
        self.current_lifes = 3
        self.current_level = 1
        self.current_score = 0
        self.monsters.monsters = []
        self.ufo.rects = []
        self.pygame_gfx._life_rects = []
        self.pygame_gfx.monster_explosion_rects = []
        self.monsters.shots.shots = []
        self.ship.shots.shots_ship_shot_rects = []
        self.monsters.initialize()
        self.pygame_gfx.spawn_lives(self.nr_lives)

    def new_level_reset(self):
        self.current_level += 1
        self.pygame_gfx.loading_anim_completions = 0
        self.pygame_gfx.loading_text_anim_counter = 0
        self.pygame_gfx.loading_text_frame_counter = 0
        self.monsters.monsters = []
        self.ufo.rects = []
        self.pygame_gfx.monster_explosion_rects = []
        self.monsters.shots.shots = []
        self.ship.shots.shots = []
        self.monsters.initialize()

    @staticmethod
    def on_cleanup():
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False

        self.ship.initialize()
        self.monsters.initialize()
        self.pygame_gfx.spawn_lives(self.nr_lives)
        while self._running:
            pygame.time.delay(10)  # Is this needed ?
            for event in pygame.event.get():
                self.on_event(event)

            if self.current_lifes > 0:

                if len(self.monsters.monsters) > 0:
                    self.monsters.move()

                    self.monsters.generate_monsters_shots(self.current_level)
                    self.ufo.generate_ufo()

                    self.ufo.update_ufo_position()
                    self.ufo.update_ufo_rects()
                    self.pygame_gfx.update_ufo_anim_rects(self.ufo)

                    if self.neural_net is None:
                        self.update_ship_position()
                    else:
                        current_state = self.get_state()
                        actions = self.neural_net.forward(current_state)
                        best_action = torch.argmax(actions).item()
                        self.update_ship_position(action=best_action)
                    self.ship.update_ship_rect()

                    self.ship.update_ship_shots_position()
                    self.ship.update_ship_shot_rects()

                    self.monsters.update_monster_shots_position()
                    self.monsters.update_monster_shot_rects()

                    self.shot_2_ship_collision_detect()
                    self.shot_2_monster_collision_detect()
                    self.shot_2_ufo_collision_detect()

                    self.monsters.update_monster_rects()

                    self.pygame_gfx.update_monster_explosion_rects()

                    self.pygame_gfx.update_life_rects()
                    self.pygame_gfx.update_score(self.current_score)
                    self.pygame_gfx.update_level(self.current_level)

                    self.in_game_render()

                    self.pygame_gfx.ship_anim_counter += 1
                    self.pygame_gfx.life_anim_counter += 1
                    self.pygame_gfx.monster_anim_counter += 1
                    self.pygame_gfx.ufo_anim_counter += 1
                else:
                    self.is_dead = True
                    self.pygame_gfx.update_loading_rect()
                    self.pygame_gfx.loading_render()
                    self.pygame_gfx.loading_text_anim_counter += 1
                    if self.pygame_gfx.loading_anim_completions == 2:
                        self.new_level_reset()
            else:
                mouse_position = pygame.mouse.get_pos()
                if self.pygame_gfx.restart_button_dims[0] <= mouse_position[0] <= self.pygame_gfx.restart_button_dims[
                    0] + self.pygame_gfx.restart_button_width \
                        and self.pygame_gfx.restart_button_dims[1] <= mouse_position[1] <= self.pygame_gfx.restart_button_dims[
                    1] + self.pygame_gfx.restart_button_height:
                    pygame.draw.rect(self.pygame_gfx._game_over_background_surf, self.pygame_gfx.restart_button_color_light,
                                     self.pygame_gfx.restart_button_dims)
                    left, middle, right = pygame.mouse.get_pressed()
                    if left:
                        self.game_over_reset()
                else:
                    pygame.draw.rect(self.pygame_gfx._game_over_background_surf, self.pygame_gfx.restart_button_color_dark,
                                     self.pygame_gfx.restart_button_dims)

                self.pygame_gfx.game_over_render()
                self.pygame_gfx.update_game_over_rect()
                self.pygame_gfx.game_over_anim_counter += 1

        self.on_cleanup()

    def initialize_environment(self):
        self.ship.rect = FakeRect(width=self.ship.width, height=self.ship.height)
        self.monsters.shots.rect = FakeRect(width=self.monsters.shots.width, height=self.monsters.shots.height)
        self.monsters.rect = FakeRect(width=self.monsters.width, height=self.monsters.height)
        self.ufo.rect = FakeRect(width=self.ufo.width, height=self.ufo.height)
        self.ship.shots.rect = FakeRect(width=self.monsters.shots.width, height=self.monsters.shots.height)
        self.monsters.initialize()
        self.ship.initialize()

    def initialize_new_level(self):
        self.current_level += 1
        self.monsters_killed = 0
        self.monsters.shots.shots = []
        self.ship.shots.shots = []
        self.monsters.monsters = []
        self.initialize_environment()

    def step(self, action: int):

        self.current_reward = 0
        if self.monsters_killed == 30:
            assert len(self.monsters.monsters) == 0, print(len(self.monsters.monsters))
            self.maxCounter = 0
            self.current_reward += 3
            self.initialize_new_level()

        self._set_action(action=action)

        if len(self.ship.shots.shots) > 0:
            pass
        # print(self._ship_shot_rects[0].centery)

        # print(f"Monster pos: {self._monster_rects[0].centerx}")
        if self.maxCounter == self.maxIter:
            self._running = False
        if self.is_dead:
            self._running = False
            self.current_reward += self.death_punishment
        else:
            if self.current_lifes > 0:

                if len(self.monsters.monsters) > 0:
                    # Initially moving monsters right
                    self.monsters.move()

                    self.monsters.generate_monsters_shots(self.current_level)

                    self.ufo.generate_ufo()

                    self.ufo.update_ufo_position()

                    self.ufo.update_ufo_rects()

                    self.ship.update_ship_shots_position()

                    self.ship.update_ship_shot_rects()

                    self.monsters.update_monster_shots_position()

                    self.monsters.update_monster_shot_rects()

                    self.shot_2_ship_collision_detect()

                    self.shot_2_monster_collision_detect()

                    self.shot_2_ufo_collision_detect()

        new_state = self.get_state()
        self.maxCounter += 1
        gameover = not self._running

        return self.current_reward, gameover, new_state


if __name__ == "__main__":
    theApp = SpaceInvadersApp(display_gameplay=True,seed=0)
    theApp.on_execute()
