import pygame
import glcontext
import pygame_shaders
import asyncio
from modules import *
import pygame._sdl2 as sdl2

class Master:

    def __init__(self):

        self.app:App
        self.debug:Debug
        self.dt:float
        self.offset:pygame.Vector2
        self.display:pygame.Surface
        self.window: sdl2.Window

        self.font_1 = pygame.font.Font("fonts/PixelOperator.ttf", 14)
        self.font = pygame.font.Font("fonts/PixelOperator-Bold.ttf", 18)
        self.font_big = pygame.font.Font("fonts/PixelOperator.ttf", 32)


class App:

    MAIN_MENU = 2
    IN_GAME = 3

    def __init__(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED|pygame.OPENGL|pygame.DOUBLEBUF)
        self.display = pygame.Surface((W, H))
        pygame.display.set_caption("Lethal Intrusion")
        # icon = pygame.image.load("graphics/icon.png").convert()
        # pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()

        self.shader = pygame_shaders.Shader((W, H), (W, H), (0, 0), "shaders/default_vertex.glsl", 
                        "shaders/default_fragment.glsl", self.display)

        self.state = self.MAIN_MENU

        self.master = Master()
        self.master.display = self.display
        self.master.app = self
        self.master.window = sdl2.Window.from_display_module()
        self.music = Music(self.master)
        self.debug = Debug(self.display, 14, 7)
        self.master.debug = self.debug
        self.game = Game(self.master)
        self.main_menu = MainMenu(self.master)
        SoundSet(self.master)

    async def run(self):
        
        while True:

            pygame.display.flip()

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

            self.shader.render(self.display)

    def run_states(self):

        self.music.run()

        if self.state == self.MAIN_MENU:
            self.main_menu.run()
        elif self.state == self.IN_GAME:
            self.game.run()

if __name__ == "__main__":

    app = App()
    asyncio.run(app.run())
