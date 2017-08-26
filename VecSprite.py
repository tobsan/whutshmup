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

import pygame
from pygame.sprite import Sprite
from pygame.rect import Rect

from Vec2d import Vec2d

class VecSprite(Sprite):
    """
    Sprites with two vectors - direction and position
    
    The sprite holds an image with width and height which is rotated
    to match the direction of this VecSprite. This class serves as the base
    class for more or less anything that moves.

    Class also includes getters and setters for some attributes that should not
    be set without something else happening at the same time, so use with
    caution
    """

    def __init__(self, init_pos, init_dir, image, speed):
        # Initialize the sprite
        super(VecSprite, self).__init__()

        # Set position, direction and speed
        self.position = Vec2d(init_pos)
        self.direction = Vec2d(init_dir).normalized()
        self.__speed = speed

        # Load the image and rotate it 
        self.__base_image = image 
        # Rotate the image CLOCKWISE, hence the negative angle
        self.image = pygame.transform.rotate(self.__base_image,
                                             -self.direction.angle)
        self.__image_w, self.__image_h = self.image.get_size() # Rotated size

        # Rect attribute
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = Rect((0, 0), (self.__image_w, self.__image_h))
        self.rect.center = (self.position.x, self.position.y)

        # Misc
        self.__counter = 0

    # General updating procedure
    # 
    #
    def update(self, *_):
        """
        Updates this sprite by calling move() and updating a counter.

        Separated update() and move() to make overriding easier, since one may
        want to override the moving procedure but most likely not the updating.
        """
        self.move()
        self.__counter += 1

    def move(self):
        """
        Moves the sprite according to its direction and speed, and also updates
        the rect to reflect this move.
        """
        displacement = Vec2d(
            self.direction.x * self.speed,
            self.direction.y * self.speed)
        self.position += displacement
        self.rect.center = self.position.x, self.position.y
    
    def __recalc(self):
        """
        Recalculation of image properties and the corresponding rect. Used
        whenever one changes direction or image.
        """
        angle = self.direction.angle
        self.image = pygame.transform.rotate(self.__base_image, -angle) 
        self.__image_w, self.__image_h = self.image.get_size()
        self.rect.size = self.__image_w, self.__image_h
        self.rect.center = self.position.x, self.position.y

    def get_counter(self):
        """
        The counter is updated on each call to update(). Therefore, if you
        override update for whatever reason, remember to call super().update
        """
        return self.__counter
    counter = property(get_counter)

    def set_image(self, image):
        """
        This method should be used to manipulate which image is used for the
        sprite. Don't set the image attribute directly.
        """
        self.__base_image = image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.__recalc()

    def get_angle(self):
        """
        The direction is represented by a two-dimensional vector, but sometimes
        it is interesting to know the vectors angle (for example, if one want to
        rotate it).
        """
        return self.direction.angle

    def get_direction(self):
        """
        The direction is a vector, but one should not mess with that directly,
        so we provide access only to the two vector components.
        """
        return self.direction.x, self.direction.y

    def set_direction(self, (x, y)):
        """
        The point of not letting someone mess with the vector directly is that
        when direction is set, the image this sprite represents has to be
        rotated and some calculations have to be made.
        """
        self.direction = Vec2d(x, y).normalized()
        self.__recalc()

    def mirror_direction_y(self):
        """
        Mirrors the sprites y component (turns it upside-down)
        """
        self.direction.y *= -1
        self.__recalc()

    def mirror_direction_x(self):
        """
        Mirrors the sprites x component (mirrors it)
        """
        self.direction.x *= -1
        self.__recalc()

    def get_position(self):
        """
        The position is also a vector, and no messing with it (but you may have
        a look at the coordinates for x and y
        """
        return self.position.x, self.position.y

    def set_position(self, (x, y)):
        """
        Just like with the direction, setting the position has effects for other
        parts of the vector. 
        """
        self.position = Vec2d(x, y)
        self.rect.center = x, y

    def get_width(self):
        """
        The width is the same as the width of the rotated image
        """
        return self.__image_w

    def get_height(self):
        """
        The height is the same as the height of the rotated image
        """
        return self.__image_h
    
    def get_speed(self):
        return self.__speed

    def set_speed(self, speed):
        """
        The reason speed is not a public attribute is that it should be possible
        to override the speed-setting method. That can be desirable if one want
        to emulate acceleration up to a speed.
        """
        self.__speed = speed
    speed = property(get_speed, set_speed)
