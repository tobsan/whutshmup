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

from pygame.locals import USEREVENT

WINDOW_SIZE = (800, 600)
GAME_WIDTH = 600
FRAMERATE = 30

# Game states
RUNNING = 0
PAUSED = 1
CLEARED = 2
DIED = 3
QUITGAME = 4
ABORTED = 5

# Values
ENEMY_FIRE = USEREVENT + 1
USER_FIRE  = USEREVENT + 2
BOSS_ENTER = USEREVENT + 4
BOSS_EXIT  = USEREVENT + 5
PLAYER_DIED = USEREVENT + 6

# Speeds, default values
SHIPSPEED = 10
ENEMYSPEED = 3
SHOTSPEED = 25

# Paths
GFX_PATH = "graphics"
SND_PATH = "sound"
MP3_PATH = "music"

