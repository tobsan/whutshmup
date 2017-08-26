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

from Common import GFX_PATH, SHOTSPEED, USER_FIRE, PLAYER_DIED
from Ship import Ship, Animation
from Shot import Shot

# TODO: Acceleration up to maxspeed
# TODO: The code for respawning is far from optimal.
# TODO: Different ship images for strafing
class Player(Ship):
    """
    The player is a Ship with power and lives added to it. It is also an
    animated ship. The player can have a hitbox (if not, the hitbox is the whole
    ship). Damage decreases ship power and with that the ship's fire capacity
    """

    shipfile = join(GFX_PATH,"deltawing.png")

    # TODO: Specific hitbox colour that can be mapped instead?
    hitbox = (30, 13, 8, 18) # Measured in GIMP on deltawing.png, heh
    
    def __init__(self, common, init_pos, init_dir, speed):
        super(Player, self).__init__(common, init_pos, init_dir, 
                                     Player.shipfile, speed)

        # Use to animate hitbox or something
        ship = self.res.get_graphics(Player.shipfile)
        self.__animation = Animation([ship], 5)

        # The player can be continously firing by holding the fire button
        self.__firing = False
        self.__firecounter = 1

        self.max_damage = 1
        self.__power = 1
        self.__lives = 3
        self.__targetspeed = 0

        self.__hitmask = self.mask.scale(self.mask.get_size())
        self.create_hitbox(Player.hitbox)
        self.mask = self.__hitmask

    def create_hitbox(self, (x, y, width, height)):
        """
        The hitbox is typically not the whole ship, so it can be set here. This
        should be called only when changing image, since if the hitbox is large,
        this will take too much power to be computed at each tick.
        """
        self.__hitmask.clear()
        for i in range(width):
            for j in range(height):
                self.__hitmask.set_at((x+i, y+j), 1)

    # Overrides the update function in Ship
    def update(self, *_):
        """
        Overrides the update in Ship. For the player, as with the aliens, this
        mostly handles firing, but it also makes sure that the image displayed
        when blitting is the one currently active from the animation
        """

        # Maybe change the animation image
        self.__animation.update()
        # And in that case, this changes, too!
        self.set_image(self.__animation.get_image())
        self.mask = self.__hitmask

        super(Player, self).update()

        # Fires more when highpowered
        if self.__firing and not self.has_target():
            if self.__firecounter % 10 == 0:
                self.__firecounter = 1
                shots = min(2 + self.__power, 6)
                sound = True
                for i in range(shots):
                    shot = self.__create_shot(sound)
                    for _ in range(i):
                        shot.update()
                    post(Event(USER_FIRE, shot = shot))
                    sound = False
            else: self.__firecounter += 1
        elif self.__firecounter != 0:
            # Prevents abuse of the fire button
            self.__firecounter = (self.__firecounter + 1) % 10
    
    def __create_shot(self, sound):
        """
        Since the player generally fires more than one shot at a time, it would
        be unneccessary to play sounds for all of them, hence the sound argument
        which is boolean.
        """
        pos, shipdir = self.get_position(), self.get_direction()
        if sound:
            return Shot(self.common, Shot.playershot, pos, shipdir, SHOTSPEED, 
                        Shot.mediumdamage, Shot.playersound)
        else:
            return Shot(self.common, Shot.playershot, pos, shipdir, SHOTSPEED, 
                        Shot.mediumdamage, None)

    def respawn(self):
        """
        If the player dies but has more lives, a respawn is performed. This
        function could be used to do a fancy entrance to the screen, too.
        """
        # Set life/power
        self.__lives -= 1
        self.__power = 1
        self.reset_damage()
        # Set location
        rect = self.surface.get_rect()
        (x, y) = rect.centerx, rect.bottom - 100
        self.set_position((x, y))
        # TODO: Nice entrance
        # TODO: Temporary immortality
        # Make the ship un-manouverable by setting a target
        # self.set_target((x, y - 150))

    def add_damage(self, amount):
        """
        Override from ship, since for the player, power and damage are each
        others opposites. Therefore, we emulate that behaviour in this method.
        """
        self.__power -= amount
        if self.__power <= 0:
            super(Player, self).add_damage(self.max_damage)
            if self.__lives == 0:
                # Communicate to the rest of the game
                post(Event(PLAYER_DIED))
            else:
                self.respawn()
        else:
            # This is done only so the damage flag is set in Ship, to give the
            # player a visual cue about it being hit
            super(Player, self).add_damage(0)

    #
    # General getters and setters below
    #

    def set_fire(self, value):
        self.__firing = value

    def is_firing(self):
        return self.__firing

    def set_power(self, value):
        self.__power = value
    
    def get_power(self):
        return self.__power
    power = property(get_power, set_power)
    
    def set_lives(self, lives):
        self.__lives = lives

    def get_lives(self):
        return self.__lives
    lives = property(get_lives, set_lives)

