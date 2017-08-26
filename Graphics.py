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
from pygame.font import SysFont
from pygame.rect import Rect

from Common import WINDOW_SIZE, GAME_WIDTH, GFX_PATH

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY  = (64, 64, 64)

class Graphics:
    """
    This class has two purposes. It keeps track of the window and its surfaces,
    and it is used to draw stuff onto said surfaces.
    """

    def __init__(self, resources, options):
        self.__resources = resources
        
        args = pygame.DOUBLEBUF 
        if options.fullscreen:
            args |= pygame.FULLSCREEN
        self.__window = pygame.display.set_mode(WINDOW_SIZE, args)
        pygame.display.set_caption("Whutshmup?!")

        side_width = (WINDOW_SIZE[0] - GAME_WIDTH) / 2
        self.__game_rect = Rect((side_width, 0), (GAME_WIDTH, WINDOW_SIZE[1]))
        self.__left_rect = Rect((0, 0), (side_width, WINDOW_SIZE[1])),
        self.__right_rect = Rect((GAME_WIDTH + side_width, 0), 
                                 (side_width, WINDOW_SIZE[1])
                                )
        self.surface = self.__window.subsurface(self.__game_rect)
        self.left = self.__window.subsurface(self.__left_rect)
        self.right = self.__window.subsurface(self.__right_rect)

        self.__scrolling_speed = 0
        self.__current_scroll = 0
        self.__total_distance = 0

        # Fonts
        self.__large = SysFont("Monospace", 40, True)
        self.__small = SysFont("Monospace", 20, True)
        self.__smaller = SysFont("Monospace", 12, True)

        # TODO: Different backgrounds for different levels
        bgimg = join(GFX_PATH, "BG-bluepattern.png")
        self.__bg_img = self.__resources.get_graphics(bgimg)
        self.paint_bg()
    
    def get_width(self):
        return self.__game_rect.width
    
    def get_height(self):
        return self.__game_rect.height
    
    def get_total_distance(self):
        return self.__total_distance

    def reset_distance(self):
        self.__total_distance = 0
        self.__current_scroll = 0

    def set_scroll(self, speed):
        self.__scrolling_speed = speed

    def get_scroll(self):
        return self.__scrolling_speed

    def scroll(self):
        self.__current_scroll += self.__scrolling_speed
        self.__current_scroll %= 1200
        self.__total_distance += self.__scrolling_speed

    def paint_level_cleared(self):
        """
        A greeting painted as a semi-transparent overlay on the game screen
        """
        trans_win = self.__window.copy()
        trans_win.set_alpha(128)
        trans_win.fill(BLACK)
        self.__window.blit(trans_win, (0, 0))

        clear = self.__large.render("Level cleared!", True, WHITE)
        anykey = self.__small.render("Press any key to continue", True, WHITE)
        self.__window.blit(clear, (250, 300))
        self.__window.blit(anykey, (250, 350))
        flip()

    def paint_game_cleared(self):
        self.__window.fill(BLACK)
        goodjob = self.__large.render("Game cleared!", True, WHITE)
        key = self.__small.render("Congratulations! Press any key to continue", 
                                  True, WHITE)
        self.__window.blit(goodjob, (250, 300))
        self.__window.blit(key, (250, 350))
        flip()
        
    def paint_bg(self):
        """
        The background is a 600x1200px image that is tiled when the game
        scrolls. This currently works for that size, but should be generalized
        to fit any images that can be tiled.
        """
        self.__window.fill(GRAY)
        self.surface.fill(BLACK)
        srect = Rect(0, 1200 - self.__current_scroll, 600, 600)
        self.surface.blit(self.__bg_img, (0, 0), srect)
        self.surface.blit(self.__bg_img, (0, self.__current_scroll))

    # Paint the main menu 
    def main_menu(self, labels, active):
        """
        Paints the main menu. Active entries are highlighted in green
        """
        self.__window.fill(BLACK)
        # Main header
        header = self.__large.render("Whutshmup?!", True, WHITE)
        self.__window.blit(header, (250, 300))

        # Then all alternatives
        yinx = 350
        for i in range(len(labels)):
            label = labels[i]
            if i == active:
                value = self.__small.render(label, True, BLACK, GREEN)
                self.__window.blit(value, (250, yinx))
            else:
                value = self.__small.render(label, True, WHITE)
                self.__window.blit(value, (250, yinx))
            yinx += 50

        who = self.__smaller.render("Code by Tobias Olausson 2013", True, WHITE)
        self.__window.blit(who, (10, 10))
        flip()
    
    def paint_instructions_keys(self):
        """
        Paints the instruction screen for what keys are default, together with a
        keyboard with these keys marked.
        """
        keyboard = self.__resources.get_graphics(join(GFX_PATH,"keyboard.png"))
        self.__window.fill(BLACK)
        self.__window.blit(keyboard, (150, 200))
        theader = self.__large.render("Default controls", True, WHITE)
        tesc = self.__small.render("ESC to abort/quit", True, WHITE)
        treturn = self.__small.render("Return to accept/select", True, WHITE)
        tarrows = self.__small.render("Arrows to navigate", True, WHITE)
        tspace = self.__small.render("Space to fire", True, WHITE)
        tback = self.__smaller.render("Left/Right for main menu/next", True, 
                                      WHITE)
        self.__window.blit(theader, (400 - theader.get_width() / 2, 100))
        self.__window.blit(tesc, (140, 175))
        self.__window.blit(treturn, (450, 175))
        self.__window.blit(tarrows, (500, 400))
        self.__window.blit(tspace, (200, 400))
        self.__window.blit(tback, (250, 550))

        flip()

    def paint_instructions_ship(self):
        """
        Paints the instruction screen on how the player's ship works
        """
        ship = self.__resources.get_graphics(join(GFX_PATH,"deltawing.png"))
        hitbox = self.__resources.get_graphics(join(GFX_PATH,"hitbox.png"))
        theader = self.__large.render("The ship", True, WHITE)
        tinfo = self.__small.render("Modeled after JAS 39 Gripen", True, WHITE)
        tbox = self.__small.render("The red ellipse is the hitbox", True, WHITE)
        tback = self.__smaller.render("Left/Right for prev/next", True, WHITE)
        # TODO: Info about larger hitbox for crashing and items

        self.__window.fill(BLACK)
        self.__window.blit(ship, (250, 200))
        self.__window.blit(tinfo, (150, 300))
        self.__window.blit(hitbox, (400, 200))
        self.__window.blit(theader, (400 - theader.get_width() / 2, 100))
        self.__window.blit(tbox, (400, 450))
        self.__window.blit(tback, (250, 550))

        flip()

    def paint_instructions_enemies(self, enemies):
        """
        Paints the instruction screen about the enemies, but not about any of
        the bosses. Enemies are given as a list of tuples on the form (Label,
        Image-path).
        """
        theader = self.__large.render("The enemies", True, WHITE)
        tback = self.__smaller.render("Left/Right for prev/main menu.", True, 
                                      WHITE)
        self.__window.fill(BLACK)
        self.__window.blit(theader, (400 - theader.get_width() / 2, 100))
        self.__window.blit(tback, (250, 550))

        x = y = 175
        for (title, enemy) in enemies:
            enimg = rotate(self.__resources.get_graphics(enemy))
            text = self.__small.render(title, True, WHITE)
            self.__window.blit(text, (x, y))
            self.__window.blit(enimg, (x, y+25))
            x += 150
            if x >= 600:
                y += 200
                x = 175
    
        flip()

    # Active is an index, selected is boolean
    def paint_options(self, key_opts, bool_opts, active, selected):
        """
        Paints the options screen. Key options can be set to any key (except
        those already used) whereas the boolean options can be true or false.
        """
        self.__window.fill(BLACK)

        theader = self.__large.render("Options", True, WHITE)
        self.__window.blit(theader, (400 - theader.get_width() / 2, 100))

        yinx = 200
        # First we take care of the keys
        for i in range(len(key_opts)):
            (label, val) = key_opts[i]
            rlabel = self.__small.render(label, True, WHITE)
            self.__window.blit(rlabel, (250, yinx))
            keyname = pygame.key.name(val)
            if i == active:
                if not selected:
                    rval = self.__small.render(keyname, True, BLACK, GREEN)
                    self.__window.blit(rval, (450, yinx))
            else:
                rval = self.__small.render(keyname, True, WHITE)
                self.__window.blit(rval, (450, yinx))
            yinx += 25
        
        yinx += 25

        # And then we do all the boolean values
        j = len(key_opts)
        for i in range(len(bool_opts)):
            (label, val) = bool_opts[i]
            rlabel = self.__small.render(label, True, WHITE)
            self.__window.blit(rlabel, (250, yinx))
            if i+j == active:
                rval = self.__small.render(str(val), True, BLACK, GREEN)
                self.__window.blit(rval, (450, yinx))
            else: 
                rval = self.__small.render(str(val), True, WHITE)
                self.__window.blit(rval, (450, yinx))
            yinx += 25

        flip()

    def game_over(self):
        """
        Painted when the player dies and has no more lives.
        """
        self.__window.fill(BLACK)
        self.__window.set_alpha(128)
        toobad = self.__large.render("GAME OVER", True, WHITE)
        tryagain = self.__small.render("Try again (y/n)?", True, WHITE)
        self.__window.blit(toobad, (250, 300))
        self.__window.blit(tryagain, (250, 350))
        flip()

    # TODO: Use graphics
    def paint_stats(self, ship):
        """
        Paints statistics about the ship and game to the left panel
        """
        font = self.__smaller
        lives = font.render("Lives: " + str(ship.get_lives()), True, WHITE)
        power = font.render("Power: " + str(ship.get_power()), True, WHITE)
        dist = font.render("Dist: " + str(self.__total_distance), True, WHITE)
        rect = self.left.blit(lives, (10, 200))
        rect = self.left.blit(power, (10, rect.bottom))
        self.left.blit(dist, (10, rect.bottom))

    # TODO: Use graphics
    def paint_boss(self, boss):
        """
        Paints boss statistics to the right panel
        """
        life = boss.max_damage - boss.get_damage()
        boss = self.__smaller.render("Boss: " + str(life), True, WHITE)
        self.right.blit(boss, (10, 100))

#
# Functions below
#

def flip():
    pygame.display.flip()
    
def rotate(image):
    """
    For convenience, all sprites face east in their images. We usually however,
    want them to face south. To do that we need to rotate -90 degrees 
    counter-clockwise
    """
    return pygame.transform.rotate(image, -90)
