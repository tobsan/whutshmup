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
from Vec2d import Vec2d
from Shadows import add_shadow

from Common import GFX_PATH, SND_PATH
from VecSprite import VecSprite

class Ship (VecSprite):
    """
    Ships are specialized vectorized sprites that adds damage and strafing
    abilities to the "regular" sprites. As such, it is the basis for both the
    player and all the enemies in the game.
    """

    explosionsound = join(SND_PATH,"explosion.wav")
    hitsound = join(SND_PATH,"hit.wav")

    # Init_position, init_direction an size are all pairs
    def __init__(self, common, init_pos, init_dir, img_file, speed):
        self.common = (self.surface, self.res, self.options) = common
        img = self.res.get_graphics(img_file)

        # Initialize the VecSprite superclass
        super(Ship, self).__init__(init_pos, init_dir, img, speed)

        # Movement. Ships can strafe, as opposed to any object
        self.__strafe = Vec2d(self.direction).rotated(0)
        self.__strafe_angle = 0

        # A ship may be headed automatically towards some target
        self.__target = None

        # When a ship is hit, it should flash (with yellow)
        self.__hit = False

        # The hitsurface is an overlay drawn when the ship is hit
        self.__hitsurface = self.image.copy()
        self.calculate_hitsurface()
        
        # Ship statistics
        self.__damage = 0
        self.__max_damage = 3
        # Used when ships explode
        self.__exploding = False
        self.__explode_counter = 1

    def update(self, *_):
        """
        Overrides default update by adding code for stopping at a specific
        target, if such a target is set. 
        """
        self.__hit = False
        super(Ship, self).update()
        if not self.__exploding and self.__target != None:
            (x, y) = self.get_position()
            (x_t, y_t) = self.__target
            # We have (sort of) reached our target, so stop!
            if abs(x-x_t) < 3 and abs(y-y_t) < 3: 
                self.speed = 0
                self.__target = None
    
    def move(self):
        """
        Overrides default move by using strafe instead of direction to calculate
        the displacement. 
        """
        displacement = Vec2d(
            self.__strafe.x * self.speed,
            self.__strafe.y * self.speed)
        self.position += displacement
        self.rect.center = self.get_position()
        
    def calculate_hitsurface(self):
        """
        Basically, the hitsurface is calculated by painting every pixel in the
        sprite, which is set in a generated mask, to light blue.

        The existing mask attribute is not used, since it might change due to
        wanting collision detection to only look at a specific hitbox or so
        """
        self.__hitsurface = self.image.copy()
        self.__hitsurface.set_alpha(128) # 50 % transparent
        mask = pygame.mask.from_surface(self.image)
        for x in range(self.image.get_width()):
            for y in range(self.image.get_height()):
                if mask.get_at((x, y)) != 0:
                    # 2A7FFF - Light blue, 50 % transparent
                    color = (42, 127, 255, 128) 
                    self.__hitsurface.set_at((x, y), color)

    def set_target(self, (x, y)):
        """
        Setting a target makes the ship autopilot towards that target. Setting a
        target only affects the strafe vector, so a ship with a target does not
        change its direction (or angle, if you will). 
        """
        (x_0, y_0) = self.get_position()
        self.__strafe = Vec2d(x-x_0, y-y_0).normalized()
        self.__target = (x, y)

    def has_target(self):
        """
        If the target parameter were written in Haskell it would be Maybe Vec2d
        """
        return self.__target != None

    def blit(self):
        """
        Lets the ship draw itself. This overrides the default blit by drawing an
        animation for when the ship explodes, and by adding a drop shadow to the
        ship before blitting. Also, if the ship was hit, draw the hitsurface
        overlay.
        """
        # Animate an explosion
        if self.__exploding:
            # TODO: Use an image/animation instead
            if self.__explode_counter < 16:
                width = self.get_width()
                radius = int(width / 2.0 / (16.0 - self.__explode_counter))
                pos = map(int, self.get_position())
                color = (255, 0, 0) # Red
                pygame.draw.circle(self.surface, color, pos, radius)
                self.__explode_counter += 2
            else: 
                self.kill()
        else:
            # Add a shadow to the image, then blit it in its original position
            simage = add_shadow(self.image, (10, 10))
            self.surface.blit(simage, self.rect)

            if self.__hit:
                self.surface.blit(self.__hitsurface, self.rect)

    #
    # Ship damage
    #
    def get_damage(self):
        return self.__damage    
    
    def add_damage(self, damage):
        """
        The ship holds control over its damage, so when it gets too high, it
        explodes. 
        """
        self.__hit = True
        self.__damage += damage
        if self.__damage >= self.__max_damage:
            self.__exploding = True
            # Play a sound for explosion, but only if sound is enabled
            if self.options.sound:
                sound = self.res.get_sound(Ship.explosionsound)
                sound.set_volume(0.2)
                sound.play()
    
    def reset_damage(self):
        """
        In no reasonable universe can you both explode and have 0 damage, so
        resetting the damage also unsets the explosion flag
        """
        self.__damage = 0
        self.__exploding = False
    
    def get_max_damage(self):
        return self.__max_damage

    def set_max_damage(self, damage):
        """
        The maximum damage is private but accessible through the property, since
        it is usually desirable to change it when different ships have different
        thresholds until they explode (like bosses)
        """
        self.__max_damage = damage
    max_damage = property(get_max_damage, set_max_damage)

    def is_exploding(self):
        return self.__exploding

    #
    # Ship direction and strafing. Some overrides here since not every moving
    # sprite has the ability to strafe.
    #

    def set_direction(self, (x, y)):
        """
        Override, due to strafing abilities
        Setting the direction does not affect the relative strafing angle
        """
        super(Ship, self).set_direction((x, y))
        self.set_strafe(self.__strafe_angle)
        self.calculate_hitsurface()

    def get_strafe(self):
        return self.__strafe
    
    def set_strafe(self, angle_degrees):
        """
        Set a strafe vector that is relative to the ship angle with given amount
        of degrees. 90 or -90 here will strafe to the sides, for instance
        """
        self.__strafe = Vec2d(self.direction).rotated(angle_degrees)
        self.__strafe_angle = angle_degrees
    strafe = property(get_strafe, set_strafe)

    def set_strafe_composite(self, (x, y)):
        """
        If you neccessarily have to set a specifik strafe vector, that's fine
        too. The vector will be normalized, however.
        """
        self.__strafe = Vec2d(x, y).normalized()
 
    def mirror_direction_y(self):
        """
        Override: mirroring the direction should also mirror the strafe vector
        """
        super(Ship, self).mirror_direction_y()
        self.__strafe.y *= -1
        self.calculate_hitsurface()

    def mirror_direction_x(self):
        """
        Override: mirroring the direction should also mirror the strafe vector
        """
        super(Ship, self).mirror_direction_x()
        self.__strafe.x *= -1
        self.calculate_hitsurface()


class Animation:
    """
    Animation class is a wrapper around a number of images that we cycle through
    timed by a given interval.
    """

    def __init__(self, images, interval):
        self.__images = images
        self.__active = 0
        self.__interval = interval
        self.__counter = 0

    def update(self):
        """
        If the counter is matching the interval, we change to the next image in
        our animation.
        """
        self.__counter += 1
        if self.__counter % self.__interval == 0:
            self.__active = (self.__active + 1) % len(self.__images)

    def get_image(self):
        """
        Returns the currently active image in the collection
        """
        return self.__images[self.__active]
