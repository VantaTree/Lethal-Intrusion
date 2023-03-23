import pygame
from .config import *
from .engine import *

EFFECTS = {}

def preload_effects():

    EFFECTS.update( import_sprite_sheets("graphics/effects") )

class ParticleEffect:

    def __init__(self, master):

        self.master = master
        master.particle_effect = self

        self.grp = CustomGroup()
        self.attack_grp = CustomGroup()

    def add_effect(self, type, name, move_key=None, anim_speed=0.15, kill_on_anim=False, flip=False):

        if type == "attack":
            Effect(self.master, [self.attack_grp], name, move_key, anim_speed, kill_on_anim, flip)
        elif type == "dust":
            PlayerDust(self.master, [self.grp], name)

    # def draw(self):

    #     self.grp.draw()
    #     self.attack_grp.draw()

    def update(self):

        self.grp.update()
        self.attack_grp.update()


class Effect(pygame.sprite.Sprite):

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
        self.draw_image = True

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

        if not self.draw_image: return

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)

    def update(self):

        self.update_image()
        if self.move is not None:
            self.move(self)


class PlayerDust(Effect):

    def __init__(self, master, grps, type):

        flip = master.player.facing_x < 0

        move_key = None
        if type in ("floor_dust", "step_dust"):
            kill_on_anim = True
        elif type == "wall_dust":
            kill_on_anim = False
            def right(effect):effect.rect.bottomright = (master.player.hitbox.right, master.player.hitbox.centery+16)
            self.move_right_key = right
            def left(effect):effect.rect.bottomleft = (master.player.hitbox.left, master.player.hitbox.centery+16)
            self.move_left_key = left
        else: raise KeyError(F"type: {type} not implemented")

        super().__init__(master, grps, type, move_key, 0.15, kill_on_anim, flip)

        if type == "floor_dust":
            self.rect.midbottom = master.player.hitbox.midbottom
        elif type == "step_dust":
            # if not flip:
            #     self.rect.bottomright = master.player.hitbox.bottomleft
            # else:
            #     self.rect.bottomleft = master.player.hitbox.bottomright
            self.rect.midbottom = master.player.hitbox.midbottom

    def update(self):
        
        if self.type == "wall_dust":
            if not self.master.player.wall_clinged:
                self.draw_image = False
                return
            self.draw_image = True
            self.flip = self.master.player.facing_x < 0
            if not self.flip:
                self.move = self.move_right_key
            else:
                self.move = self.move_left_key

        super().update()