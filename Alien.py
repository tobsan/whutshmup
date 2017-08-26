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
from pygame.event import Event, post

from Common import GFX_PATH, SHOTSPEED, BOSS_ENTER, BOSS_EXIT
from Common import ENEMY_FIRE
from Ship import Ship
from Shot import ClusterShot, Smallshot, Mediumshot, Snipeshot

# *******************************************
#
# Regular ships below. 
#
# *******************************************

def all_ships():
    """
    For the graphics module, paint_instructions_enemies()
    """
    return [ ("Scout", Scout.scoutship)
           , ("Alien", Alien.alienship)
           , ("Bomber", Bomber.bombership)
           , ("Chopper", Chopper.choppership)
           , ("Sniper", Sniper.snipership)
           , ("Kamikaze", Kamikaze.kship)
           ] 

class Enemy(Ship):
    """
    The enemy class is the base of all other enemy ships. That way all ships
    have a reference to the player, if they have to aim or change direction
    depending on the player's position (although they could check any part of
    it's state).  NOTE: Enemies are not to alter the player's state, only read
    it, so be nice!
    """
    
    def __init__(self, common, player, init_pos, init_dir, img, speed):
        super(Enemy, self).__init__(common, init_pos, init_dir, img, speed)
        # If enemies should be able to act depending on what the user does, they
        # need to know where the user is and how it moves.
        self.player = player

class Scout(Enemy):
    """
    Just a moving ship that does not fire at all. Apart from the specific
    graphics this is essentially nothing else than a Ship-object
    """

    scoutship = join(GFX_PATH, "enemyship.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(Scout, self).__init__(common, player, init_pos, 
                                    init_dir, Scout.scoutship, speed)
        self.max_damage = 3

class Alien(Enemy):
    """
    The basic enemy ship. They fire small shots forward in fixed intervals and
    does not behave in anyway depending on the player. I wouldn't use them if I
    were a master villain...
    """
    
    alienship = join(GFX_PATH, "enemyship.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(Alien, self).__init__(common, player, init_pos, 
                                    init_dir, Alien.alienship, speed)
        self.max_damage = 6
        
    # Overrides the update function in Ship
    def update(self, *_):
        super(Alien, self).update()
        
        # Should we fire?
        if self.counter % 30 == 0:
            shot = self.__create_shot()
            fire = Event(ENEMY_FIRE, ship = self, shot = shot)
            post(fire)
   
    def __create_shot(self):
        pos, shipdir = self.get_position(), self.get_direction()
        return Smallshot(self.common, pos, shipdir, SHOTSPEED, None)

class Bomber(Enemy):
    """
    Bomber ships. They are large, can take lots of damage, they should be slow
    and they fire Clustershots
    """
    
    bombership = join(GFX_PATH, "bomber.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(Bomber, self).__init__(common, player, init_pos, 
                                     init_dir, Bomber.bombership, speed)
        self.max_damage = 21

    def update(self, *_):
        super(Bomber, self).update()

        if self.counter % 75 == 0:
            (x, y) = self.get_position()
            s_1 = self.__create_shot()
            s_1.set_position((x - self.get_width() / 3, y))
            s_2 = self.__create_shot()
            s_2.set_position((x + self.get_width() / 3, y))
            e_1 = Event(ENEMY_FIRE, ship = self, shot = s_1)
            e_2 = Event(ENEMY_FIRE, ship = self, shot = s_2)
            post(e_1)
            post(e_2)

    def __create_shot(self):
        pos, shipdir = self.get_position(), self.get_direction()
        return ClusterShot(self.common, pos, shipdir, 7, 25, 25)

class Chopper(Enemy):
    """
    The choppers are quite weak, but they fire with high frequency and they fire
    four shots at a time. The only travel forward in a straight line
    """

    choppership = join(GFX_PATH, "chopper.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(Chopper, self).__init__(common, player, init_pos, 
                                      init_dir, Chopper.choppership, speed)
        self.max_damage = 10

    def update(self, *_):
        super(Chopper, self).update()

        if self.counter % 20 == 0:
            (x, y) = self.get_position()
            s_1 = self.__create_shot()
            s_2 = self.__create_shot()
            s_3 = self.__create_shot()
            s_4 = self.__create_shot()
            s_1.set_position((x - self.get_width() / 7, y))
            s_2.set_position((x + self.get_width() / 7, y))
            s_3.set_position((x - 4 * self.get_width() / 7, y))
            s_4.set_position((x + 4 * self.get_width() / 7, y))
            post(Event(ENEMY_FIRE, ship = self, shot = s_1))
            post(Event(ENEMY_FIRE, ship = self, shot = s_2))
            post(Event(ENEMY_FIRE, ship = self, shot = s_3))
            post(Event(ENEMY_FIRE, ship = self, shot = s_4))

    def __create_shot(self):
        pos, shipdir = self.get_position(), self.get_direction()
        return Smallshot(self.common, pos, shipdir, SHOTSPEED, None)

class Sniper(Enemy):
    """
    Besides having the ugliest sprite image in the entire game, snipers are
    quite weak. They don't fire very often, but their shots are really fast.
    """
    snipership = join(GFX_PATH, "sniper.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(Sniper, self).__init__(common, player, init_pos, 
                                     init_dir, Sniper.snipership, speed)
        self.max_damage = 10

    def update(self, *_):
        super(Sniper, self).update()
        (x, y) = self.get_position()
        (xplayer, yplayer) = self.player.get_position()
        if self.counter % 100 == 0:
            shot = self.__create_shot()
            shot.set_direction((xplayer-x, yplayer-y))
            event = Event(ENEMY_FIRE, ship = self, shot = shot)
            post(event)

    def __create_shot(self):
        return Snipeshot(self.common, self.get_position(), self.get_direction())

class Kamikaze(Enemy):
    """
    Kamikaze ships update their direction vector once in a while and tries to
    simply crash into the player. They are however quite weak, so they are easy
    to kill.
    """
    kship = join(GFX_PATH, "kamikaze.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(Kamikaze, self).__init__(common, player, init_pos, 
                                       init_dir, Kamikaze.kship, speed)
        self.max_damage = 5 # Override

    # Override
    def update(self, *_):
        super(Kamikaze, self).update()
        if self.counter % 10 == 0: 
            (x, y) = self.get_position()
            (xplayer, yplayer) = self.player.get_position()
            if y < yplayer-50: # Some kind of threshold
                self.set_strafe_composite((xplayer-x, yplayer-y))


# TODO: Add some kind of miniboss, like the spider-elk but easier.


# ************************************************************************
#
# Boss ships below
#
# ************************************************************************

class Boss(Enemy):
    """
    All the general boss class does is to notify the rest of the game of boss
    entrance and exit, so if you override its methods, remember to call super()
    """

    def __init__(self, common, player, init_pos, init_dir, img, speed):
        super(Boss, self).__init__(common, player, init_pos, 
                                   init_dir, img, speed)
        post(Event(BOSS_ENTER, ship = self))
        self.delay = 100 # Delay before firing

    def kill(self):
        post(Event(BOSS_EXIT))
        super(Boss, self).kill()

    def add_damage(self, damage):
        if self.counter > self.delay:
            super(Boss, self).add_damage(damage)

    def blit(self):
        if self.is_exploding():
            # do something special, a large explosion or so
            super(Boss, self).blit()
        else:
            super(Boss, self).blit()

class FirstBoss(Boss):
    """
    The first boss fires at the player depending on its position with high
    intensity, and also fires two simultaneous ClusterShots every 10 regular
    shots. When its life gets low, it fires more intensively
    
    Nickname: Spindelälgen (the spider elk)
    """
    ship = join(GFX_PATH, "boss.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(FirstBoss, self).__init__(common, player, init_pos, 
                                        init_dir, FirstBoss.ship, speed)

        self.max_damage = 300
        self.set_target((300, 100))

    def update(self, *_):
        super(FirstBoss, self).update()
        # The boss becomes harder close to its death!
        freq = 7 if self.get_damage() < 200 else 5
        if self.counter > self.delay and self.counter % freq == 0:
            # Regular shots, that seek the player!
            (x, y) = self.get_position()
            shot = Mediumshot(self.common, (x, y), self.get_direction(), 20)
            (xplayer, yplayer) = self.player.get_position()
            shot.set_direction((xplayer-x, yplayer-y))
            event = Event(ENEMY_FIRE, ship = self, shot = shot)
            post(event)
        if self.counter > self.delay and self.counter % 100 == 0:
            (x, y) = self.get_position()
            s_1 = self.__create_shot()
            s_1.set_position((x-20, y))
            e_1 = Event(ENEMY_FIRE, ship = self, shot = s_1)
            s_2 = self.__create_shot()
            s_2.set_position((x+20, y))
            e_2 = Event(ENEMY_FIRE, ship = self, shot = s_2)
            post(e_1)
            post(e_2)

    def __create_shot(self):
        pos, shipdir = self.get_position(), self.get_direction()
        return ClusterShot(self.common, pos, shipdir, 8, 10, 10)


# TODO: Move around in a pattern? Like the evil sun in SMB3!
class SecondBoss(Boss):
    """
    The second boss is a spherical one that shoots only very slow clustershots,
    but at a quite high intensity.
    """
    ship = join(GFX_PATH, "boss2.png")

    def __init__(self, common, player, init_pos, init_dir, speed):
        super(SecondBoss, self).__init__(common, player, init_pos,
                                         init_dir, SecondBoss.ship, speed)

        self.max_damage = 500
        self.dircounter = 0
        self.set_target((300, 100))

    def update(self, *_):
        super(SecondBoss, self).update()

        # This is a good start for a boss behaviour, at least!
        if self.counter > self.delay and self.counter % 15 == 0:
            s_1 = self.__create_shot()
            s_2 = self.__create_shot()
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0), 
                    (1, 1), (1, -1), (-1, 1), (-1, -1)
                   ]
            s_1.set_direction(dirs[self.dircounter % 8])
            self.dircounter += 1
            s_2.set_direction(dirs[self.dircounter % 8])
            self.dircounter += 1
            e_1 = Event(ENEMY_FIRE, ship = self, shot = s_1)
            e_2 = Event(ENEMY_FIRE, ship = self, shot = s_2)
            post(e_1)
            post(e_2)

    # The second boss shoots slow shots that have a long timeout, but that
    # creates 30 new small shots.
    def __create_shot(self):
        pos, shipdir = self.get_position(), self.get_direction()
        return ClusterShot(self.common, pos, shipdir, 3, 30, 30)

