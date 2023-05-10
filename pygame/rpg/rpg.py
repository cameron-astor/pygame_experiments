import pygame, time, random
from pygame_util import Scene, SceneManager


#################
## Tile system ##
#################

# A single tile
class Tile:
    def __init__(self, x, y, sprite: pygame.Surface, sprite_id: int) -> None:
        self.sprite = sprite
        self.x = x
        self.y = y
        self.sprite_id = sprite_id

        # Collision rect
        self.rect = self.sprite.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

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
class Tilemap:
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

                tile = Tile(x_coord, y_coord, sprite, x)
                row.append(tile)
                x_coord += self.tilesize
            y_coord += self.tilesize
            x_coord = 0
            self.map.append(row)

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.Surface, camera_adj: tuple) -> None:
        pass
        # for y in self.map:
        #     for x in y:
        #         screen.blit(x.sprite, (x.x + camera_adj[0], x.y + camera_adj[1]))

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

# Represents a single animation to be played by the AnimationManager
#
# The tileset corresponds to the particular tileset the animation sprites
# will be drawn from.
#
# The keyframes are the particular animation sprite ids in order.
class Animation:
    def __init__(self, name: str, tileset: Tileset, keyframes: list[int]) -> None:

        self.name = name

        self.tileset = tileset
        # print("IN ANIMATION CONSTRUCTOR of " + self.name)
        # print(type(self.tileset))

        self.current_sprite_id = 0

        self.keyframes = keyframes

        self.loop_animation = False
        self.animation_frequency = 0
        self.current_keyframe = 0 
        self.keyframe_time = 0 # For delta time

    def get_current_sprite(self) -> pygame.Surface:
        # print(self.tileset)
        return self.tileset.get_tile_sprite(self.current_sprite_id)

    def update(self, dt) -> None:

            self.keyframe_time += dt # Keeping track of how long the current animation frame has been displayed

            if self.keyframe_time >= self.animation_frequency: 
                if len(self.keyframes) - 1 <= self.current_keyframe: # End of this run of animation

                    if self.loop_animation is True:
                        self.current_keyframe = 0
                    else:
                        self.deactivate_animation()

                else: 
                    self.current_keyframe += 1 # Move to next keyframe
                    self.current_sprite_id = self.keyframes[self.current_keyframe] # Assign sprite at new keyframe
                    
                self.keyframe_time = 0 # Reset keyframe time before ending animation

    # Plays a single desired animation for this entity.
    # Overrides current animation
    def activate_animation(self, frequency: float, loop: bool):
        self.animation_frequency = frequency
        self.loop_animation = loop

    def deactivate_animation(self):
        self.animation_frequency = 0
        self.loop_animation = False
    

# Uses our tileset abstraction to parse animation spritesheets as well.
#
# A sprite can only have one active animation at a time
class AnimationManager:
    def __init__(self, spritesheets: dict, tilesize: int, scale: int) -> None:
        
        self.tilesets = {}

        # Parse spritesheets into tilesets
        for s in spritesheets:
            tileset = Tileset("none", tilesize, scale, spritesheets[s])
            self.tilesets[s] = tileset
        
        self.active_animation = Animation("dummy", self.tilesets[list(self.tilesets.keys())[0]], [0]) # Set to dummy as default
        # print(self.active_animation.name)

        # Animations are registered in a dictionary with a name as a key
        # and an Animation object as values
        self.animations = {}

        # self.current_sprite_id = 0 # The current sprite to be displayed given as an id in the tileset
        self.current_tileset = None # The current active tileset for the animation

    # Register animation.
    def register_animation(self, name: str, sprite_ids: list[int], tileset: str):
        # print(tileset)
        # print(self.tilesets[tileset])
        self.animations[name] = Animation(name, self.tilesets[tileset], sprite_ids)

    # Get current animation frame
    def get_current_sprite(self) -> pygame.Surface:
        if self.active_animation is not None:
            return self.active_animation.get_current_sprite() # type: ignore
        else:
            return pygame.Surface((0,0))

    # Update animation frame
    def update(self, dt):
        if self.active_animation is not None:
            self.active_animation.update(dt) # type: ignore

    # Plays a single desired animation for this entity.
    # Overrides current animation
    def activate_animation(self, animation: str, frequency: float, loop: bool):
        self.active_animation = self.animations[animation]
        self.active_animation.animation_frequency = frequency
        self.active_animation.loop_animation = loop

    def deactivate_animation(self):
        self.active_animation = None


##############
## Entities ##
##############

class Player:
    def __init__(self, spritesheets: dict, x, y) -> None:
        self.x = x
        self.y = y
        self.velocity = 250 # Movement speed
        self.direction = "down" # Direction the player is currently pointing
        self.moving = False

        #########################
        ## Register animations ##
        #########################
        self.animations = AnimationManager(spritesheets, 16, 4)

        # Walking animations
        self.animations.register_animation("walking_right", [3, 7, 11, 15], "walking_animations")
        self.animations.register_animation("walking_left", [2, 6, 10, 14], "walking_animations")
        self.animations.register_animation("walking_up", [1, 5, 9, 13], "walking_animations")
        self.animations.register_animation("walking_down", [0, 4, 8, 12], "walking_animations")

        # Stationary sprites
        self.animations.register_animation("stationary_down", [0, 0, 0], "walking_animations")
        self.animations.register_animation("stationary_up", [1, 1, 1], "walking_animations")
        self.animations.register_animation("stationary_left", [2, 2, 2], "walking_animations")
        self.animations.register_animation("stationary_right", [3, 3, 3], "walking_animations")

        # Attacks
        self.animations.register_animation("attack_down", [0, 0, 0], "attack_animation")
        self.animations.register_animation("attack_up", [1, 1, 1], "attack_animation")
        self.animations.register_animation("attack_left", [2, 2, 2], "attack_animation")
        self.animations.register_animation("attack_right", [3, 3, 3], "attack_animation")

        self.rect = pygame.Rect(self.x, self.y, 16, 16)

    def move(self, dt) -> None:
        if self.direction == "up":
            self.y -= self.velocity * dt
        elif self.direction == "down":
            self.y += self.velocity * dt       
        elif self.direction == "left":
            self.x -= self.velocity * dt      
        elif self.direction == "right":
            self.x += self.velocity * dt

    def attack(self) -> None:
        self.animations.activate_animation("attack_" + self.direction, 0.1, False)

    def set_direction(self, new_direction: str) -> None:
        self.direction = new_direction

    def start_moving(self, animation: str) -> None:
        self.moving = True
        self.animations.activate_animation(animation, 0.15, True)

    def stop_moving(self) -> None:
        self.moving = False
        self.animations.activate_animation("stationary_" + self.direction, 0.1, True)

    def update_collider(self) -> None:
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self, dt) -> None:
        if self.moving:
            self.move(dt)

        self.animations.update(dt)
        # print(self.animations.active_animation.current_sprite_id)
        self.update_collider()
    
    def render(self, screen: pygame.Surface, camera_adj: tuple) -> None:
        screen.blit(self.animations.get_current_sprite(), (self.x + camera_adj[0], self.y + camera_adj[1]))

class Enemy:
    def __init__(self, spritesheets: dict, x, y) -> None:
        self.spritesheet = spritesheets
        self.x = x
        self.y = y
        self.health = 3

        #########################
        ## Register animations ##
        #########################
        self.animations = AnimationManager(spritesheets, 50, 4)
        self.animations.register_animation("idle", [0, 1, 2, 3, 4], "enemy_idle")
        self.animations.activate_animation("idle", 0.1, True) # Start playing animation

    def update(self, dt):
        self.animations.update(dt)

    def render(self, screen: pygame.Surface, camera_adj: tuple):
        screen.blit(self.animations.get_current_sprite(), (self.x + camera_adj[0], self.y + camera_adj[1]))

class Projectile:
    def __init__(self, spritesheets: dict, x, y) -> None:
        self.spritesheets = spritesheets
        self.x = x
        self.y = y
        self.velocity = 500
        self.rotation = 0
        self.direction = "right"

        self.animations = AnimationManager(spritesheets, 16, 2)
        self.animations.register_animation("projectile", [0, 1, 2, 3, 4], "projectile")
        self.animations.activate_animation("projectile", 0.1, True)

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

    def update(self, dt):
        self.animations.update(dt)
        self.move(dt)

    def render(self, screen: pygame.Surface, camera_adj: tuple):
        screen.blit(self.animations.get_current_sprite(),  (self.x + camera_adj[0], self.y + camera_adj[1]))

class Button:
    def __init__(self, x, y, text: str) -> None:
        self.x = x
        self.y = y

        self.font = pygame.font.SysFont("Calibri", 36)
        self.color = "white"
        self.text = text

        self.text_surface = self.font.render(self.text, True, self.color)
        self.rect = self.text_surface.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.hovered = False

        self.event = lambda: print("Default button") # Function for when the button is pressed

    def update(self, dt):
        if self.hovered is True:
            self.color = "blue"
        else:
            self.color = "white"

        # Rerender text
        self.text_surface = self.font.render(self.text, True, self.color)    

    def set_hover(self, hovered: bool):
        self.hovered = hovered

    # Register the event to happen when the button is pressed.
    def register_event(self, func):
        self.event = func

    def render(self, screen: pygame.Surface):
        screen.blit(self.text_surface, (self.x, self.y))        

############
## Scenes ##
############
class StartScene(Scene):
    def __init__(self, manager: SceneManager, screen: pygame.Surface, sprites: dict, debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)
        # self.entities = []
        self.previous_time = None

        # MAP
        MAP     =      [[101,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,102], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 79], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0, 0, 0, 0, 0,79], 
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [112,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,113]]

        # Create tileset
        self.tileset = Tileset("gfx/rpg_sprites.png", 16, 4)
        # Create tilemap
        self.tilemap = Tilemap(MAP, self.tileset)

        # Create player
        # Player animations
        player_anims = {"walking_animations": self.sprites["player_walk"],
                        "attack_animation": self.sprites["player_attack"]}
        self.player = Player(player_anims, 100, 100)

        # Create enemy
        enemy_anims = {"enemy_idle": self.sprites["enemy_idle"]}
        self.enemy = Enemy(enemy_anims, 500, 500)

        # Projectiles
        self.projectile = Projectile({"projectile": self.sprites["projectile"]}, 50, 50)

        self.projectiles = [] # Keep track of projectiles in world

        # Define collision sprites
        self.collision_sprites = [81, 112, 69, 101, 91, 71, 113, 79, 102]

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

        # Tile collisions
        for y in self.tilemap.map:
            for x in y:     
                if self.player.rect.colliderect(x.rect) and x.sprite_id in self.collision_sprites:
                    print("Collision") 

        for p in self.projectiles:
            p.update(dt)

        self.player.update(dt)
        self.projectile.update(dt)
        self.enemy.update(dt)
        self.camera.update(dt)
    
    def render(self) -> None:
        # Clear screen
        self.screen.fill((30, 124, 184)) # Water background color

        # for e in self.entities:
        #     e.render(self.screen)
        for y in self.tilemap.map:
            for x in y:
                self.screen.blit(x.sprite, (x.x + self.camera.get_camera_adjustment()[0], 
                                            x.y + self.camera.get_camera_adjustment()[1]))

        self.tilemap.render(self.screen, self.camera.get_camera_adjustment())
        self.player.render(self.screen, self.camera.get_camera_adjustment())
        self.projectile.render(self.screen, self.camera.get_camera_adjustment())

        for p in self.projectiles:
            p.render(self.screen, self.camera.get_camera_adjustment())

        self.enemy.render(self.screen, self.camera.get_camera_adjustment())

        # Update display
        pygame.display.update()
    
    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

            # Attack controls
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.attack()
                p = Projectile({"projectile": self.sprites["projectile"]}, self.player.x, self.player.y)
                p.set_direction(self.player.direction)
                self.projectiles.append(p)

            if event.type == pygame.KEYDOWN and event.key in self.keybinds:

                # The moment a key is pressed, add it to the keystack
                self.keystack.append(event.key)
                # print(self.keystack)

            if event.type == pygame.KEYUP and event.key in self.keybinds:

                # If the key is released, remove it from the keystack
                self.keystack.remove(event.key)
                # print(self.keystack)

                # if self.keybinds[event.key][1] == self.player.direction:
                #     self.player.moving = False

            # Read latest element in keystack
            if len(self.keystack) > 0: # If keystack has any keys
                if self.current_key != self.keystack[-1]: # If the active key has changed
                    # Deactivate animation
                    # self.player.animations.deactivate_animation()

                    self.current_key = self.keystack[-1]

                    # Player commands
                    self.player.set_direction(self.keybinds[self.current_key][1])
                    self.player.start_moving("walking_" + self.keybinds[event.key][1])

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

        self.previous_time = None

        # Create buttons
        self.quit_button = Button(500, 400, "Quit Game")
        self.restart_button = Button(480, 300, "Restart Game")

        # Create button events
        def quit_button():
            self.manager.quit = True
        def restart_button():
            self.manager.scenes["start"] = StartScene(self.manager, self.screen, self.sprites, self.debug) # Reset start scene
            self.manager.set_scene("start")

        self.quit_button.register_event(quit_button)
        self.restart_button.register_event(restart_button)

        self.buttons = [self.quit_button, self.restart_button]

    def update(self) -> None:
        if self.previous_time is None: # First run through the loop needs a previous_time value to compute delta time
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now 

        mouse_x, mouse_y = pygame.mouse.get_pos() # Get mouse coords

        for b in self.buttons: # Check mouse over buttons
            if b.hovered == False and b.rect.collidepoint(mouse_x, mouse_y):
                b.hovered = True
            if b.hovered == True and not b.rect.collidepoint(mouse_x, mouse_y):
                b.hovered = False

        self.quit_button.update(dt)
        self.restart_button.update(dt)
    
    def render(self) -> None:
        self.screen.fill((59, 3, 3))

        self.quit_button.render(self.screen)
        self.restart_button.render(self.screen)

        pygame.display.update()

    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

            # Mouse detection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                for b in self.buttons:
                    if b.hovered:
                        b.event() # If the button is hovered when mouse is clicked, activate the button's event

# Main menu
class Menu(Scene):
    def __init__(self, manager: SceneManager, screen: pygame.Surface, sprites: dict, debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)

        self.previous_time = None

        # Create buttons
        self.quit_button = Button(500, 400, "Quit Game")
        self.start_button = Button(500, 300, "Start Game")

        # Create button events
        def quit_button():
            self.manager.quit = True
        def start_button():
            self.manager.set_scene("start")

        self.quit_button.register_event(quit_button)
        self.start_button.register_event(start_button)

        self.buttons = [self.quit_button, self.start_button]

    def update(self) -> None:
        if self.previous_time is None: # First run through the loop needs a previous_time value to compute delta time
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now 

        mouse_x, mouse_y = pygame.mouse.get_pos() # Get mouse coords

        for b in self.buttons: # Check mouse over buttons
            if b.hovered == False and b.rect.collidepoint(mouse_x, mouse_y):
                b.hovered = True
            if b.hovered == True and not b.rect.collidepoint(mouse_x, mouse_y):
                b.hovered = False

        self.quit_button.update(dt)
        self.start_button.update(dt)
    
    def render(self) -> None:
        self.screen.fill("black")

        self.quit_button.render(self.screen)
        self.start_button.render(self.screen)

        pygame.display.update()

    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

            # Mouse detection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                for b in self.buttons:
                    if b.hovered:
                        b.event() # If the button is hovered when mouse is clicked, activate the button's event


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
                  "gameover": GameOverScene(self.scene_manager, self.screen, self.sprites, self.debug),
                  "menu": Menu(self.scene_manager, self.screen, self.sprites, self.debug)}
        self.scene_manager.initialize(scenes, "gameover")

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

        sprites["player_walk"] = pygame.image.load("gfx/player_animations.png").convert_alpha()
        sprites["player_attack"] = pygame.image.load("gfx/attack.png").convert_alpha()
        sprites["environment_tiles"] = pygame.image.load("gfx/rpg_sprites.png").convert_alpha()
        sprites["enemy_idle"] = pygame.image.load("gfx/enemy_idle.png").convert_alpha()
        sprites["projectile"] = pygame.image.load("gfx/projectile.png").convert_alpha()

        return sprites
    
    # Set debug mode on or off
    def set_debug(self, debug: bool) -> None:
        self.debug = debug


# Main code
g = Game()
# g.set_debug(True)
g.run()
