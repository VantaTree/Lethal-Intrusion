import pygame
from .engine import *
from .config import *
from .player import Player
from .world import Level, Camera
from .path_gen import generate_all_path
from .economy import load_coin, CoinSystem
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

        generate_all_path()
        self.master.offset = pygame.Vector2(0, 0)

        load_coin()

        # self.music = Music(master)
        # self.pause_menu = PauseMenu(master)
        self.player = Player(master)
        self.level = Level(master, "test")
        self.master.level = self.level
        self.camera = Camera(master, self.player, lambda a:a.hitbox.center)

        self.paused = False

        self.coin_system = CoinSystem(master)

    def transition_level(self, level_id, trans_id):

        self.level = Level(self.master, level_id, trans_id)
        self.master.level = self.level

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
        self.coin_system.update()

        self.level.draw_bg()
        self.coin_system.draw()
        self.player.draw()
        self.level.draw_fg()
