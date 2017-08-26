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

from glob import glob
from os.path import isfile, join

from Common import GFX_PATH, SND_PATH
from pygame.image import load
from pygame.mixer import Sound

class Resources:
    """
    This class handles loading and access to graphics and audio resources.
    it should be initialized just after pygame is initialized. It cannot be
    used before pygame is initialized, since it uses pygame functions.

    NOTE: Don't use this class to load music, since the music module in pygame
          handles music by streaming as opposed to sound effects
    """

    def __init__(self):
        """ Initialize the cache directories, empty at start """
        self.__graphics = {}
        self.__sound = {}

    def preload_all(self):
        """
        preload_all should be used before the game starts to improve
        performance, by caching all sounds in the sound directory and all
        graphics in the graphics directory. Note however, as with the rest of
        this module, that both pygame and its mixer has to be initialized for
        this to work.
        """

        snd = glob(join(SND_PATH,"*.wav"))
        for sound in snd:
            self.get_sound(sound)
        gfx = glob(join(GFX_PATH,"*.png"))
        for image in gfx:
            self.get_graphics(image)

    def get_graphics(self, key):
        """
        If the key is already loaded into the cache, return it. If not, load the
        image, convert its alpha channel and insert it into the cache, then
        return it.
        If the file corresponding to the key does not exist an IOError is raised
        """
        if key not in self.__graphics:
            if isfile(key):
                self.__graphics[key] = load(key).convert_alpha()
            else:
                raise IOError("File doesn't exist")
        return self.__graphics[key]

    def get_sound(self, key):
        """
        If the key is already loaded into the cache, return it. If not, load the
        sound, insert it into the cache, then return it.
        If the file corresponding to the key does not exist an IOError is raised
        """
        if key not in self.__sound:
            if isfile(key):
                self.__sound[key] = Sound(key)
            else:
                raise IOError("File doesn't exist")
        return self.__sound[key]

