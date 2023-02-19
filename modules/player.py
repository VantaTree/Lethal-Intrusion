import pygame
import random
from .frect import FRect
from .engine import *
from .config import *

#TODO: Player Movt, https://cryptpad.fr/pad/#/3/pad/edit/53704a288fec495a6656d0bedd99227f/

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
        self.facing_x = 1
        self.wall_x = 1
        self.max_speed = 2
        self.acceleration = 0.5
        self.deceleration = 0.5
        self.jump_power = 7.5
        self.dash_speed = 8
        self.gravity = 0.32

        # self.facing_right = True
        self.moving = False
        self.can_double_jump = False
        self.on_ground = True
        self.on_slope = False
        self.jumping = False
        self.landing = False
        self.dashing = False
        self.can_dash = True
        self.on_wall = False
        self.wall_clinged = False
        self.touched_wall = False

        self.in_control = True

        self.has_double_jump = True
        self.has_dash = True
        self.has_wall_cling = True

        self.JUMP_BUFFER = CustomTimer()
        self.CYOTE_TIMER = CustomTimer()
        self.DASH_BUFFER = CustomTimer()
        self.DASH_COOLDOWN = CustomTimer()
        self.DASH_FOR = CustomTimer()
        self.WALL_JUMP_FOR = CustomTimer()

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

        self.image = pygame.transform.flip(image, self.facing_x==-1, False)
        self.rect.midbottom = self.hitbox.midbottom

    def process_events(self):

        if not self.in_control:
            self.input_x = 0
            if not self.dashing:
                self.moving = False
            return

        self.input_x = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.input_x += 1
            self.facing_x = 1
            # self.facing_right = True
        if keys[pygame.K_a]:
            self.input_x -= 1
            self.facing_x = -1
            # self.facing_right = False

        self.moving = bool(self.input_x)

        for event in pygame.event.get((pygame.KEYUP, pygame.KEYDOWN)):
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    # self.JUMP_TIMER.stop()
                    # self.can_jump = True
                    if self.velocity.y < -2:
                        self.velocity.y = -2
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.JUMP_BUFFER.start(60)
                if self.has_dash and self.can_dash and event.key in (pygame.K_LSHIFT, pygame.K_LCTRL):
                    self.DASH_BUFFER.start(60)
                # if event.key in (pygame.K_ESCAPE, pygame.K_p):
                #     self.master.game.pause_game()

        if self.JUMP_BUFFER.running and (self.on_ground or self.wall_clinged or self.CYOTE_TIMER.running or self.can_double_jump):

            if not (self.on_ground or self.wall_clinged or self.CYOTE_TIMER.running) and self.can_double_jump:
                self.can_double_jump = False
            if self.wall_clinged:
                self.facing_x = self.wall_x
                self.velocity.x = 2.5*self.wall_x
                self.in_control = False
                self.WALL_JUMP_FOR.start(80)
            self.velocity.y = -self.jump_power
            self.jumping = True
            self.anim_index = 0
            self.JUMP_BUFFER.stop()
            self.CYOTE_TIMER.stop()
            # self.master.sounds["jump2"].play()

        if self.DASH_BUFFER.running and not self.DASH_COOLDOWN.running:

            if not (self.on_ground or self.wall_clinged or self.CYOTE_TIMER.running):
                self.can_dash = False
            if self.wall_clinged:
                self.facing_x = self.wall_x
            self.dashing = True
            self.in_control = False
            self.DASH_BUFFER.stop()
            self.DASH_COOLDOWN.start(400)
            self.DASH_FOR.start(100)
    
    def check_timers(self):

        self.JUMP_BUFFER.check()
        self.CYOTE_TIMER.check()
        self.DASH_BUFFER.check()
        self.DASH_COOLDOWN.check()
        if self.DASH_FOR.check():
            self.in_control = True
            self.dashing = False
            self.velocity.x = self.facing_x*2
        if self.WALL_JUMP_FOR.check():
            self.in_control = True

    def apply_force(self):

        if self.dashing:
            self.velocity.y = 0
            self.velocity.x = self.facing_x*self.dash_speed
            return

        if self.moving:
            self.velocity.move_towards_ip( (self.max_speed*self.input_x, self.velocity.y), self.acceleration *self.master.dt)
        elif not self.WALL_JUMP_FOR.running:
            self.velocity.move_towards_ip( (0, self.velocity.y), self.deceleration *self.master.dt)

        self.velocity.y += self.gravity *self.master.dt

        limit_y = 1.5 if self.wall_clinged else 8
        if self.velocity.y > limit_y:
            self.velocity.y = limit_y


    def move(self):

        self.on_wall = False

        self.hitbox.centerx += self.velocity.x * self.master.dt
        do_collision(self, self.master.level, 0, self.master)
        self.hitbox.centery += self.velocity.y * self.master.dt
        if self.on_slope and not self.dashing:
            self.hitbox.centery += abs(self.velocity.x * self.master.dt) +1

        self.power_land = 0
        if not self.on_ground: self.power_land = self.velocity.y
        was_on_ground = self.on_ground
        self.on_ground = False
        self.on_slope = False

        do_collision(self, self.master.level, 1, self.master)
        do_collision(self, self.master.level, 2, self.master)

        self.wall_clinged = self.on_wall and not self.on_ground
        self.touched_wall = self.wall_clinged

        if not self.on_ground and was_on_ground:
            self.CYOTE_TIMER.start(100)

        if self.on_ground or self.wall_clinged:
            if self.has_double_jump:
                self.can_double_jump = True
            self.can_dash = True

        if self.power_land > 1 and self.on_ground:
            self.landing = True
            self.anim_index = 0
            if self.power_land >= 8:
                # self.master.sounds["big_thud"].play()
                pass

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        # pygame.draw.rect(self.screen, "green", (self.hitbox.x + self.master.offset.x, self.hitbox.y + self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)

    def update(self):

        self.process_events()
        self.check_timers()
        self.apply_force()
        self.move()
        self.update_image()

        self.master.debug("pos: ", (round(self.hitbox.centerx, 2), round(self.hitbox.bottom, 2)))
        self.master.debug("moving: ", self.moving)
        self.master.debug("on ground: ", self.on_ground)
        self.master.debug("wall cling: ", self.wall_clinged)
        self.master.debug("can double jump: ", self.can_double_jump)
        self.master.debug("can dash: ", self.can_dash)



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
            if player.has_wall_cling and player.touched_wall and axis == 0 and cell == 3 and rect.colliderect(player.hitbox.inflate(2, 0)):
                player.on_wall = True
            if not player.hitbox.colliderect(rect): continue
            rectg = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, 8)

            if axis == 0: # x-axis

                if cell == 3:

                    if not player.touched_wall:
                        player.wall_x = player.facing_x * -1
                    player.touched_wall = True

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
