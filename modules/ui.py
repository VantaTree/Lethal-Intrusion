import pygame
from .config import *
from .engine import *

class UI:

    def __init__(self, master):

        self.master = master
        master.ui = self

        self.screen = master.display

        #player UI

        self.heart_icon = pygame.image.load("graphics/ui/heart_icon.png").convert_alpha()
        self.bar_empty = pygame.image.load("graphics/ui/bar_empty.png").convert_alpha()
        self.bar_health = pygame.image.load("graphics/ui/bar_health.png").convert_alpha()
        self.health_ui_pos = 10, 10

        self.heart_icon = pygame.transform.scale_by(self.heart_icon, 2)
        self.bar_empty = pygame.transform.scale_by(self.bar_empty, 2)
        self.bar_health = pygame.transform.scale_by(self.bar_health, 2)

        self.coin_icon = pygame.image.load("graphics/ui/coin.png").convert_alpha()
        self.coin_icon = pygame.transform.scale_by(self.coin_icon, 2)
        self.coin_ui_pos = 15, 40

    def draw(self):

        #player health

        self.screen.blit(self.heart_icon, self.health_ui_pos)
        for i in range(5):
            bar = self.bar_health if i < self.master.player.health else self.bar_empty
            pos = (self.heart_icon.get_width()+self.health_ui_pos[0]+5+i*bar.get_width(),
                   self.health_ui_pos[1] + 6)
            self.screen.blit(bar, pos)

        self.screen.blit(self.coin_icon, self.coin_ui_pos)
        text = self.master.font.render(str(self.master.player.money), False, (123, 40, 102))
        self.screen.blit(text, (self.coin_ui_pos[0]+20, self.coin_ui_pos[1]-2))


    def update(self):

        pass