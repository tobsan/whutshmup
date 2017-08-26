# encoding=UTF-8
#
# (c) Tobias Olausson (tobsan@tobsan.se) 2013
# 
# This file is part of whutshmup
#
# whutshmup is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# whutshmup is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with 
# whutshmup. If not, see <http://www.gnu.org/licenses/>.
#

import pickle
from pygame.locals import K_LEFT, K_DOWN, K_UP, K_RIGHT, K_SPACE
from pygame.locals import K_ESCAPE, K_RETURN

class Options(object):
    
    optionsfile = "options.dat"
    @staticmethod
    def load():
        try:
            f = open(Options.optionsfile, "rb")
            opts = pickle.load(f)
            f.close()
            return opts
        except IOError:
            return Options()

    def __init__(self):
        # Default keys
        self.__left = K_LEFT
        self.__down = K_DOWN
        self.__up = K_UP
        self.__right = K_RIGHT
        self.__fire = K_SPACE
        self.__abort = K_ESCAPE
        self.__confirm = K_RETURN

        # Boolean data
        self.__fullscreen = False
        self.__music = True
        self.__sfx = True

        # TODO: Customizeable. How to do with ships etc? Scaling?
        self.__resolution = (800, 600) 

    def set_index(self, index, value):
        fs = [lambda v: self.set_left(v), lambda v: self.set_down(v)
             ,lambda v: self.set_up(v), lambda v: self.set_right(v)
             ,lambda v: self.set_fire(v), lambda v: self.set_abort(v)
             ,lambda v: self.set_confirm(v), lambda v: self.set_fullscreen(v)
             ,lambda v: self.set_music(v), lambda v: self.set_sfx(v)]
        fun = fs[index]
        fun(value)

    def get_index(self, index):
        vals = [self.left, self.down, self.up, self.right, self.fire,
                self.abort, self.confirm, self.fullscreen, self.music, self.sfx]
        return vals[index]

    def get_all_keys(self):
        return [self.left, self.down, self.up, self.right,
                self.fire, self.abort, self.confirm]

    def get_left(self):
        return self.__left

    def set_left(self, key):
        self.__left = key
    left = property(get_left, set_left)

    def get_down(self):
        return self.__down

    def set_down(self, key):
        self.__down = key
    down = property(get_down, set_down)

    def get_up(self):
        return self.__up

    def set_up(self, key):
        self.__up = key
    up = property(get_up, set_up)

    def get_right(self):
        return self.__right

    def set_right(self, key):
        self.__right = key
    right = property(get_right, set_right)

    def get_fire(self):
        return self.__fire
    
    def set_fire(self, key):
        self.__fire = key
    fire = property(get_fire, set_fire)

    def get_abort(self):
        return self.__abort

    def set_abort(self, key):
        self.__abort = key
    abort = property(get_abort, set_abort)

    def get_confirm(self):
        return self.__confirm
    
    def set_confirm(self, key):
        self.__confirm = key
    confirm = property(get_confirm, set_confirm)

    def get_fullscreen(self):
        return self.__fullscreen

    def set_fullscreen(self, value):
        self.__fullscreen = value
    fullscreen = property(get_fullscreen, set_fullscreen)

    def get_music(self):
        return self.__music
    
    def set_music(self, value):
        self.__music = value
    music = property(get_music, set_music)

    def get_sfx(self):
        return self.__sfx
    
    def set_sfx(self, value):
        self.__sfx = value
    sfx = property(get_sfx, set_sfx)
    sound = property(get_sfx, set_sfx)

    def save(self):
        f = open(Options.optionsfile, "wb")
        pickle.dump(self, f)
        f.close()

