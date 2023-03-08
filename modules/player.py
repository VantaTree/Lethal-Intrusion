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

        self.animations = import_sprite_sheets("graphics/player/new_anims")
        self.animation = self.animations["idle"]
        self.image = self.animation[0]
        self.rect = self.image.get_rect()

        self.anim_index = 0
        self.anim_speed = 0.15

        self.base_rect = FRect(0, 0, 18, 3)
        self.hitbox = FRect(32, 0, 17, 30)
        self.velocity = pygame.Vector2()
        self.input_x = 0
        self.facing_x = 1
        self.wall_x = 1
        self.max_speed = 2
        self.acceleration = 0.5
        self.deceleration = 0.5
        self.jump_power = 7.5
        self.dash_speed = 6
        self.gravity = 0.32
        self.terminal_vel = 6

        self.moving = False
        self.can_double_jump = False
        self.on_ground = True
        self.on_slope = False
        self.on_one_way_platform = False
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
        self.WALL_CYOTE_TIMER = CustomTimer()
        self.DASH_BUFFER = CustomTimer()
        self.DASH_COOLDOWN = CustomTimer()
        self.DASH_FOR = CustomTimer()
        self.WALL_JUMP_FOR = CustomTimer()
        self.NEGATE_PLATFORM_COLLISION = CustomTimer() # one way olatform collsion (4)

        self.money = 0

    def update_image(self):

        if self.dashing: state = "dash"
        elif self.wall_clinged and self.velocity.y > 0: state = "cling"
        elif self.landing: state = "land"
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
        elif self.dashing: self.anim_speed = 0.25
        elif self.moving: self.anim_speed = 0.15
        else: self.anim_speed = 0.08

        self.anim_index += self.anim_speed *self.master.dt

        self.image = pygame.transform.flip(image, self.facing_x==-1, False)
        self.rect = self.image.get_rect(midbottom=self.hitbox.midbottom)
        if state == "cling":
            if self.facing_x == 1:
                self.rect.midright = self.hitbox.midright
            elif self.facing_x == -1:
                self.rect.midleft = self.hitbox.midleft

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
        if keys[pygame.K_a]:
            self.input_x -= 1
            self.facing_x = -1

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
                if self.has_dash and self.can_dash and event.key in (pygame.K_LSHIFT, pygame.K_LCTRL, pygame.K_j):
                    self.DASH_BUFFER.start(60)
                    self.anim_index = 0
                if self.on_one_way_platform and event.key == pygame.K_s:
                    self.NEGATE_PLATFORM_COLLISION.start(500)
                # if event.key in (pygame.K_ESCAPE, pygame.K_p):
                #     self.master.game.pause_game()

                #for testing, temporary
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                if event.key == pygame.K_o:
                    mx, my = pygame.mouse.get_pos()
                    mx = mx/3 - self.master.offset.x
                    my = my/3 - self.master.offset.y
                    self.master.coin_system.spawn_coins((mx, my), 3)
                if event.key == pygame.K_p:
                    mx, my = pygame.mouse.get_pos()
                    mx = mx/3 - self.master.offset.x
                    my = my/3 - self.master.offset.y
                    self.master.coin_system.spawn_coins((mx, my), 10)

        if self.JUMP_BUFFER.running and (self.on_ground or self.wall_clinged or self.CYOTE_TIMER.running or self.WALL_CYOTE_TIMER.running or self.can_double_jump):

            if not (self.on_ground or self.wall_clinged or self.CYOTE_TIMER.running or self.WALL_CYOTE_TIMER.running) and self.can_double_jump:
                self.can_double_jump = False
            if self.wall_clinged:
                self.facing_x = self.wall_x
                self.velocity.x = 2.5*self.wall_x
                self.in_control = False
                self.WALL_JUMP_FOR.start(100)
            self.velocity.y = -self.jump_power
            self.jumping = True
            self.anim_index = 0
            self.JUMP_BUFFER.stop()
            self.CYOTE_TIMER.stop()
            # self.master.sounds["jump2"].play()

        if self.DASH_BUFFER.running and not self.DASH_COOLDOWN.running:

            if not (self.on_ground or self.wall_clinged or self.CYOTE_TIMER.running or self.WALL_CYOTE_TIMER.running):
                self.can_dash = False
            if self.wall_clinged:
                self.facing_x = self.wall_x
            self.dashing = True
            self.in_control = False
            self.DASH_BUFFER.stop()
            self.DASH_COOLDOWN.start(500)
            self.DASH_FOR.start(200)
    
    def check_timers(self):

        self.JUMP_BUFFER.check()
        self.CYOTE_TIMER.check()
        self.WALL_CYOTE_TIMER.check()
        self.DASH_BUFFER.check()
        self.DASH_COOLDOWN.check()
        self.NEGATE_PLATFORM_COLLISION.check()
        if self.DASH_FOR.check():
            self.in_control = True
            self.dashing = False
            self.velocity.x = self.facing_x*2
        if self.WALL_JUMP_FOR.check():
            self.in_control = True
            if self.input_x:
                self.velocity.x = abs(self.velocity.x) * self.input_x

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

        limit_y = 1.7 if self.wall_clinged else self.terminal_vel
        if self.velocity.y > limit_y:
            self.velocity.y = limit_y

    def move(self):

        self.on_wall = False

        self.hitbox.centerx += self.velocity.x * self.master.dt
        self.do_collision(0)
        self.hitbox.centery += self.velocity.y * self.master.dt
        if self.on_slope and not self.dashing:
            self.hitbox.centery += abs(self.velocity.x * self.master.dt) +1

        self.power_land = 0
        if not self.on_ground: self.power_land = self.velocity.y
        was_on_ground = self.on_ground
        self.on_ground = False
        self.on_slope = False
        self.on_one_way_platform = False

        self.do_collision(1)
        self.do_collision(2)

        was_wall_clinged = self.wall_clinged

        self.wall_clinged = self.on_wall and not self.on_ground
        self.touched_wall = self.wall_clinged

        if not self.wall_clinged and was_wall_clinged:
            self.WALL_CYOTE_TIMER.start(100)

        if not self.on_ground and was_on_ground:
            self.CYOTE_TIMER.start(100)

        if self.on_ground or self.wall_clinged:
            if self.has_double_jump:
                self.can_double_jump = True
            self.can_dash = True

        if self.power_land > 1 and self.on_ground:
            self.landing = True
            self.anim_index = 0
            if self.power_land >= self.terminal_vel:
                # self.master.sounds["big_thud"].play()
                pass

    def do_collision(self, axis):

        level = self.master.level
        px = int(self.hitbox.centerx / TILESIZE)
        py = int(self.hitbox.centery / TILESIZE)
        self.base_rect.midbottom = self.hitbox.midbottom
        self.base_rect.y += 1

        for y in range(py-1, py+2):
            for x in range(px-1, px+2):

                if x < 0 or y < 0: continue
                try:
                    cell =  level.collision[y][x]
                except IndexError: continue

                rect = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE)
                if self.has_wall_cling and self.touched_wall and axis == 0 and cell == 3 and rect.colliderect(self.hitbox.inflate(2, 0)):
                    self.on_wall = True
                if not self.hitbox.colliderect(rect): continue
                rectg = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, 8)

                if axis == 0: # x-axis

                    if cell == 3:

                        if not self.touched_wall:
                            self.wall_x = self.facing_x * -1
                        self.touched_wall = True

                        if self.velocity.x > 0:
                            self.hitbox.right = rect.left
                        if self.velocity.x < 0:
                            self.hitbox.left = rect.right

                elif axis == 1: # y-axis
                    if cell == 3 or ( cell == 4 and not self.NEGATE_PLATFORM_COLLISION.running and (rectg.collidepoint(self.hitbox.bottomleft) or rectg.collidepoint(self.hitbox.bottomright)) ):

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
                            self.hitbox.bottom = y*TILESIZE-relx+TILESIZE# +1 #error correction
                            self.on_ground = True
                            self.on_slope = True
                            self.velocity.y = 0

    def collect_coin(self, value):
        self.money += value

    def draw(self):

        self.screen.blit(self.image, self.rect.topleft + self.master.offset)
        # pygame.draw.rect(self.screen, "green", (self.hitbox.x + self.master.offset.x, self.hitbox.y + self.master.offset.y, self.hitbox.width, self.hitbox.height), 1)
        # pygame.draw.rect(self.screen, "blue", (self.rect.x + self.master.offset.x, self.rect.y + self.master.offset.y, self.rect.width, self.rect.height), 1)

    def update(self):

        self.process_events()
        self.check_timers()
        self.apply_force()
        self.move()
        self.update_image()

        self.master.debug("Money: ", self.money)
        # self.master.debug("pos: ", (round(self.hitbox.centerx, 2), round(self.hitbox.bottom, 2)))
        # self.master.debug("moving: ", self.moving)
        # self.master.debug("on ground: ", self.on_ground)
        # self.master.debug("wall cling: ", self.wall_clinged)
        # self.master.debug("can double jump: ", self.can_double_jump)
        # self.master.debug("can dash: ", self.can_dash)
