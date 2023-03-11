import pygame
from .frect import FRect
from .config import *
from .engine import *
from math import sin

ENEMIES:dict[str, dict[str, list[pygame.Surface]]] = {}

def preload_enemies():

    for name in ("crawler",):
        ENEMIES[name] = import_sprite_sheets(F"graphics/enemies/{name}")

#states:

IDLE = 0
AGRO = 1
FOLLOW = 2
ATTACK = 3


class Enemy(pygame.sprite.Sprite):

    def __init__(self, master, grps, type, flip, pos, size, max_speed, acc, decc, health):
        
        super().__init__(grps)
        self.master = master
        self.screen = master.display

        self.type = type
        self.animations = ENEMIES[type]
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect()
        self.anim_index = 0

        self.hitbox = FRect(0, 0, *size)
        self.hitbox.midbottom = pos
        self.base_rect = FRect(0, 0, size[0]+1, 3)
        self.velocity = pygame.Vector2()
        self.input_x = 0
        self.facing_x = -1 if flip else 1
        self.max_speed = max_speed
        self.acceleration = acc
        self.deceleration = decc

        self.on_ground = False
        self.on_slope = False
        self.on_one_way_platform = False
        self.moving = False
        self.attacking = False
        self.invinsible = False
        self.hurting = False

        self.health = health

        self.INVINSIBILITY_TIMER = CustomTimer()
        self.HURTING_TIMER = CustomTimer()

    def update_image(self, state=None, anim_speed=None):

        if state is None:
            if self.attacking: state = "attack"
            elif self.moving: state = "walk"
            else: state = "idle"

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:

            if self.attacking: self.attacking = False

            image = self.animations[state][0]
            self.anim_index = 0

        if anim_speed is None:
            if self.attacking: anim_speed = 0.3
            elif self.moving: anim_speed = 0.15
            else: anim_speed = 0.08

        self.anim_index += anim_speed*self.master.dt

        self.image = pygame.transform.flip(image, self.facing_x<0 , False)
        if self.hurting:
            self.image.fill((180, 0, 12), special_flags=pygame.BLEND_RGBA_MIN)
        elif self.invinsible and sin(pygame.time.get_ticks()/20) > 0.8:
            self.image.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)

        self.rect.midbottom = self.hitbox.midbottom

    def apply_force(self):

        # self.input_x = 0

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_PERIOD]:
        #     self.input_x += 1
        #     self.facing_x = 1
        # if keys[pygame.K_COMMA]:
        #     self.input_x -= 1
        #     self.facing_x = -1

        if self.input_x: self.facing_x = self.input_x
        self.moving = bool(self.input_x)

        if self.moving:
            self.velocity.move_towards_ip( (self.max_speed*self.input_x, self.velocity.y), self.acceleration *self.master.dt)
        else:
            self.velocity.move_towards_ip( (0, self.velocity.y), self.deceleration *self.master.dt)

        self.velocity.y += GRAVITY *self.master.dt

        if self.velocity.y > 6:
            self.velocity.y = 6

    def move(self):

        self.hitbox.centerx += self.velocity.x * self.master.dt
        self.do_collision(0)
        self.hitbox.centery += self.velocity.y * self.master.dt

        self.on_ground = False
        self.on_slope = False
        self.on_one_way_platform = False

        self.do_collision(1)
        self.do_collision(2)

    def do_collision(self, axis):

        level = self.master.level
        px1 = int(self.hitbox.left / TILESIZE)
        px2 = int(self.hitbox.right / TILESIZE)
        py1 = int(self.hitbox.top / TILESIZE)
        py2 = int(self.hitbox.bottom / TILESIZE)
        
        self.base_rect.midbottom = self.hitbox.midbottom
        self.base_rect.y += 1

        for y in range(py1, py2+1):
            for x in range(px1, px2+1):

                if x < 0 or y < 0: continue
                try:
                    cell =  level.collision[y][x]
                except IndexError: continue

                rect = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE)
                rectg = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, 4)
                if not self.hitbox.colliderect(rect): continue

                if axis == 0: # x-axis

                    if cell == 3:

                        if self.velocity.x > 0:
                            self.hitbox.right = rect.left
                        if self.velocity.x < 0:
                            self.hitbox.left = rect.right

                elif axis == 1: # y-axis
                    if cell == 3 or ( cell == 4 and (rectg.collidepoint(self.hitbox.bottomleft) or rectg.collidepoint(self.hitbox.bottomright)) ):

                            if self.velocity.y > 0:
                                self.hitbox.bottom = rect.top
                                self.velocity.y = 0
                                self.on_ground = True
                                if cell == 4:
                                    self.on_one_way_platform = True

                    if cell == 3:
                        if self.velocity.y < 0:
                            self.hitbox.top = rect.bottom
                            self.velocity.y = 0

                elif axis == 2 and self.velocity.y >= 0: # slopes

                    if not rect.colliderect(self.base_rect): continue

                    relx = None
                    if cell == 1:
                        relx = self.hitbox.right - rect.left
                    elif cell == 2:
                        relx = rect.right - self.hitbox.left
                    else: continue
                        
                    if relx is not None:
                        if relx > TILESIZE:
                            self.hitbox.bottom = rect.top
                            self.on_ground = True
                            self.on_slope = True
                            self.velocity.y = 0
                        elif self.hitbox.bottom > y*TILESIZE-relx+TILESIZE:
                            self.hitbox.bottom = y*TILESIZE-relx+TILESIZE
                            self.on_ground = True
                            self.on_slope = True
                            self.velocity.y = 0
        
    def check_timers(self):

        if self.INVINSIBILITY_TIMER.check():
            self.invinsible = False
        if self.HURTING_TIMER.check():
            self.hurting = False

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)

    def update(self):

        self.check_timers()
        self.apply_force()
        self.move()
        self.update_image()


class Crawler(Enemy):

    def __init__(self, master, grps):

        super().__init__(master, grps, "crawler", False, (48, 300), (32, 12), 0.6, 0.07, 0.12, 100)

        self.state = IDLE

    def state_manager(self):

        player = self.master.player
        self.input_x = 0

        if self.state == IDLE:
            if dist_sq(player.hitbox.center, self.hitbox.center) < 128**2:
                self.state = FOLLOW
        if self.state == FOLLOW:
            dist = player.hitbox.centerx - self.hitbox.centerx
            if dist > 0: self.input_x = 1
            elif dist < 0: self.input_x = -1

            if dist_sq(player.hitbox.center, self.hitbox.center) < 32**2:
                self.state = ATTACK
                self.attacking = True
                self.anim_index = 0
        if self.state == ATTACK and not self.attacking:
            self.state = FOLLOW
        

    def update(self):

        self.state_manager()
        super().update()