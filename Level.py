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
import itertools

from Common import GFX_PATH
from VecSprite import VecSprite
from Alien import Scout, Alien, Bomber, Chopper, Sniper, Kamikaze
from Alien import FirstBoss, SecondBoss, all_ships

# Level :: [(Int, [LevelItem])]
# LevelItem :: Dict

# TODO: Take over almost all functionality from check_level in Logic.py

class Level(object):
    
    def __init__(self, items):
        self.__items = items

    # TODO: Include enemies
    def get(self, distance):
        def keep_barrier(x, dist):
            if x[0] > dist or is_barrier(x):
                return True
            return False

        def is_barrier(x):
            return x[1][0]['item'] == Barrier

        # We only need the actual items, so strip the distance
        todo = map(lambda x: x[1], filter(lambda x: x[0] <= distance, self.__items))
        self.__items = filter(lambda x: keep_barrier(x, distance), self.__items)
        return todo

    def scroll(self, distance):
        self.__items = [(pos + distance, i) for (pos, i) in self.__items]

    def pop(self, index):
        self.__items.pop(index)

    # Override
    def __len__(self):
        return len(self.__items)

def level_convert():
    levs = get_levels()
    ret = []
    for level in levs:
        ret.append(Level(level))
    return ret

# Note: Barriers can't have the same number as anything else
# TODO: Enemies that move in patterns
# TODO: A reasonable way to save/load levels
# TODO: A level design language. Looping etc should be possible
# TODO: Levels as functions?
# TODO: Why does 45 degrees strafe become 90 degrees?
def get_levels():
    return  [ # Start Level 1
            [(100, [{ 'item' : Scout, 'pos' : (100, -100), 'speed' : 10 }
                   ,{ 'item' : Scout, 'pos' : (200, -100), 'speed' : 10 }
                   ])
           , (400, [{ 'item' : Scout, 'pos' : (500, -100), 'speed' : 10 }
                   ,{ 'item' : Scout, 'pos' : (400, -100), 'speed' : 10 }
                   ])
           , (700, [{ 'item' : Scout, 'pos' : (250, -100), 'speed' : 10 }
                   ,{ 'item' : Scout, 'pos' : (350, -100), 'speed' : 10 }
                   ])
           , (700, [{ 'item' : Item, 'type' : Item.POWER, 'pos' : (300, -200)
                    , 'value' : 2, 'speed' : 10 } ])
           , (725, [{ 'item' : Barrier }])
           , (750, [{ 'item' : Bomber, 'pos' : (400, -50), 'target' : (400,150) }])
           , (750, [{ 'item' : Chopper, 'pos' : (100, -50), 'speed' : 9 },
                     { 'item' : Chopper, 'pos' : (200, -50), 'speed' : 9 },
                     { 'item' : Chopper, 'pos' : (100, -250), 'speed' : 9 },
                     { 'item' : Chopper, 'pos' : (200, -250), 'speed' : 9 },
                   ])
           , (1500, [{ 'item' : Bomber, 'pos' : (100,-50), 'target' : (100, 150) },
                     { 'item' : Chopper, 'pos' : (400, -50), 'speed' : 9 },
                     { 'item' : Chopper, 'pos' : (500, -50), 'speed' : 9 },
                     { 'item' : Chopper, 'pos' : (400, -250), 'speed' : 9 },
                     { 'item' : Chopper, 'pos' : (500, -250), 'speed' : 9 },
                    ])
           , (1550, [{ 'item' : Barrier }])
           , (1700, [{ 'item' : Alien, 'pos' : (400,-50), 'strafe' : 45 }
                    ,{ 'item' : Alien, 'pos' : (300,-50), 'strafe' : 45 }
                    ,{ 'item' : Alien, 'pos' : (200,-50), 'strafe' : -45 }
                    ,{ 'item' : Alien, 'pos' : (300,-50), 'strafe' : -45 }
                    ])
           , (2200, [{ 'item' : Alien, 'pos' : (300, -50), 'target' : (100, 100)}
                    ,{ 'item' : Alien, 'pos' : (300, -50), 'target' : (200, 100)}
                    ,{ 'item' : Alien, 'pos' : (300, -50), 'target' : (400, 100)}
                    ,{ 'item' : Alien, 'pos' : (300, -50), 'target' : (500, 100)}
                    ])
           , (2205, [{ 'item' : Barrier }])
           , (2400, [{ 'item' : Bomber, 'pos' : (300,-100), 'target' : (300,200) }
                    ,{ 'item' : Kamikaze, 'pos' : (0,-100), 'speed' : 12 }
                    ,{ 'item' : Kamikaze, 'pos' : (600,-100), 'speed' : 12}
                    ,{ 'item' : Alien, 'pos' : (300, -50), 'target' : (100, 100)}
                    ,{ 'item' : Alien, 'pos' : (300, -50), 'target' : (500, 100)}
                    ])
           , (2450, [{ 'item' : Barrier }]) 
           , (2800, [{ 'item' : FirstBoss, 'pos' : (300,-100) }]) 
            ] # End Level 1
              # Start Level 2
           ,[ (100, [{ 'item' : Bomber, 'pos' : (300,-100), 'target' : (200, 200) }
                    ,{ 'item' : Bomber, 'pos' : (300,-100), 'target' : (400, 200) }
                    ])
               ,(120, [{ 'item' : Barrier }]) 
               ,(1000, [{ 'item' : SecondBoss, 'pos' : (300, -100) } ])
            ] # End Level 2
            ]

# TODO: Find a better place for this
class Barrier(VecSprite):
    """
    The barrier is the most ill-placed class in this whole game project
    """
    blehe = "blaha"

class Item(VecSprite):
    """
    Items are objects that the player can pick up that has some effect on the
    gaming experience. Currently, items can be life or power-ups. Items are
    contained inside crates, but the crates break when shot at, revealing their
    contents.
    """
    
    crateimg = join(GFX_PATH,"crate.png")
    heartimg = join(GFX_PATH,"heart.png")
    levelimg = join(GFX_PATH,"powerup.png")

    # Item types
    LIFE = 1
    POWER = 2
    MINE = 3 # Not used atm
    types = [LIFE, POWER, MINE]

    def __init__(self, common, init_pos, init_dir, speed, item_type, value):
        (self.surface, self.res, self.options) = common
        img = self.res.get_graphics(Item.crateimg)
        super(Item, self).__init__(init_pos, init_dir, img, speed)

        self.boxed = True
        self.boxcounter = 0
        self.__type = item_type
        self.__value = value

        if item_type == Item.LIFE:
            self.__itemimage = self.res.get_graphics(Item.heartimg)
        elif item_type == Item.POWER:
            self.__itemimage = self.res.get_graphics(Item.levelimg)

    def blit(self):
        """
        Paint the item. If it is currently unboxing, draw a filled circle
        similar to the explosion animation. Otherwise, just blit the image.
        """
        if not self.boxed and self.boxcounter < 16:
            radius = int(self.get_width() / 2 / (16.0 - self.boxcounter))
            (x, y) = self.get_position()
            color = (255, 0, 0) # Red
            pygame.draw.circle(self.surface, color, (int(x), int(y)), radius)
            self.boxcounter += 3
        else:
            self.surface.blit(self.image, self.rect)

    def get_type(self):
        return self.__type

    def get_value(self):
        return self.__value

    def is_boxed(self):
        return self.boxed

    def unbox(self):
        self.boxed = False
        self.set_image(self.__itemimage)

