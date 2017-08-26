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

from pygame.draw import circle
from pygame.surface import Surface
from pygame.mask import Mask

from Common import GFX_PATH, SND_PATH
from VecSprite import VecSprite

#
# Shorthands for certain common shot types
#
def Smallshot(common, position, direction, speed, sound):
    return Shot(common, Shot.smallshot, position, direction, 
                speed, Shot.smalldamage, sound)
def Mediumshot(common, position, direction, speed):
    return Shot(common, Shot.mediumshot, position, direction, 
                speed, Shot.mediumdamage, Shot.mediumsound)
def Snipeshot(common, position, direction):
    return Smallshot(common, position, direction, 50, Shot.snipesound)
    

# A regular shot that travels in a straight line
class Shot(VecSprite):
    """
    A shot is a sprite that has an associated value for damage, which it will
    inflict upon hitting something.
    """
    
    smallshot = join(GFX_PATH, "shot-8.png")
    mediumshot = join(GFX_PATH, "shot-16.png")
    largeshot = join(GFX_PATH, "shot-32.png")
    playershot = join(GFX_PATH, "playershot.png")
    smalldamage = 1
    mediumdamage = 2
    largedamage = 5
    mediumsound = join(SND_PATH, "mediumshot.wav")
    snipesound = join(SND_PATH, "snipershot.wav")
    playersound = join(SND_PATH, "playershot.wav")

    def __init__(self, common, image, init_pos, init_dir, speed, damage, sound):
        self.common = (self.surface, self.res, self.options) = common
        img = self.res.get_graphics(image)
        super(Shot, self).__init__(init_pos, init_dir, img, speed)

        # Create and play the sound, we don't need to keep it
        if sound != None and self.options.sound:
            sound = self.res.get_sound(sound)
            sound.set_volume(0.4)
            sound.play()

        self.__damage = damage

    def blit(self):
        self.surface.blit(self.image, self.rect)

    def get_damage(self):
        return self.__damage

class ClusterShot(Shot):
    """
    ClusterShots explodes into several regular shots after a given timeout
    """
    
    clusterfile = Shot.largeshot
    clusterdamage = 5
    clustersound = join(SND_PATH, "clustershot.wav")

    def __init__(self, common, init_pos, init_dir, speed, timeout, clusters):
        super(ClusterShot, self).__init__(common, ClusterShot.clusterfile, 
                                          init_pos, init_dir, speed, 
                                          Shot.largedamage, 
                                          ClusterShot.clustersound)
        self.__timeout = timeout
        self.__clusters = clusters

    def update(self, *_):
        """
        Override from regular shots. After timeout, create as many new smaller
        and faster shots as needed, and add them to whatever sprite group the
        cluster shot belonged to.
        """
        super(ClusterShot, self).update()
        if self.counter >= self.__timeout:
            cpos = self.get_position()
            for i in range(self.__clusters):
                # Angle calculation magic. 360 degree coverage
                angle = 90 - 180 / self.__clusters * (i-1)
                if i % 2 == 0: 
                    angle -= 180
                newdir = self.direction.rotated(angle)
                shot = Shot(self.common, Shot.smallshot, cpos, newdir, 
                            self.speed * 2, Shot.smalldamage, None)
                for group in self.groups():
                    group.add(shot)
            self.kill() # The original shot should die

# TODO: Use mines in the game
class Mine(Shot):
    """
    Mines are shots that creates a blast after a timeout, damaging anything
    within that blast zone.
    """
    minefile = join(GFX_PATH, "mine.png")

    def __init__(self, common, init_pos, init_dir, speed, timeout, radius):
        super(Mine, self).__init__(common, Mine.minefile, init_pos, init_dir, 
                                   speed, Shot.largedamage)
        self.__timeout = timeout
        self.__radius = radius

    def update(self, *_):
        if self.counter < self.__timeout:
            super(Mine, self).update()
        elif self.counter - self.__timeout > self.__radius:
            self.kill()

    # TODO: Find a neater way to do this
    def blit(self):
        """
        If the shot should explode: Paint a blast! Otherwise, just do what any
        other shot would do.
        """
        if self.counter >= self.__timeout:
            size = self.__timeout - self.counter
            rad = self.__radius - size
            pos = map(int, self.get_position())
            rect = circle(self.surface, (255, 102, 0), pos, rad)
            self.rect = rect
            self.image = Surface((rect.width, rect.height))
            self.mask = Mask((rect.width, rect.height)) 
            self.mask.fill() # Everything in this mask is set
        else:
            super(Mine, self).blit()


