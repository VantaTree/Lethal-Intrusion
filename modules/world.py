import pygame
import pygame_shaders
import csv
from .config import *
from .engine import *

class Level:

    def __init__(self, master, level_id):
        
        self.master = master
        self.screen = master.display
        
        self.map_type = level_id
        self.collision = self.load_csv(F"data/levels/{level_id}/_collision.csv", True)
        self.size = len(self.collision[0])*TILESIZE, len(self.collision)*TILESIZE

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

    def draw_bg(self):

        pygame_shaders.clear((114, 6, 12))
        self.screen.fill(0x72060c)
        
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

    def draw_fg(self):

        pass

    def update(self):

        pass


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

        if self.master.offset.x > 0: self.master.offset.x = 0
        elif self.master.offset.x < -self.master.level.size[0]*TILESIZE + W:
            self.master.offset.x = -self.master.level.size[0]*TILESIZE + W

        if self.master.offset.y > 0: self.master.offset.y = 0
        if self.master.offset.y < -self.master.level.size[1]*TILESIZE + H:
            self.master.offset.y = -self.master.level.size[1]*TILESIZE + H

    def update(self):

        self.update_offset()
        self.clamp_offset()