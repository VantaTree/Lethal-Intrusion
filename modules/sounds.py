import pygame
from os import listdir

class SoundSet:

    def __init__(self, master):

        self.dict:dict[str, pygame.mixer.Sound] = {}
        
        self.master = master
        self.master.sounds = self

        for sound_file in listdir("sounds"):
            self.dict[sound_file[:-4]] = pygame.mixer.Sound(F"sounds/{sound_file}")

        self.dict["jump2"].set_volume(0.3)
        self.dict["UI_click"].set_volume(0.3)
        self.dict["PC_slash"].set_volume(0.3)

    def __getitem__(self, key):

        return self.dict[key]