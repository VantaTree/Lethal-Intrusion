import pygame
from .config import *
from .engine import *


class Button():
    def __init__(self, master, pos, action, button_list, text_color='white'):

        self.pos = pos
        self.action = action
        self.master = master
        self.screen = master.display
        self.text_color = text_color
        self.mouse_hover = False
        self.hover_sound_played = False


        self.image = self.master.font.render(action.upper(), False, self.text_color)
        self.rect = self.image.get_rect(center=pos)
        self.detection_rect = self.rect.inflate(10,10)

        self.underline = pygame.Surface((self.image.get_width(), 1))
        self.underline.fill(self.text_color)
        self.underline_rect = self.underline.get_rect(midtop=(self.rect.midbottom))

        self.shadow = self.master.font.render(action.upper(), False, (105, 75, 105))
        self.shadow.set_alpha(200)
        

        button_list.append(self)

    def interact(self, mouse_pos, click=False):

        if click and self.mouse_hover:
            if self.action != "start":self.master.sounds["UI_click"].play()
            return self.action
        self.mouse_hover = self.detection_rect.collidepoint(mouse_pos)
        if self.mouse_hover:
            if not self.hover_sound_played:
                self.hover_sound_played = True
                self.master.sounds["soft_click"].play()
        else:self.hover_sound_played = False

    def draw(self):
        
        if not self.mouse_hover:
            self.screen.blit(self.shadow, (self.rect.left-2, self.rect.top+2))
        else:
            self.screen.blit(self.underline, self.underline_rect)

        self.screen.blit(self.image, self.rect)


class MainMenu():

    def __init__(self, master):
        self.master = master
        self.master.main_menu = self
        self.screen = master.display
        self.mainmenu_bg = pygame.image.load("graphics/cover.png").convert()
        self.mainmenu_bg = pygame.transform.scale(self.mainmenu_bg, (W, H))
        # self.title_surf = self.master.font_big.render('Lethal Intrusion', False, (163, 32, 28))
        # self.title_rect = self.title_surf.get_rect(midtop=(W/2, 40))
        # self.title_shadow = self.master.font_big.render('Lethal Intrusion', False, (105, 75, 105))
        # self.title_shadow.set_alpha(200)
        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        # col = (252, 205, 146)
        col = (123*1.5, 40*1.5, 102*1.5)
        Button(self.master, (W//2, H*0.68), 'start', self.buttons, col)
        Button(self.master, (W//2, H*0.78), 'fullscreen', self.buttons, col)
        Button(self.master, (W//2, H*0.88), 'quit', self.buttons, col)

    def update(self):

        for event in pygame.event.get((pygame.MOUSEBUTTONDOWN)):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(get_mouse_pos(self.master), click=True)
                    if action == 'start':
                        self.master.music.change_track("tunnel")
                        self.master.sounds["UI_click"].play()
                        self.master.app.state = self.master.app.IN_GAME
                    elif action == 'fullscreen':
                        pygame.display.toggle_fullscreen()
                    elif action == 'quit':
                        pygame.quit()
                        raise SystemExit
                    if action is not None:
                        return

    def draw(self):

        self.screen.fill((80, 10, 20))

        self.screen.blit(self.mainmenu_bg, (0, 0))

        # self.screen.blit(self.title_shadow, (self.title_rect.x-2, self.title_rect.y+2))
        # self.screen.blit(self.title_surf, self.title_rect)

        for button in self.buttons:
            button.draw()
            button.interact(get_mouse_pos(self.master))

    def run(self):
        self.update()
        self.draw()


class PauseMenu():

    def __init__(self, master):
        self.master = master
        self.master.pause_menu = self

        self.screen = master.display
        self.bg = self.screen.copy()
        self.bg_overlay = pygame.Surface(self.screen.get_size())
        self.bg_overlay.fill((123, 40, 102))
        self.bg_overlay.set_alpha(192)

        self.title_surf = self.master.font_big.render('Paused', False, (163, 32, 28))
        self.title_rect = self.title_surf.get_rect(midtop=(W/2, 40))
        self.title_shadow = self.master.font_big.render('Paused', False, (105, 75, 105))
        self.title_shadow.set_alpha(200)

        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        Button(self.master, (W//2, H*0.4), 'resume', self.buttons)
        Button(self.master, (W//2, H*0.5), 'fullscreen', self.buttons)
        Button(self.master, (W//2, H*0.6), 'quit', self.buttons)

    def open(self):
        self.bg = self.screen.copy()
        self.master.sounds["UI_click"].play()

    def update(self):
        
        for event in pygame.event.get((pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.master.game.paused = False
                self.master.sounds["UI_click"].play()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(get_mouse_pos(self.master), click=True)
                    if action == 'resume':
                        self.master.game.paused = False
                    elif action == 'fullscreen':
                        pygame.display.toggle_fullscreen()
                    elif action == 'quit':
                        pygame.quit()
                        raise SystemExit
                    if action is not None:
                        return
    def draw(self):

        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.bg_overlay, (0, 0))

        self.screen.blit(self.title_shadow, (self.title_rect.x-2, self.title_rect.y+2))
        self.screen.blit(self.title_surf, self.title_rect)

        for button in self.buttons:
            button.draw()
            button.interact(get_mouse_pos(self.master))

class DeathMenu():

    def __init__(self, master):
        self.master = master
        self.master.pause_menu = self

        self.screen = master.display
        self.bg = self.screen.copy()
        self.bg_overlay = pygame.Surface(self.screen.get_size())
        self.bg_overlay.fill((123, 40, 102))
        self.bg_overlay.set_alpha(192)

        self.title_surf = self.master.font_big.render('You Died', False, (163, 32, 28))
        self.title_rect = self.title_surf.get_rect(midtop=(W/2, 40))
        self.title_shadow = self.master.font_big.render('You Died', False, (105, 75, 105))
        self.title_shadow.set_alpha(200)

        self.buttons:list[Button] = []
        self.create_buttons()
        
    def create_buttons(self):

        Button(self.master, (W//2, H*0.4), 'retry', self.buttons)
        Button(self.master, (W//2, H*0.5), 'main menu', self.buttons)
        Button(self.master, (W//2, H*0.6), 'quit', self.buttons)

    def open(self):
        self.bg = self.screen.copy()
        self.master.sounds["UI_click"].play()

    def update(self):
        
        for event in pygame.event.get((pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                for button in self.buttons:
                    action = button.interact(get_mouse_pos(self.master), click=True)
                    if action == 'retry':
                        self.master.game.paused = False
                        self.master.game.death_screen = False
                    elif action == 'main menu':
                        self.master.app.state = self.master.app.MAIN_MENU
                        self.master.game.paused = False
                        self.master.game.death_screen = False
                        self.master.music.change_track("main_menu")
                    elif action == 'quit':
                        pygame.quit()
                        raise SystemExit
                    if action is not None:
                        return
    def draw(self):

        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.bg_overlay, (0, 0))

        for button in self.buttons:
            button.draw()
            button.interact(get_mouse_pos(self.master))
