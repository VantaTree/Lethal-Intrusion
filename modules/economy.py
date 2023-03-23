import pygame
import random
from .config import *
from .engine import *

coin_animations:dict[int, list[pygame.Surface]] = {}

def preload_coin():

    global coin_animations
    # surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    # pygame.draw.circle(surf, "pink", (8, 8), 2)
    # coin_animations[1] = [surf.copy()]
    # pygame.draw.circle(surf, "magenta", (8, 8), 3)
    # coin_animations[5] = [surf]

    coin_animations = import_sprite_sheets("graphics/coins")

class Coin(pygame.sprite.Sprite):

    def __init__(self, master, grps, pos, velocity:pygame.Vector2, value):

        self.master = master
        self.screen = master.display
        super().__init__(grps)

        self.value = value
        self.velocity = velocity

        if value == 1:
            size = 6
        elif value == 5:
            size = 8
        self.hitbox = pygame.FRect(0, 0, size, size)
        self.base_rect = pygame.FRect(0, 0, size+1, 2)
        self.top_rect = pygame.FRect(0, 0, size+1, 2)
        self.hitbox.center = pos

        self.animation = coin_animations[str(value)]
        self.image = self.animation[0]
        self.rect = self.image.get_rect(center = pos)

        self.anim_index = 0
        self.anim_speed = 0.15
        
        self.velx_resistance = 0.004
        self.terminal_vel = 6
        self.bounce_factor = 0.5

        self.moving = True
        self.touch_block = False
        self.on_slope = False

    def update_image(self):

        try:
            self.image = self.animation[int(self.anim_index)]
        except IndexError:
            self.image = self.animation[0]
            self.anim_index = 0

        self.anim_index += self.anim_speed * self.master.dt

        self.rect.center = self.hitbox.center

    def move(self):

        x_res = self.velx_resistance*self.master.dt
        if self.touch_block and not self.on_slope: x_res *= 10

        self.velocity = self.velocity.move_towards((0, self.velocity.y), x_res)
        self.velocity.y += GRAVITY * self.master.dt

        if self.velocity.y > self.terminal_vel:
            self.velocity.y = self.terminal_vel

        prev_pos = self.hitbox.center

        self.hitbox.x += self.velocity.x * self.master.dt
        self.do_collision(0)
        self.touch_block = False
        self.on_slope = False
        self.hitbox.y += self.velocity.y * self.master.dt
        self.do_collision(1)
        self.do_collision(2)

        self.moving = prev_pos != self.hitbox.center

    def check_player_collide(self):

        if self.hitbox.colliderect(self.master.player.hitbox):
            self.master.player.collect_coin(self.value)
            self.kill()

    def do_collision(self, axis):

        level = self.master.level
        px1 = int(self.hitbox.left / TILESIZE)
        px2 = int(self.hitbox.right / TILESIZE)
        py1 = int(self.hitbox.top / TILESIZE)
        py2 = int(self.hitbox.bottom / TILESIZE)
        
        self.base_rect.midbottom = self.hitbox.midbottom
        self.base_rect.y += 1
        self.top_rect.midtop = self.hitbox.midtop
        self.top_rect.y -= 1

        for y in range(py1, py2+1):
            for x in range(px1, px2+1):

                if x < 0 or y < 0: continue
                try:
                    cell =  level.collision[y][x]
                except IndexError: continue

                rect = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE)
                rectg = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, 4)
                if not self.hitbox.colliderect(rect): continue

                if axis == 0 and cell == 3: # x-axis

                        if self.velocity.x > 0:
                            self.hitbox.right = rect.left
                        if self.velocity.x < 0:
                            self.hitbox.left = rect.right

                        self.velocity.x *= -self.bounce_factor

                elif axis == 1: # y-axis
                    if cell == 3 or ( cell == 4 and (rectg.collidepoint(self.hitbox.bottomleft) or rectg.collidepoint(self.hitbox.bottomright)) ):

                            if self.velocity.y > 0:
                                self.hitbox.bottom = rect.top
                                self.touch_block = True

                    if cell == 3:
                        if self.velocity.y < 0:
                            self.hitbox.top = rect.bottom
                            self.touch_block = True

                    if cell in (3, 4):
                        self.velocity.y *= -self.bounce_factor

                elif axis == 2: # slopes

                    if cell in (1, 2) and self.velocity.y >= 0 and rect.colliderect(self.base_rect):

                        relx = None
                        if cell == 1:
                            relx = self.hitbox.right - rect.left
                        elif cell == 2:
                            relx = rect.right - self.hitbox.left
                        else: continue
                        
                        if relx > TILESIZE:
                            self.hitbox.bottom = rect.top
                            self.touch_block = True
                            self.on_slope = True
                        elif self.hitbox.bottom > y*TILESIZE-relx+TILESIZE:
                            self.hitbox.bottom = y*TILESIZE-relx+TILESIZE
                            self.touch_block = True
                            self.on_slope = True

                        if self.on_slope:
                            self.velocity *= self.bounce_factor
                            if cell == 1:
                                self.velocity.reflect_ip((-0.1, -1))
                            elif cell == 2:
                                self.velocity.reflect_ip((0.1, -1))

                    if cell in (5, 6) and self.velocity.y <= 0 and rect.colliderect(self.top_rect):

                        relx = None
                        if cell == 5:
                            relx = self.hitbox.right - rect.left
                        elif cell == 6:
                            relx = rect.right - self.hitbox.left
                        else: continue

                        if relx > TILESIZE:
                            self.hitbox.top = rect.bottom
                            self.touch_block = True
                            self.on_slope = True
                        elif self.hitbox.top < y*TILESIZE+relx:
                            self.hitbox.top = y*TILESIZE+relx
                            self.touch_block = True
                            self.on_slope = True

                        if self.on_slope:
                            self.velocity *= self.bounce_factor
                            if cell == 5:
                                self.velocity.reflect_ip((-0.1, 1))
                            elif cell == 6:
                                self.velocity.reflect_ip((0.1, 1))

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft+self.master.offset)

    def update(self):

        if self.moving:
            self.move()
        self.update_image()
        self.draw()
        self.check_player_collide()

class CoinSystem:

    def __init__(self, master):

        self.master = master
        master.coin_system = self

        self.grp = CustomGroup()

    def spawn_coins(self, pos, value, direction = None, offset = 20):

        if direction is None:
            direction = pygame.Vector2(0, -1)

        for _ in range((value//10)*2):
            Coin(self.master, [self.grp], pos,
                self.get_random_velocity(direction, offset)*random.randint(30, 40)*0.1, 5)
            
        for _ in range(value%10):
            Coin(self.master, [self.grp], pos,
                self.get_random_velocity(direction, offset)*random.randint(30, 40)*0.1, 1)

    @staticmethod
    def get_random_velocity(direction:pygame.Vector2, offset):
        return direction.rotate(random.randint(-offset, offset))

    def draw(self):

        self.grp.draw()

    def update(self):

        self.grp.update()
    