import pygame
from modules import *
import asyncio

class Master:

    def __init__(self):

        self.app:App
        self.debug:Debug
        self.dt:float
        self.offset:pygame.Vector2


    
class App:

    MAIN_MENU = 2
    IN_GAME = 3

    def __init__(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED)
        pygame.display.set_caption("Lethal Intrusion")
        # icon = pygame.image.load("graphics/icon.png").convert()
        # pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()

        self.state = self.IN_GAME

        self.master = Master()
        self.master.app = self
        self.debug = Debug()
        self.master.debug = self.debug
        self.game = Game(self.master)
        # SoundSet(self.master)
        # self.main_menu = MainMenu(self.master)

    async def run(self):
        
        while True:

            pygame.display.update()

            self.master.dt = self.clock.tick(FPS) / 16.667
            if self.master.dt > 10: self.master.dt = 10
            self.debug("FPS:", round(self.clock.get_fps(), 2))

            for event in pygame.event.get((pygame.QUIT)):
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            await asyncio.sleep(0)

            self.run_states()
            self.debug.draw()

    def run_states(self):

        if self.state == self.IN_GAME:
            self.game.run()

if __name__ == "__main__":

    app = App()
    asyncio.run(app.run())
