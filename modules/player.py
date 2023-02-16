import pygame
import random
from .frect import FRect
from .engine import *
from .config import *

class Player:

    def __init__(self, master):

        self.master = master
        self.master.player = self
        self.screen = master.display

        self.animations = import_sprite_sheets("graphics/player/anims")
        self.animation = self.animations["idle"]
        self.image = self.animation[0]
        self.rect = self.image.get_rect()

        self.anim_index = 0
        self.anim_speed = 0.15

        self.base_rect = FRect(0, 0, 14, 3)
        self.hitbox = FRect(32, 0, 13, 28)
        self.velocity = pygame.Vector2()
        self.input_x = 0
        self.max_speed = 2
        self.acceleration = 0.5
        self.deceleration = 0.5
        self.jump_power = 7.5
        self.gravity = 0.4

        self.facing_right = True
        self.moving = False
        self.can_jump = True
        self.on_ground = True
        self.on_slope = False
        self.jumping = False
        self.landing = False

        self.in_control = True

        self.dying = False

        self.JUMP_TIMER = CustomTimer()
        self.CYOTE_TIMER = CustomTimer()

    def update_image(self):

        if self.landing: state = "land"
        elif self.jumping: state = "jump"
        elif not self.on_ground: state = "midair"
        elif self.moving: state = "run"
        else:  state = "idle"

        try:
            image = self.animations[state][int(self.anim_index)]
        except IndexError:
            image = self.animations[state][0]
            self.anim_index = 0

            if self.jumping: self.jumping = False
            if self.landing: self.landing = False

        if self.jumping or self.landing: self.anim_speed = 0.2
        elif self.moving: self.anim_speed = 0.15
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        self.image = pygame.transform.flip(image, not self.facing_right, False)
        self.rect.midbottom = self.hitbox.midbottom

    def get_input(self):

        if not self.in_control:
            self.moving = False
            return

        self.input_x = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.input_x += 1
            self.facing_right = True
        if keys[pygame.K_a]:
            self.input_x -= 1
            self.facing_right = False
        
        if keys[pygame.K_SPACE] and (self.on_ground or self.CYOTE_TIMER.running) and self.can_jump:

            self.velocity.y = -self.jump_power
            self.can_jump = False
            self.JUMP_TIMER.start(600)
            self.jumping = True
            self.anim_index = 0
            self.CYOTE_TIMER.stop()
            # self.master.sounds["jump2"].play()

        self.moving = bool(self.input_x)

    def apply_force(self):

        if self.moving:
            self.velocity.move_towards_ip( (self.max_speed*self.input_x, self.velocity.y), self.acceleration *self.master.dt)
        else:
            self.velocity.move_towards_ip( (0, self.velocity.y), self.deceleration *self.master.dt)

        self.velocity.y += self.gravity *self.master.dt
        if self.velocity.y > 8:
            self.velocity.y = 8

    def move(self):

        self.hitbox.centerx += self.velocity.x * self.master.dt
        do_collision(self, self.master.game.level, 0, self.master)
        self.hitbox.centery += self.velocity.y * self.master.dt
        if self.on_slope:
            self.hitbox.centery += abs(self.velocity.x * self.master.dt) +1

        self.power_land = 0
        if not self.on_ground: self.power_land = self.velocity.y
        was_on_ground = self.on_ground
        self.on_ground = False
        self.on_slope = False

        do_collision(self, self.master.game.level, 1, self.master)
        do_collision(self, self.master.game.level, 2, self.master)

        if not self.on_ground and was_on_ground:
            self.CYOTE_TIMER.start(100)

        if self.power_land > 1 and self.on_ground:
            self.landing = True
            self.anim_index = 0
            if self.power_land >= 8:
                # self.master.sounds["big_thud"].play()
                pass


    def process_events(self):

        if self.in_control:
            for event in pygame.event.get((pygame.KEYUP, pygame.KEYDOWN)):
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.JUMP_TIMER.stop()
                        self.can_jump = True
                        if self.velocity.y < -1:
                            self.velocity.y = -1
                    # if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    #     self.master.game.pause_game()
            
        if self.JUMP_TIMER.check():
            self.can_jump = True

        self.CYOTE_TIMER.check()

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        # pygame.draw.rect(self.screen, "green", (self.hitbox.x + self.master.offset.x, self.hitbox.y + self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)

    def update(self):

        self.process_events()
        self.get_input()
        self.apply_force()
        self.move()
        self.update_image()

        self.master.debug("pos: ", (round(self.hitbox.centerx, 2), round(self.hitbox.bottom, 2)))
        self.master.debug("on ground: ", self.on_ground)
        self.master.debug("on slope: ", self.on_slope)


def do_collision(player:Player, level, axis, master):

    px = int(player.hitbox.centerx / TILESIZE)
    py = int(player.hitbox.centery / TILESIZE)
    player.base_rect.midbottom = player.hitbox.midbottom
    player.base_rect.y += 1

    for y in range(py-1, py+2):
        for x in range(px-1, px+2):

            if x < 0 or y < 0: continue
            try:
                cell =  level.collision[y][x]
            except IndexError: continue

            rect = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE)
            if not player.hitbox.colliderect(rect): continue
            rectg = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, 8)

            if axis == 0: # x-axis

                if cell == 3:

                    if player.velocity.x > 0:
                        player.hitbox.right = rect.left
                    if player.velocity.x < 0:
                        player.hitbox.left = rect.right

            elif axis == 1: # y-axis
                if cell == 3 or ( cell == 4 and (rectg.collidepoint(player.hitbox.bottomleft) or rectg.collidepoint(player.hitbox.bottomright)) ):

                        if player.velocity.y > 0:
                            player.hitbox.bottom = rect.top
                            player.velocity.y = 0
                            player.on_ground = True

                if cell == 3:
                    if player.velocity.y < 0:
                        player.hitbox.top = rect.bottom
                        player.velocity.y = 0

            elif axis == 2 and player.velocity.y >= 0: # slopes

                if not rect.colliderect(player.base_rect): continue

                relx = None
                if cell == 1:
                    relx = player.hitbox.right - rect.left
                elif cell == 2:
                    relx = rect.right - player.hitbox.left
                else: continue
                    
                if relx is not None:
                    if relx > TILESIZE:
                        player.hitbox.bottom = rect.top
                        player.on_ground = True
                        player.on_slope = True
                        player.velocity.y = 0
                    elif player.hitbox.bottom > y*TILESIZE-relx+TILESIZE:
                        player.hitbox.bottom = y*TILESIZE-relx+TILESIZE# +1 #error correction
                        player.on_ground = True
                        player.on_slope = True
                        player.velocity.y = 0
                        
def get_xy(grid, x, y):

    if x < 0 or y < 0: return
    try:
        return grid[y][x]
    except IndexError: return
