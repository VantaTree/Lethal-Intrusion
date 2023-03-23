import pygame
from .engine import *
from .config import *
from .player import Player
from .world import preload_world_stuff, Level, Camera, FIFO
from .economy import preload_coin, CoinSystem
from .effects import preload_effects, ParticleEffect
from .menus import PauseMenu, DeathMenu
from .ui import UI

class Game:

    GRASSY = 0
    ROCKY = 1
    CORRIDOR = 2

    def __init__(self, master):

        self.master = master
        self.master.game = self
        self.screen = master.display

        # generate_all_path()
        self.master.offset = pygame.Vector2(0, 0)

        preload_world_stuff()
        preload_coin()
        preload_effects()
        self.enemy_grp = CustomGroup()

        self.vingette = pygame.image.load("graphics/vingette.png").convert_alpha()
        self.vingette = pygame.transform.scale(self.vingette, (W, H))
        
        self.pause_menu = PauseMenu(master)
        self.death_menu = DeathMenu(master)
        self.particle_effect = ParticleEffect(master)
        self.player = Player(master)
        self.level = Level(master, "Intestine01", change_track=False)
        self.master.level = self.level
        self.camera = Camera(master, self.player, lambda a:a.hitbox.center)

        self.paused = False
        self.death_screen = False

        self.coin_system = CoinSystem(master)
        self.ui = UI(master)
        self.fifo = FIFO(master, 15)

    def transition_level(self, level_id, trans_id, direc):

        self.coin_system.grp.empty()

        del self.level
        self.level = Level(self.master, level_id, trans_id)
        self.master.level = self.level

        if direc in ("right", "left"):
            self.player.velocity.update(self.player.max_speed*self.player.facing_x, 0)
        elif direc == "up":
            self.player.velocity.update(self.player.max_speed*self.player.facing_x, -self.player.jump_power)
        else: self.player.velocity.update(0, 0)

        self.player.jumping = False
        self.player.landing = False

    def pause_game(self):

        if not self.paused:
            self.paused = True
            
            self.pause_menu.open()

    def open_death_screen(self):

        self.paused = True
        self.death_screen = True
        self.death_menu.open()

    def run(self):

        self.master.debug("CoinsUpdating: ", len(self.coin_system.grp))

        pass

        if self.death_screen:
            self.death_menu.update()
            self.death_menu.draw()
            return
        elif self.paused:
            self.pause_menu.update()
            self.pause_menu.draw()
            return
        elif self.fifo.active:
            if not self.fifo.run():
                return
            if not self.fifo.active:
                self.player.NEGATE_JUMP_STOP_TIMER.start(2_000)

        self.player.update()
        self.enemy_grp.update()
        self.level.update()
        self.camera.update()
        self.coin_system.update()
        self.particle_effect.update()
        self.ui.update()

        self.level.draw_bg()
        self.particle_effect.grp.draw()
        self.enemy_grp.draw()
        self.coin_system.draw()
        self.player.draw()
        self.particle_effect.attack_grp.draw()
        self.level.draw_fg()
        self.ui.draw()

        if self.fifo.active:
            self.fifo.midway()

