import pygame, time, random

class Collectible:
    pass

class Player:
    pass

# Main game class
class Game:
    def __init__(self) -> None:
        # Initialize global game variables
        pygame.init() 
        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.sprites = self.load_sprites()

    # MAIN GAME LOOP #
    def run(self) -> None:
        self.previous_time = time.time()
        while self.running:

            self.poll_events()
            self.update()
            self.render()              

        pygame.quit()

    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.running = False

    def update(self) -> None:
        pass

    def render(self) -> None:
        # Clear screen
        self.screen.fill("black")

        # Render background
        self.screen.blit(self.sprites["background"], (0, 0))

        # Render player

        # Render collectible

        # Update the display
        pygame.display.update() 

    # Load sprite textures into pygame as surfaces. 
    # Returns a dictionary of names to surfaces.
    def load_sprites(self) -> dict: 
        sprites = {}

        sprites["collectible"] = pygame.image.load("gfx/collectible.png").convert_alpha()
        sprites["background"] = pygame.image.load("gfx/simple_game_bg.png").convert_alpha()
        sprites["spaceship"] = pygame.image.load("gfx/spaceship.png").convert_alpha()

        return sprites
    
# Main code
g = Game()
g.run()