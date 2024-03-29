import pygame
import pygame_shaders
import csv
import pytmx
from pytmx.util_pygame import load_pygame
from math import ceil
from .enemy import preload_enemies, Enemy, Crawler
from .config import *
from .engine import *

def preload_world_stuff():

    preload_enemies()

class Level:

    def __init__(self, master, level_id, trans_id=None, change_track=True):
        
        self.master = master
        self.screen = master.display
        
        self.map_type = level_id
        self.data = load_pygame(F"data/maps/{self.map_type}.tmx")
        self.size = self.data.width, self.data.height

        # self.path_data = self.load_csv(F"data/map_paths/{self.map_type}.csv", True)
        self.get_collision_data()
        self.get_draw_layers()
        self.get_object_layers()

        if trans_id is not None:
            trans_to = self.data.get_object_by_name(F"transition_spawn_{trans_id}")
            self.master.player.hitbox.midbottom = trans_to.x, trans_to.y

        # Crawler(master, [master.game.enemy_grp])
        if change_track:
            if "Intestine" in self.map_type:
                if self.map_type in ("Intestine01, Intestine02", "Intestine03"):
                    master.music.change_track("tunnel")
                else: master.music.change_track("maze")
                pygame.mixer.music.set_volume(0.6)
            elif "Heart" in self.map_type:
                master.music.change_track("heart")
                pygame.mixer.music.set_volume(0.3)

    @staticmethod
    def load_csv(path, integer=False):

        reader = csv.reader(open(path))
        if integer:
            grid = []
            for row in reader:
                grid.append( [int(cell) for cell in row] )
        else:
            grid = [row for row in reader]

        return grid
    
    def get_collision_data(self):
        
        for tileset in self.data.tilesets:
            if tileset.name == "collision":
                collision_firstgid = tileset.firstgid

        self.collision = self.data.get_layer_by_name("collision").data
        
        for y, row in enumerate(self.collision):
            for x, gid in enumerate(row):

                self.collision[y][x] = self.data.tiledgidmap[gid] - collision_firstgid

    def get_draw_layers(self):

        self.fg_layers = [self.data.get_layer_by_name(F"fg_{i}") for i in range(self.data.properties["fg_layers"])]
        self.tile_map_layers = [self.data.get_layer_by_name(F"tile_map_{i}") for i in range(self.data.properties["tile_map_layers"])]
        self.bg_layers = [self.data.get_layer_by_name(F"bg_{i}") for i in range(self.data.properties["bg_layers"])]

        for layer in self.fg_layers + self.bg_layers:

            if not hasattr(layer, "parallaxx"):
                layer.parallaxx = 1.0
            if not hasattr(layer, "parallaxy"):
                layer.parallaxy = 1.0
            if not hasattr(layer, "repeatx"):
                layer.repeatx = 0
            if not hasattr(layer, "repeaty"):
                layer.repeaty = 0
            if not hasattr(layer, "offsetx"):
                layer.offsetx = 0
            if not hasattr(layer, "offsety"):
                layer.offsety = 0

            layer.parallaxx = float(layer.parallaxx)
            layer.parallaxy = float(layer.parallaxy)

            layer.image2 = pygame.image.load(layer.source.lstrip("../../")).convert()

    def get_object_layers(self):

        self.transition_objects = self.data.get_layer_by_name("transition")

    def draw_bg(self):

        pygame_shaders.clear((0, 0, 0))
        
        if self.data.background_color:
            self.screen.fill(self.data.background_color)
        else:
            self.screen.fill((255, 0, 255))

        for layer in self.bg_layers:
            if isinstance(layer, pytmx.TiledImageLayer):
                self.draw_image_layer(self.screen, layer, self.master.offset)

        for layer in self.tile_map_layers:
            for x, y, image in layer.tiles():
                self.screen.blit(image, (x*TILESIZE + self.master.offset.x, y*TILESIZE + self.master.offset.y - image.get_height() + TILESIZE))
        
        if self.master.debug.on:
            for y, row in enumerate(self.collision):
                for x, cell in enumerate(row):
                    if cell == 1:
                        pygame.draw.polygon(self.screen, 'green', ( ((x*TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE+TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy, ((x*TILESIZE+TILESIZE, y*TILESIZE)+self.master.offset).xy ), 1)
                    elif cell == 2:
                        pygame.draw.polygon(self.screen, 'green', ( ((x*TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE+TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy, ((x*TILESIZE, y*TILESIZE)+self.master.offset).xy ), 1)
                    elif cell == 3:
                        pygame.draw.rect(self.screen, "green", (x*TILESIZE+self.master.offset.x, y*TILESIZE+self.master.offset.y, TILESIZE, TILESIZE), 1)
                    elif cell == 4:
                        pygame.draw.rect(self.screen, "green", (x*TILESIZE+self.master.offset.x, y*TILESIZE+self.master.offset.y, TILESIZE, TILESIZE//4), 1)
                    elif cell == 5:
                        pygame.draw.polygon(self.screen, 'green', ( ((x*TILESIZE, y*TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE+TILESIZE, y*TILESIZE)+self.master.offset).xy, ((x*TILESIZE+TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy ), 1)
                    elif cell == 6:
                        pygame.draw.polygon(self.screen, 'green', ( ((x*TILESIZE, y*TILESIZE+TILESIZE)+self.master.offset).xy,
                        ((x*TILESIZE, y*TILESIZE)+self.master.offset).xy, ((x*TILESIZE+TILESIZE, y*TILESIZE)+self.master.offset).xy ), 1)

                    # if self.path_data[y][x]:
                    #     pygame.draw.rect(self.screen, "blue", (x*TILESIZE+self.master.offset.x, y*TILESIZE+self.master.offset.y, TILESIZE, TILESIZE), 1)                

        for layer in self.fg_layers:
            if isinstance(layer, pytmx.TiledImageLayer):
                self.draw_image_layer(self.screen, layer, self.master.offset)

    def draw_fg(self):

        self.screen.blit(self.master.game.vingette, (0, 0))
    
    @staticmethod
    def draw_image_layer(surface, layer, offset):

        pos = layer.offsetx + offset.x*layer.parallaxx, layer.offsety + offset.y*layer.parallaxy

        if layer.repeatx:
            for i in range(0, ceil((W-pos[0])/layer.image.get_width())):
                surface.blit(layer.image, (pos[0]+ i*layer.image.get_width(), pos[1]))

                if layer.repeaty:
                    for iy in range(1, ceil((H-pos[1])/layer.image.get_height())):
                        surface.blit(layer.image, (pos[0]+ i*layer.image.get_width(), pos[1]+ iy*layer.image.get_height()))

        elif layer.repeaty:
            for iy in range(0, ceil((H-pos[1])/layer.image.get_height())):
                surface.blit(layer.image, (pos[0], pos[1]+ iy*layer.image.get_height()))
        else:
            surface.blit(layer.image2, pos)

    def check_player_transitions(self):

        player = self.master.player

        for obj in self.transition_objects:

            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            if rect.collidepoint(player.hitbox.center):

                direc = obj.properties["direction"]

                if direc == "right" and player.velocity.x > 0:
                    pass
                elif direc == "left" and player.velocity.x < 0:
                    pass
                elif direc == "down" and player.velocity.y > 0:
                    pass
                elif direc == "up" and player.velocity.y < 0:
                    pass
                else: continue

                self.master.game.fifo.start(self.master.game.transition_level, obj.properties["room_to"], obj.properties["transition_to"], direc)

    def update(self):

        self.check_player_transitions()
        self.master.debug("lvl: ", self.map_type)


class Camera:

    def __init__(self, master, target = None, key = None):

        self.master = master
        master.camera = self

        self.camera_rigidness = 0.05

        self.target = target
        self.key = key

    def key(self): pass

    def set_target(self, target, key):

        self.target = target
        self.key = key

    def get_target_pos(self):

        return self.key(self.target)

    def snap_offset(self):

        self.master.offset =  (self.get_target_pos() - pygame.Vector2(W/2, H/2)) * -1

    def update_offset(self):

        if self.target == self.master.player:
            self.camera_rigidness = 0.18 if self.master.player.moving else 0.05
        else: self.camera_rigidness = 0.05
        
        self.master.offset -= (self.master.offset + (self.get_target_pos() - pygame.Vector2(W/2, H/2)))\
            * self.camera_rigidness * self.master.dt

    def clamp_offset(self):

        if self.master.level.size[0]*TILESIZE <= W: self.master.offset.x = 0
        elif self.master.offset.x > 0: self.master.offset.x = 0
        elif self.master.offset.x < -self.master.level.size[0]*TILESIZE + W:
            self.master.offset.x = -self.master.level.size[0]*TILESIZE + W
        
        if self.master.level.size[1]*TILESIZE <= H:
            self.master.offset.y = 0
        elif self.master.offset.y > 0: self.master.offset.y = 0
        elif self.master.offset.y < -self.master.level.size[1]*TILESIZE + H:
            self.master.offset.y = -self.master.level.size[1]*TILESIZE + H

    def update(self):

        self.update_offset()
        self.clamp_offset()

class FIFO:

    def __init__(self, master, alpha_speed):

        self.master = master
        self.screen = self.master.display
        
        self.cover_surf = pygame.Surface((W, H))
        self.bg = pygame.Surface((W, H))

        self.alpha = 0
        self.alpha_speed = alpha_speed

        self.alpha_direc = 0
        self.active = False
        self.signal = None
        self.args = None

    def start(self, signal, *args):

        self.alpha_direc = 1
        self.alpha = 0
        self.active = True
        self.signal = signal
        self.args = args
        self.bg = self.screen.copy()

    def midway(self):

        self.bg = self.screen.copy()
        self.screen.fill((0, 0, 0))

    def run(self):

        self.alpha += self.alpha_speed*self.alpha_direc*self.master.dt
        if self.alpha > 255:
            self.alpha = 255
            self.alpha_direc = -1
            self.signal(*self.args)
            return True
        elif self.alpha < 0:
            self.alpha_direc = 0
            self.alpha = 0
            self.active = False
            return True
        self.cover_surf.set_alpha(self.alpha)

        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.cover_surf, (0, 0))