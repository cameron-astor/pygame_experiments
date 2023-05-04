import pygame, time, random
from pygame_util import Scene, SceneManager, Entity


#################
## Tile system ##
#################

# A single tile
class Tile:
    def __init__(self, x, y, sprite: pygame.Surface) -> None:
        self.sprite = sprite
        self.x = x
        self.y = y

    def update(self) -> None:
        pass

    def render(self) -> None:
        pass

# A set of sprites for tiles loaded from a tilesheet file
#
# Tiles will be loaded and numbered from left to right 
# starting at the top of the image and going down.
#
# Tiles must be square. Tilesize reperesents the length of one side
# of the tile.
#
class Tileset:
    def __init__(self, filename: str, original_tilesize: int, scale_factor: int = 1, sprites=None) -> None:
        if sprites is None:
            self.tilesheet = pygame.image.load(filename).convert_alpha() # Load tileset image from file
        else:
            self.tilesheet = sprites # Provide already loaded tilesheet

        self.tileset = {} # Dict of tile ids to tile images
        self.tilesize = original_tilesize # Size of tiles on spritesheet
        self.scale_factor = scale_factor
        self.scaled_size = self.tilesize * self.scale_factor # Final size of sprites in tileset after scaling

        tile_id = 0
        for y in range(int(self.tilesheet.get_height()/self.tilesize)):
            for x in range(int(self.tilesheet.get_width()/self.tilesize)):
                tile_rect = pygame.Rect(x*self.tilesize, y*self.tilesize, self.tilesize, self.tilesize)
                tile_image = self.tilesheet.subsurface(tile_rect)

                # Apply scale factor
                tile_image = pygame.transform.scale(tile_image, 
                                              (tile_image.get_width() * self.scale_factor, 
                                               tile_image.get_height() * self.scale_factor))

                self.tileset[tile_id] = tile_image

                tile_id += 1

    def get_tileset(self) -> dict:
        return self.tileset
 
    def get_tile_sprite(self, id: int) -> pygame.Surface:
        return self.tileset[id]

# A particular configuration of tiles which forms a map.
#
# Takes in a list of lists populated by ID numbers corresponding to a particular
# tileset. This represents the map to be populated with tiles.
class Tilemap(Entity):
    def __init__(self, map: list[list], tileset: Tileset) -> None:
        self.tileset = tileset
        self.map_spec = map
        self.map = [[]]
        self.tilesize = self.tileset.scaled_size # Size of each tile in the map

        TESTMAP =      [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                        [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                        [2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0], 
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        # Create map tiles from spec
        x_coord = 0
        y_coord = 0
        for y in TESTMAP:
            row = []
            for x in y:

                sprite = self.tileset.get_tile_sprite(x)

                tile = Tile(x_coord, y_coord, sprite)
                row.append(tile)
                x_coord += self.tilesize
            y_coord += self.tilesize
            x_coord = 0
            self.map.append(row)

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        for y in self.map:
            for x in y:
                screen.blit(x.sprite, (x.x, x.y))

######################
## Animation system ##
######################

# Uses our tileset abstraction to parse animation spritesheets as well.
#
# A sprite can only have one active animation at a time
class AnimationManager:
    def __init__(self, spritesheet: pygame.Surface) -> None:
        # Parse spritesheet into tileset
        self.tileset = Tileset("none", 16, 4, spritesheet)
        
        # Animations are registered in a dictionary with a name as a key
        # and a list of sprite ids as a value.
        self.animations = {}

    # Register animation.
    def register_animation(self, name: str, sprite_ids: list[int]):
        self.animations["name"] = sprite_ids

    # Get current animation frame
    def get_current_sprite(self) -> pygame.Surface:
        return self.tileset.get_tile_sprite(0)

    # Update animation frame
    def update(self, dt):
        pass

    # Plays a single desired animation for this entity.
    def play_single_animation(self, animation: str, frequency: int):
        pass

    def activate_loop_animation(self, animation: str, frequency: int):
        pass

    def deactivate_loop_animation(self, animation: str):
        pass

##############
## Entities ##
##############

class Player(Entity):
    def __init__(self, spritesheet: pygame.Surface, x, y) -> None:
        self.x = x
        self.y = y

        # Register animations
        self.animations = AnimationManager(spritesheet)

    def update(self, dt) -> None:
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.animations.get_current_sprite(), (self.x, self.y))

class Enemy(Entity):
    pass


############
## Scenes ##
############
class StartScene(Scene):
    def __init__(self, manager: SceneManager, screen: pygame.Surface, sprites: dict, debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)
        self.entities = []
        self.previous_time = None

        # Create tileset
        self.tileset = Tileset("gfx/test_tiles.png", 16, 4)
        # Create tilemap
        self.tilemap = Tilemap([[]], self.tileset)
        # Create player
        self.player = Player(self.sprites["player_animations"], 50, 50)

        self.entities.extend([self.tilemap, self.player])

    def update(self) -> None:

        if self.previous_time is None: # First run through the loop needs a previous_time value to compute delta time
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now 

        for e in self.entities:
            e.update(dt)
    
    def render(self) -> None:
        # Clear screen
        self.screen.fill("black")

        for e in self.entities:
            e.render(self.screen)

        # Update display
        pygame.display.update()
    
    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

class Level1(Scene):
    def __init__(self, manager: SceneManager, screen: pygame.Surface, sprites: dict, debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)

    def update(self) -> None:
        return super().update()
    
    def render(self) -> None:
        return super().render()
    
    def poll_events(self) -> None:
        return super().poll_events()

class Level2(Scene):
    def __init__(self, manager: SceneManager, screen: pygame.Surface, sprites: dict, debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)

    def update(self) -> None:
        return super().update()
    
    def render(self) -> None:
        return super().render()

    def poll_events(self) -> None:
        return super().poll_events()

class GameOverScene(Scene):
    def __init__(self, manager: SceneManager, screen: pygame.Surface, sprites: dict, debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)

    def update(self) -> None:
        return super().update()
    
    def render(self) -> None:
        return super().render()

    def poll_events(self) -> None:
        return super().poll_events()


###################
# Main game class #
###################
class Game:
    def __init__(self) -> None:
        # Initialize global game variables
        pygame.init() 
        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.sprites = self.load_sprites()
        self.debug = False # Default off

        # Scene system
        self.scene_manager = SceneManager()
        # Register scenes
        scenes = {"start": StartScene(self.scene_manager, self.screen, self.sprites, self.debug), 
                  "l1": Level1(self.scene_manager, self.screen, self.sprites, self.debug), 
                  "l2": Level2(self.scene_manager, self.screen, self.sprites, self.debug),
                  "gameover": GameOverScene(self.scene_manager, self.screen, self.sprites, self.debug)}
        self.scene_manager.initialize(scenes, "start")

        # Play music
        # pygame.mixer.music.load("sfx/music.wav")
        # pygame.mixer.music.play()
        # pygame.mixer.music.set_volume(0.1)

    # MAIN GAME LOOP #
    def run(self) -> None:
        self.previous_time = time.time()
        while self.running:

            self.scene_manager.current_scene.poll_events()
            self.scene_manager.current_scene.update()
            self.scene_manager.current_scene.render()

            if self.scene_manager.quit == True:
                self.running = False    

        pygame.quit()

    # Load sprite textures into pygame as surfaces. 
    # Returns a dictionary of names to surfaces.
    def load_sprites(self) -> dict: 
        sprites = {}

        sprites["player_animations"] = pygame.image.load("gfx/player_animations.png").convert_alpha()

        return sprites
    
    # Set debug mode on or off
    def set_debug(self, debug: bool) -> None:
        self.debug = debug


# Main code
g = Game()
# g.set_debug(True)
g.run()
