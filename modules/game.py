import pygame
from .engine import *
from .config import *
from .player import Player
from .world import Level, Camera
# from .music import Music
# from .menus import PauseMenu

class Game:

    GRASSY = 0
    ROCKY = 1
    CORRIDOR = 2

    def __init__(self, master):

        self.master = master
        self.master.game = self
        self.screen = master.display

        self.master.offset = pygame.Vector2(0, 0)

        # self.music = Music(master)
        # self.pause_menu = PauseMenu(master)
        self.player = Player(master)
        self.level = Level(master, "test")
        self.master.level = self.level
        self.camera = Camera(master, self.player, lambda a:a.hitbox.center)

        self.paused = False

    def pause_game(self):

        if not self.paused:
            self.paused = True
            self.pause_menu.open()

    def run(self):

        pass

        # self.music.run()

        # if self.paused:
        #     self.pause_menu.draw()
        #     self.pause_menu.update()
        #     return

        self.player.update()
        self.level.update()
        self.camera.update()

        self.level.draw_bg()
        self.player.draw()
        self.level.draw_fg()
