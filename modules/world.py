import pygame
import pygame_shaders
import csv
import pytmx
from pytmx.util_pygame import load_pygame
from math import ceil
from .config import *
from .engine import *

class Level:

    def __init__(self, master, level_id, trans_id=None):
        
        self.master = master
        self.screen = master.display
        
        self.map_type = level_id
        self.data = load_pygame(F"data/maps/{self.map_type}.tmx")
        self.size = self.data.width, self.data.height

        self.path_data = self.load_csv(F"data/map_paths/{self.map_type}.csv", True)
        self.get_collision_data()
        self.get_draw_layers()
        self.get_object_layers()

        if trans_id is not None:
            trans_to = self.data.get_object_by_name(F"transition_spawn_{trans_id}")
            self.master.player.hitbox.midbottom = trans_to.x, trans_to.y

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

    def get_object_layers(self):

        self.transition_objects = self.data.get_layer_by_name("transition")

    def draw_bg(self):

        pygame_shaders.clear((0, 0, 0))
        self.screen.fill(self.data.background_color)

        for layer in self.bg_layers:
            if isinstance(layer, pytmx.TiledImageLayer):
                self.draw_image_layer(self.screen, layer, self.master.offset)

        for layer in self.tile_map_layers:
            for x, y, image in layer.tiles():
                self.screen.blit(image, (x*TILESIZE + self.master.offset.x, y*TILESIZE + self.master.offset.y - image.get_height() + TILESIZE))
        
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

                # if self.path_data[y][x]:
                #     pygame.draw.rect(self.screen, "blue", (x*TILESIZE+self.master.offset.x, y*TILESIZE+self.master.offset.y, TILESIZE, TILESIZE), 1)                

        for layer in self.fg_layers:
            if isinstance(layer, pytmx.TiledImageLayer):
                self.draw_image_layer(self.screen, layer, self.master.offset)

    def draw_fg(self):

        pass
    
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
            surface.blit(layer.image, pos)

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

                self.master.game.transition_level(obj.properties["room_to"], obj.properties["transition_to"])


    def update(self):

        self.check_player_transitions()


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