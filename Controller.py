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

# Controller.py
#
# This module handles menus and anything that isn't exactly gameplay. It also
# loads levels.
#

from os.path import join

import pygame
from pygame.locals import KEYDOWN, QUIT, K_y, K_n

from Graphics import Graphics
from Logic import GameLogic

from Common import MP3_PATH
from Common import CLEARED, DIED, ABORTED
from Resources import Resources
from Options import Options
from Level import Level, level_convert


class Controller:
    
    #
    #
    def __init__(self):
        """
        pygame.init() does initialize parts of the sound, but according to the
        documentation for the mixer module, safest way is to do mixer.pre_init,
        then pygame.init and then mixer.init. The controller also makes sure any
        resources needed in the game are preloaded.
        """
        self.__options = Options.load()
        self.__resources = Resources()
        pygame.mixer.pre_init(frequency = 44100, buffer = 2048) 
        pygame.init()
        pygame.mixer.init(frequency = 44100, buffer = 2048)
        self.__graphics = Graphics(self.__resources, self.__options)
        # Load all graphics and sound effects before the game is started
        self.__resources.preload_all()
        self.__logic = None

    def main(self):
        self.main_menu()

    def play_game(self):
        """
        Initialize the game logic and handle whatever the game logic returns
        from a run of the game. 
        """
        self.__logic = GameLogic(self.__graphics, self.__resources, 
                                 self.__options)
        self.__logic.add_player()
        levels = level_convert()
        status = CLEARED
        #
        # Play the levels
        #
        for i in range(len(levels)):
            lev = levels[i]
            # Background music
            # TODO: Different music for different levels
            if self.__options.music:
                pygame.mixer.music.load(join(MP3_PATH,"cruising.mp3"))
                pygame.mixer.music.set_volume(0.8)
                pygame.mixer.music.play()

            # Prepare the level
            self.__logic.clear()
            self.__graphics.reset_distance()
            self.__graphics.set_scroll(5)
            self.__logic.set_level(lev)
            
            status = self.__logic.game_loop()
            if status != CLEARED:
                break
            # Last level cleared = game cleared!
            if i != len(levels)-1:
                self.level_cleared()

        # Turn off the music, since game is obviously over
        pygame.mixer.music.stop()

        #
        # Depending on how the game went, show some information, or not.
        #
        if status == CLEARED:
            self.game_cleared()
            self.main_menu()
        elif status == DIED:
            self.game_over()
        elif status == ABORTED:
            self.main_menu()
        else:
            self.quit()

#
# Menus below
#

    def main_menu(self):
        o = self.__options
        entries = ["Start game", "Instructions", "Options", "Quit"]
        funs = [lambda _: self.play_game(), lambda _: self.instructions()
               ,lambda _: self.options(), lambda _: self.quit()]
        active = 0
        self.__graphics.main_menu(entries, active)
        keys = [o.up, o.down, o.confirm]
        kpress = wait_for_key(keys)
        while kpress in [o.up, o.down]:
            if kpress == o.up and active > 0:
                active -= 1
            elif kpress == o.down and active < len(entries) - 1:
                active += 1
            self.__graphics.main_menu(entries, active)
            kpress = wait_for_key(keys)
        if kpress == o.confirm:
            f = funs[active]
            f(0)
        else:
            self.quit()

    # TODO: Collect and print stats from the level, too
    def level_cleared(self):
        self.__graphics.paint_level_cleared()
        anykey()

    # TODO: Highscores and stuff
    def game_cleared(self):
        self.__graphics.paint_game_cleared()
        anykey()

    # Shows an options menu and allows setting various game parameters
    def options(self, active = 0):
        o = self.__options
        key_opts = [ ("Left:", o.left), ("Down:", o.down), ("Up:", o.up)
                   , ("Right:", o.right), ("Fire:", o.fire)
                   , ("Abort:", o.abort), ("Confirm:", o.confirm)
                   ]
        bool_opts = [ ("Fullscreen: ", o.fullscreen), ("Music: ", o.music)
                    , ("Sound effects: ", o.sfx)
                    ]
        self.__graphics.paint_options(key_opts, bool_opts, active, False)
        keys = [o.up, o.down, o.confirm, o.abort]
        kpress = wait_for_key(keys)
        while kpress in [o.up, o.down]:
            if kpress == o.up and active > 0:
                active -= 1
            elif kpress == o.down and active < 9:
                active += 1
            self.__graphics.paint_options(key_opts, bool_opts, active, False)
            kpress = wait_for_key(keys)

        if kpress == o.confirm:
            # Key options
            if active < len(key_opts):
                # Paint selection and wait for input
                self.__graphics.paint_options(key_opts, bool_opts, active, True)
                key = anykey()
                # Only keys that are not already assigned may be chosen
                if key not in self.__options.get_all_keys():
                    self.__options.set_index(active, key)
                    self.__options.save()
            
            # Boolean options, just reverse the value
            else:
                fs = self.__options.fullscreen
                val = self.__options.get_index(active)
                self.__options.set_index(active, not val)
                # If the fullscreen option was changed, reinitialize the
                # graphics
                if fs != self.__options.fullscreen:
                    pygame.display.quit()
                    self.__graphics = Graphics(self.__resources, self.__options)
            self.options(active)
        elif kpress == o.abort:
            self.main_menu()
        else: # event == QUIT
            self.quit()

    # TODO: A describing text about the gameplay
    def instructions(self):
        opts = self.__options
        enemies = all_ships()
        funs = [lambda _: self.__graphics.paint_instructions_keys(),
                lambda _: self.__graphics.paint_instructions_ship(),
                lambda _: self.__graphics.paint_instructions_enemies(enemies) ]
        active = 0
        kpress = None 
        while active >= 0 and active <= 2 and kpress != QUIT:
            screen = funs[active]
            screen(0)
            kpress = wait_for_key([opts.left, opts.right])
            if kpress == opts.left: 
                active -= 1
            elif kpress == opts.right:
                active += 1
        if kpress == QUIT:
            self.quit()
        else:
            self.main_menu()

    def game_over(self):
        self.__graphics.game_over()
        # There is an option of restarting without going through the main menu
        if yn_key():
            self.play_game()
        else:
            self.main_menu()

    def quit(self):
        self.__options.save()
        pygame.mixer.quit()
        pygame.quit()

# Waits for keystroke. 
# Returns True if y is pressed, False if n is pressed.
# Loops if anything else is pressed
def yn_key():
    k = wait_for_key([K_y, K_n])
    return k == K_y

# General function for key handling
def wait_for_key(keys):
    klist = pygame.event.get([KEYDOWN, QUIT])
    while True:
        for event in klist:
            if event.type == QUIT: 
                return QUIT
            elif event.key in keys: 
                return event.key
        klist = pygame.event.get([KEYDOWN, QUIT])

# Waits for any keystroke to be pressed. Uses polling :/
def anykey():
    keys = pygame.event.get(KEYDOWN)
    while len(keys) == 0:
        keys = pygame.event.get(KEYDOWN)
    # Return the first key we found
    return keys[0].key

