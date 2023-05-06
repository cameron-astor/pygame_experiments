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

        # Create map tiles from spec
        x_coord = 0
        y_coord = 0
        for y in map:
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

    def render(self, screen: pygame.Surface, camera_adj: tuple) -> None:
        for y in self.map:
            for x in y:
                screen.blit(x.sprite, (x.x + camera_adj[0], x.y + camera_adj[1]))

###################
## Camera system ##
###################

# Represents the camera in the RPG. It centers on the subject.
# Subject must have an x and y property.
class Camera:
    def __init__(self, screen: pygame.Surface, subject) -> None:
        self.screen = screen
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()

        self.subject = subject

        self.camera_adjustment_x = 0
        self.camera_adjustment_y = 0

        # Initial camera adjustment
        # Place subject in center of camera
        self.camera_adjustment_x = (self.screen_w/2) - self.subject.x
        self.camera_adjustment_y = (self.screen_h/2) - self.subject.y

    def get_camera_adjustment(self) -> tuple:
        return (self.camera_adjustment_x, self.camera_adjustment_y)

    def update(self, dt) -> None:
        # Update camera adjustment based on new subject position
        self.camera_adjustment_x = (self.screen_w/2) - self.subject.x
        self.camera_adjustment_y = (self.screen_h/2) - self.subject.y

    

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

        self.current_sprite_id = 0 # The current sprite to be displayed given as an id in the tileset

        self.active_animation = None
        self.active_animation_frequency = 0
        self.loop_animation = False
        self.current_animation_keyframe = 0 
        self.keyframe_time = 0 # For delta time

    # Register animation.
    def register_animation(self, name: str, sprite_ids: list[int]):
        self.animations[name] = sprite_ids

    # Register a single sprite
    def register_sprite(self, name: str, sprite_id: int):
        self.animations[name] = sprite_id

    def set_sprite(self, name: str):
        self.current_sprite_id = self.animations[name]

    # Get current animation frame
    def get_current_sprite(self) -> pygame.Surface:
        return self.tileset.get_tile_sprite(self.current_sprite_id)

    # Update animation frame
    def update(self, dt):

        if self.active_animation is not None: # If an animation is currently playing
            self.keyframe_time += dt # Keeping track of how long the current animation frame has been displayed

            if self.keyframe_time >= self.active_animation_frequency: 
                if len(self.animations[self.active_animation]) - 1 <= self.current_animation_keyframe: # End of this run of animation

                    if self.loop_animation is True:
                        self.current_animation_keyframe = 0
                    else:
                        self.deactivate_animation()
                else: 
                    self.current_animation_keyframe += 1 # Move to next keyframe
                    self.current_sprite_id = self.animations[self.active_animation][self.current_animation_keyframe] # Assign sprite at new keyframe
                    
                self.keyframe_time = 0 # Reset keyframe time before ending animation


    # Plays a single desired animation for this entity.
    # Overrides current animation
    def activate_animation(self, animation: str, frequency: float, loop: bool):
        self.active_animation = animation
        self.active_animation_frequency = frequency
        self.loop_animation = loop

    def deactivate_animation(self):
        self.active_animation = None
        self.active_animation_frequency = 0
        self.loop_animation = False



##############
## Entities ##
##############

class Player(Entity):
    def __init__(self, spritesheet: pygame.Surface, x, y) -> None:
        self.x = x
        self.y = y
        self.velocity = 250
        self.direction = "down" # Direction the player is currently pointing
        self.moving = False

        #########################
        ## Register animations ##
        #########################
        self.animations = AnimationManager(spritesheet)

        # Walking animations
        self.animations.register_animation("walking_right", [3, 7, 11, 15])
        self.animations.register_animation("walking_left", [2, 6, 10, 14])
        self.animations.register_animation("walking_up", [1, 5, 9, 13])
        self.animations.register_animation("walking_down", [0, 4, 8, 12])

        # Stationary sprites
        self.animations.register_sprite("stationary_down", 0)
        self.animations.register_sprite("stationary_up", 1)
        self.animations.register_sprite("stationary_left", 2)
        self.animations.register_sprite("stationary_right", 3)

        self.rect = self.animations.get_current_sprite().get_rect()

    def move(self, dt) -> None:
        if self.direction == "up":
            self.y -= self.velocity * dt
        elif self.direction == "down":
            self.y += self.velocity * dt       
        elif self.direction == "left":
            self.x -= self.velocity * dt      
        elif self.direction == "right":
            self.x += self.velocity * dt

    def set_direction(self, new_direction: str) -> None:
        self.direction = new_direction

    def stop_moving(self) -> None:
        self.moving = False
        self.animations.set_sprite("stationary_" + self.direction)

    def update_collider(self) -> None:
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self, dt) -> None:
        if self.moving:
            self.move(dt)

        self.animations.update(dt)
        self.update_collider()
    
    def render(self, screen: pygame.Surface, camera_adj: tuple) -> None:
        screen.blit(self.animations.get_current_sprite(), (self.x + camera_adj[0], self.y + camera_adj[1]))

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

        # MAP
        MAP     =      [[101,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0], 
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [112,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69]]

        # Create tileset
        self.tileset = Tileset("gfx/rpg_sprites.png", 16, 4)
        # Create tilemap
        self.tilemap = Tilemap(MAP, self.tileset)
        # Create player
        self.player = Player(self.sprites["player_animations"], 50, 50)
        # Create camera
        self.camera = Camera(self.screen, self.player)

        #######################
        ## USER INPUT SYSTEM ##
        #######################
        self.keybinds = {pygame.K_w: (0, "up"),
                         pygame.K_d: (270, "right"),
                         pygame.K_s: (180, "down"),
                         pygame.K_a: (90, "left")}
        
        self.keystack = []
        self.current_key = None

    def update(self) -> None:

        if self.previous_time is None: # First run through the loop needs a previous_time value to compute delta time
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now 

        self.tilemap.update(dt)
        self.player.update(dt)
        self.camera.update(dt)
    
    def render(self) -> None:
        # Clear screen
        self.screen.fill((30, 124, 184)) # Water background color

        # for e in self.entities:
        #     e.render(self.screen)
        self.tilemap.render(self.screen, self.camera.get_camera_adjustment())
        self.player.render(self.screen, self.camera.get_camera_adjustment())

        # Update display
        pygame.display.update()
    
    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

            if event.type == pygame.KEYDOWN and event.key in self.keybinds:

                # The moment a key is pressed, add it to the keystack
                self.keystack.append(event.key)
                print(self.keystack)


            
            if event.type == pygame.KEYUP and event.key in self.keybinds:

                # If the key is released, remove it from the keystack
                self.keystack.remove(event.key)
                print(self.keystack)

                # if self.keybinds[event.key][1] == self.player.direction:
                #     self.player.moving = False

            # Read latest element in keystack
            if len(self.keystack) > 0: # If keystack has any keys
                if self.current_key != self.keystack[-1]: # If the active key has changed
                    # Deactivate animation
                    self.player.animations.deactivate_animation()

                    self.current_key = self.keystack[-1]

                    # Player commands
                    self.player.set_direction(self.keybinds[self.current_key][1])
                    self.player.animations.activate_animation("walking_" + self.keybinds[event.key][1], 0.2, True)
                    self.player.moving = True

            if len(self.keystack) == 0:
                self.current_key = None
                self.player.stop_moving()



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
        sprites["environment_tiles"] = pygame.image.load("gfx/rpg_sprites.png").convert_alpha()

        return sprites
    
    # Set debug mode on or off
    def set_debug(self, debug: bool) -> None:
        self.debug = debug


# Main code
g = Game()
# g.set_debug(True)
g.run()
