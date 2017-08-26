# -*- coding: UTF-8 -*-
"""
Copyright (c) Tobias Olausson (tobsan@tobsan.se) 2013
 
This file is part of whutshmup

whutshmup is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later 
version.

whutshmup is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License along with 
whutshmup. If not, see <http://www.gnu.org/licenses/>.
"""

from os.path import join

import pygame
from pygame.locals import QUIT, KEYDOWN, KEYUP
from pygame.sprite import Group

from Common import FRAMERATE, RUNNING, CLEARED, DIED, QUITGAME, ABORTED
from Common import ENEMY_FIRE, USER_FIRE, BOSS_ENTER, BOSS_EXIT, PLAYER_DIED
from Common import SHIPSPEED, MP3_PATH

from Vec2d import Vec2d
from Ship import Ship
from Level import Barrier, Item

from Player import Player
from Alien import Scout, Alien, Bomber, Sniper, Chopper, Kamikaze
from Alien import FirstBoss, SecondBoss
from Graphics import flip

class GameLogic:
    """
    GameLogic class handles an instance of the game, which in this case is
    actually a level. However, the same GameLogic instance can be used for later
    levels. 

    This class does all the heavy lifting in the game, it updates every object's
    state, adds objects to the level, does collision detection and event
    handling.
    """

    def __init__(self, graphics, resources, options):
        self.__graphics = graphics
        self.__resources = resources
        self.__options = options
        self.__common = (graphics.surface, resources, options)
        self.__ship = None
        # Different groups to avoid friendly fire
        self.__enemy_shots = Group() 
        self.__player_shots = Group()
        self.__enemies = Group() 
        self.__explosions = Group()
        self.__items = Group()
        self.__state = RUNNING
        self.__boss = None
        self.__keysdown = []
        self.__level = {}

    def game_loop(self):
        self.__state = RUNNING
        clock = pygame.time.Clock()
        while self.__state == RUNNING: 
            if self.has_won():
                self.__state = CLEARED
                break
            self.handle_events()
            self.tick()
            self.paint_stuff()
            clock.tick(FRAMERATE)
        return self.__state

    def has_won(self):
        return self.is_alive() and len(self.__level) == 0 and len(self.__enemies.sprites()) == 0 and len(self.__explosions.sprites()) == 0 and len(self.__enemy_shots.sprites()) == 0

    def is_alive(self):
        if self.__ship.get_lives() == 0:
            return not self.__ship.is_exploding()
        return True

    # Removes anything from the game that is level dependent
    # Also resets parts of the ship
    def clear(self):
        self.__enemy_shots.empty()
        self.__player_shots.empty()
        self.__enemies.empty()
        self.__explosions.empty()
        self.__level = {}
        self.__keysdown = []
        self.__boss = None
        self.__ship.set_fire(False)
        self.__ship.set_strafe(0)
        self.__ship.speed = 0
        self.__state = RUNNING

    def set_level(self, level):
        self.__level = level

    # Add a player ship
    def add_player(self):
        direction = (0, -1) # North
        common = (self.__graphics.surface, self.__resources, self.__options)
        (x, y) = common[0].get_rect().centerx, common[0].get_rect().bottom - 50
        self.__ship = Player(common, (x, y), direction, 0)

    def get_player(self):
        return self.__ship
    
    # Start continous fire by a ship
    def start_fire(self):
        self.__ship.set_fire(True)
        
    # Stop continous fire by a ship
    def stop_fire(self):
        self.__ship.set_fire(False)
    
    def add_enemy(self, enemy):
        self.__enemies.add(enemy)
    
    def get_enemies(self):
        return self.__enemies
    
    # Handles events generated by the user pressing the arrow keys.
    # TODO: Holding Left, Down and Right makes the ship go forward
    # TODO: Holding while respawning does not work.
    def arrow_pressed(self, keycode, keysdown):
        if not self.__ship.has_target():
            opts = self.__options
            arrows = [opts.up, opts.down, opts.left, opts.right]
            arrows_pressed = filter(lambda x: x in keysdown, arrows)
            last_pressed = None
            if len(arrows_pressed) > 0:
                last_pressed = arrows_pressed.pop()
            
            # Movement of the ship is made by strafing relative to the current
            # direction of the ship. Values found by trial and error.
            # TODO: Figure out why these values work, since they still don't
            #       make any sense
            dirs = { opts.up : (1, 0), opts.left : (0, -1)
                   , opts.down : (-1, 0), opts.right : (0, 1)
                   }
            strafe_1 = Vec2d(dirs[keycode])
            if last_pressed == None:
                self.__ship.strafe = strafe_1.get_angle()
            else:
                strafe_2 = Vec2d(dirs[last_pressed])
                strafe_total = strafe_1 + strafe_2
                self.__ship.strafe = strafe_total.get_angle()

            self.__ship.speed = SHIPSPEED

    # Handles events generated when a held arrow is released
    def arrow_released(self, pressed_keys):
        if not self.__ship.has_target():
            opts = self.__options
            arrows = set([opts.up, opts.down, opts.left, opts.right])
            pressed_arr = arrows & set(pressed_keys)
            if len(pressed_arr) == 0: 
                self.__ship.speed = 0
                self.__ship.strafe = 0 # No strafe
            else:
                latest = pressed_arr.pop()
                # Remove the latest pressed button temporarily
                pressed_fake = [k for k in pressed_keys if k != latest]
                # There are other arrows still pressed, so we need to
                # recalculate the strafe angle for those, so faking a button
                # press will do.
                self.arrow_pressed(latest, pressed_fake)

    # Check and see if there are any collisions within these coordinates
    def check_collisions(self):
        """
        Performs collision detection:
            1) Between the player and any enemy shots
            2) Between enemies and any player shots
            3) Between the enemy ships and the player ship
            4) Between the player and any items
            5) Between the player and the screen (boundary check)

        It also removes any objects that died or that are too far outside the
        screen to be considered interesting.

        All collisions are checked using masks and using the functions in
        pygame.sprite
        """
        player = self.__ship
        enemies = self.__enemies
        enemy_shots = self.__enemy_shots
        player_shots = self.__player_shots
        items = self.__items
        screen = self.__graphics.surface.get_rect()
        
        # First, see if the player was shot, and in that case - do something!
        if len(enemy_shots.sprites()) > 0:
            ship_shot = pygame.sprite.spritecollide(
                player,                     # Collide the player
                enemy_shots,                # With all enemy shots
                True,                       # Kill the enemy shots
                pygame.sprite.collide_mask  # Use masks for collision detection
            )
            for shot in ship_shot:
                player.add_damage(shot.get_damage())

        # Second, see if any enemies were shot by the player (or by themselves)
        if len(enemies.sprites()) > 0 and len(player_shots.sprites()) > 0:
            enemies_shot = pygame.sprite.groupcollide(
                enemies,                    # Collide all enemies
                player_shots,               # With all player shots
                False,                      # Don't kill the enemies
                True,                       # But kill all shots
                pygame.sprite.collide_mask  # Use masks for collision detection
            )
            for enemy in enemies_shot:
                shots = enemies_shot[enemy]
                for shot in shots:
                    enemy.add_damage(shot.get_damage())
        
        # Before step three and four, we want to use the whole ship as hitbox,
        # so we need to set its mask to its original state. This will be
        # changed back later.
        oldmask = player.mask.scale(player.mask.get_size())
        player.mask = pygame.mask.from_surface(player.image)

        # Third, see if any enemies were hit by the player's ship
        if len(enemies.sprites()) > 0:
            ship_collide = pygame.sprite.spritecollide(
                player,                     # Collide the player
                enemies,                    # With all enemies
                False,                      # Don't kill the enemies
                pygame.sprite.collide_mask  # Use masks for collision detection
            )
            for enemy in ship_collide:
                player.add_damage(max(0, enemy.max_damage - enemy.get_damage()))
                enemy.add_damage(5)

        # Fourth: See if any items was hit by the ship
        if len(items.sprites()) > 0:
            item_collide = pygame.sprite.spritecollide(
                player,                     # Collide the player
                items,                      # With all items
                False,                      # Don't kill the items
                pygame.sprite.collide_mask  # Use masks for collision detection
            )
            for item in item_collide:
                if item.is_boxed():
                    player.add_damage(1)
                    item.unbox()
                else:
                    if item.get_type() == Item.LIFE:
                        player.lives += item.get_value()
                    elif item.get_type() == Item.POWER:
                        player.power += item.get_value()
                    item.kill()

        # Fourth and a half: See if any items was shot by the ship
        if len(items.sprites()) > 0:
            item_hit = pygame.sprite.groupcollide(
                items,                     # Collide all items
                player_shots,              # With all player shot
                False,                     # Don't kill the items
                True,                      # But do kill the shots
                pygame.sprite.collide_mask # Use masks for collision detection
            )
            for item in item_hit:
                if item.is_boxed():
                    item.unbox()
        
        # Now, reset the player's mask
        player.mask = oldmask

        # Fifth: The player may not leave the screen, unless the ship is
        # respawning and doing a cool entrance animation, sort of
        rect = player.rect
        if not player.has_target():
            if rect.right >= screen.right: 
                (_, y) = player.get_position()
                player.set_position((screen.right - player.get_width() / 2, y))
            if rect.left <= screen.left:
                (_, y) = player.get_position()
                player.set_position((screen.left + player.get_width() / 2, y))
            if rect.bottom >= screen.bottom:
                (x, _) = player.get_position()
                pheight = player.get_height()
                player.set_position((x, screen.bottom - pheight / 2))
            if rect.top <= screen.top:
                (x, _) = player.get_position()
                player.set_position((x, screen.top + player.get_height() / 2))

        #
        # Cleaning time!
        #
        
        # Remove any ships that were too damaged, or that are completely 
        # outside the screen.
        for ship in enemies.sprites():
            if ship.is_exploding(): 
                ship.kill()
                self.__explosions.add(ship)
            # Ships are considired dead if they are more than 600 px away from
            # their nearest screen boundary
            virtual_screen = screen.inflate(1200, 1200)
            if not virtual_screen.colliderect(ship.rect): 
                ship.kill()
        
        # Remove any shots that are outside the screen 
        for shot in enemy_shots.sprites():
            if not screen.colliderect(shot.rect): 
                shot.kill()
        for shot in player_shots.sprites():
            if not screen.colliderect(shot.rect): 
                shot.kill()
        
    # Runs one step in the game logic, including everything
    def tick(self):
        # Move the level, check for any additions
        self.__graphics.scroll()
        self.check_level()
        # Move anything that moves
        self.__enemy_shots.update()
        self.__player_shots.update()
        self.__ship.update()
        self.__enemies.update()
        self.__items.update()
        # Check if anything has collided
        self.check_collisions()
    
    def check_level(self):
        player = self.__ship
        dist = self.__graphics.get_total_distance()
        todo = self.__level.get(dist)
        
        # Each of these are tuples with distance and a list of stuff to do. So
        # for each tuple work....
        # TODO: Currently barriers need to come completely alone, that is, they
        # cannot have the same distance value as any other item. That's a
        # bummer.
        for work in todo:
            for item in work:
                init = item['item']
                # If it is a Barrier item, we don't want to add any items to the
                # game, but rather just postpone everything until all current
                # enemies on the screen have been defeated.
                if init == Barrier:
                    if len(self.__enemies.sprites()) > 0:
                        scroll = self.__graphics.get_scroll()
                        # We use scroll speed here and not the difference
                        # between traveled distance and the object. This is
                        # because we have to take into account that we
                        # accumulate the value for distance since the barrier
                        # stays in place as long as there are enemies left.
                        self.__level.scroll(scroll)
                    else:
                        # Enemies defeated, so we remove the barrier!
                        self.__level.pop(0)
                    # Barrier items should come alone, but just to be sure we do
                    # not want to process any other items here
                    break

                else:
                    # Anything that is not a barrier has to have at least an
                    # initial position. Other attributes that are common to
                    # everything have default values
                    pos = item['pos']
                    direction = (0, 1)
                    if 'direction' in item:
                        direction = item['direction']
                    speed = 5 if 'speed' not in item else item['speed']

                    if init == Item:
                        item_type = item['type']
                        value = item['value']
                        i = init(self.__common, pos, direction, 
                                 speed, item_type, value)
                        self.__items.add(i)
                    else:
                        strafe = 0 if 'strafe' not in item else item['strafe']
                        i = init(self.__common, player, pos, direction, speed)
                        i.set_strafe(strafe)
                        # Ships may have a target position, which in that case
                        # is provided with the "target" key.
                        if 'target' in item:
                            i.set_target(item['target'])
                        self.add_enemy(i) # Just for now, everything is enemies
            
    def set_scrolling_speed(self, speed):
        self.__graphics.set_scroll(speed)

    def paint_stuff(self):
        # Paint background
        self.__graphics.paint_bg()
        
        # Paint the ships
        for explode in self.__explosions:
            explode.blit()
        for enemy in self.__enemies:
            enemy.blit()
        self.__ship.blit()

        # Paint GFX
        for shot in self.__enemy_shots:
            shot.blit()
        for shot in self.__player_shots:
            shot.blit()
        for item in self.__items:
            item.blit()

        # Print ship status
        self.__graphics.paint_stats(self.__ship)
        if self.__boss != None: 
            self.__graphics.paint_boss(self.__boss)
        # Update the screen
        flip()
        
    # Event handling function. 
    def handle_events(self):
        opts = self.__options
        for event in pygame.event.get():
            # 
            # Check for exit events. Whenever the user closes # the window, 
            # that's an exit event, and the game should end.
            # 
            if event.type == QUIT:
                self.__state = QUITGAME
                break

            if event.type == KEYDOWN and event.key == opts.abort:
                self.__state = ABORTED
                break
            
            # 
            # Check for movement by the player. Movement is generated by
            # pressing any of the arrow buttons. 
            # 
            arrows = [opts.up, opts.down, opts.left, opts.right]
            if event.type == KEYDOWN and event.key in arrows:
                if event.key not in self.__keysdown:
                    # The order of these calls is important
                    self.arrow_pressed(event.key, self.__keysdown)
                    self.__keysdown.append(event.key)
            
            if event.type == KEYUP and event.key in arrows:
                if event.key in self.__keysdown: 
                    # Order important here as well.
                    self.__keysdown.remove(event.key)
                    self.arrow_released(self.__keysdown)
            
            # 
            # The player can also fire the laser on the ship, by pressing 
            # and optionally holdning space
            #
            if event.type == KEYDOWN and event.key == opts.fire:
                self.start_fire()
            
            if event.type == KEYUP and event.key == opts.fire:
                self.stop_fire()
            
            #
            # If the player holds space, the ship will create USER_FIRE events
            # with shots in them. 
            #
            if event.type == USER_FIRE:
                self.__player_shots.add(event.shot)

            #
            # Enemies can also fire, by triggering an event
            # Event dictionary must contain shot, but should also contain ship
            #
            if event.type == ENEMY_FIRE:
                self.__enemy_shots.add(event.shot)

            # 
            # BOSS TIME!
            # These events are generated in init and kill in the boss class
            # They are used so that special boss information can be displayed
            # 
            if event.type == BOSS_ENTER:
                self.__boss = event.ship
                if opts.music:
                    pygame.mixer.music.load(join(MP3_PATH,"boss.mp3"))
                    pygame.mixer.music.play()

            if event.type == BOSS_EXIT:
                # TODO: Some other cool effect?
                self.__boss = None
        
            if event.type == PLAYER_DIED:
                self.__state = DIED
