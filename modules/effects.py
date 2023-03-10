import pygame
from .frect import FRect
from .config import *
from .engine import *

EFFECTS = {}

def load_effects():

    EFFECTS.update( import_sprite_sheets("graphics/effects") )

class ParticleEffect:

    def __init__(self, master):

        self.master = master
        master.particle_effect = self

        self.grp = CustomGroup()

    def add_effect(self, type, name, move_key=None, anim_speed=0.15, kill_on_anim=False, flip=False):

        if type == "attack":
            AttackEffect(self.master, [self.grp], name, move_key, anim_speed, kill_on_anim, flip)

    def draw(self):

        self.grp.draw()

    def update(self):

        self.grp.update()

class AttackEffect(pygame.sprite.Sprite):

    def __init__(self, master, grps, type, move_key=None, anim_speed=0.15, kill_on_anim=False, flip=False):

        super().__init__(grps)
        self.master = master
        self.screen = master.display
        self.type = type
        self.kill_on_anim = kill_on_anim
        self.move = move_key

        self.animation = EFFECTS[type]
        self.image = self.animation[0]
        self.rect = self.image.get_rect()
        self.anim_index = 0
        self.anim_speed = anim_speed
        self.flip = flip

    def update_image(self):

        try:
            image = self.animation[int(self.anim_index)]
        except IndexError:
            if self.kill_on_anim:
                self.kill()
                return
            image = self.animation[0]
            self.anim_index = 0

        self.anim_index += self.anim_speed*self.master.dt

        self.image = pygame.transform.flip(image, self.flip, False)

    def move(self): pass

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)

    def update(self):

        self.update_image()
        self.move(self)