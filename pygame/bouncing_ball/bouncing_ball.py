import pygame, time, random

class Entity:
    def __init__(self, 
                 x_spawn: float, 
                 y_spawn: float, 
                 velocity: float, 
                 sprite: pygame.Surface) -> None:
        
        self.x = x_spawn
        self.y = y_spawn
        self.velocity = velocity
        self.sprite = sprite

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass

class Player(Entity):
    def __init__(self, 
                 x_spawn: float, 
                 y_spawn: float, 
                 velocity: float, 
                 gravity_constant: float, 
                 sprite: pygame.Surface) -> None:
        
        super().__init__(x_spawn, y_spawn, velocity, sprite)
        self.gravity_constant = gravity_constant
        self.rect = self.sprite.get_rect()

        # Sounds
        self.jump_sound = pygame.mixer.Sound("sfx/bounce.wav")
        self.jump_sound.set_volume(0.1)
        self.death_sound = pygame.mixer.Sound("sfx/death.wav")
        self.death_sound.set_volume(0.5)

    def update(self, dt: float) -> None:
        # Update player
        self.y += self.velocity * dt
        self.velocity += self.gravity_constant * dt
        # Update bounding rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def render(self, screen: pygame.Surface) -> None: 
        # Draw player
        screen.blit(self.sprite, (self.x, self.y))

    def play_jump_sound(self) -> None:
        self.jump_sound.play()

    def play_death_sound(self) -> None:
        self.death_sound.play()

    def info(self) -> str:
        return str(self.rect) # Bounding rect info

# Represents a single Flappy Bird style obstacle. An obstacle is defined
# as a collection of blocks with a gap for the player to fly through.
class Obstacle(Entity):

    # Represents a single block of an obstacle
    class ObstacleBlock(Entity):
        def __init__(self, 
                    x_spawn: float, 
                    y_spawn: float, 
                    velocity: float, 
                    sprite: pygame.Surface) -> None:
            
            super().__init__(x_spawn, y_spawn, velocity, sprite)
            self.rect = self.sprite.get_rect()

        def update(self, dt) -> None:
            self.x += self.velocity * dt
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

        def render(self, screen: pygame.Surface) -> None:
            screen.blit(self.sprite, (self.x, self.y))

        def info(self) -> str:
            return str(self.x)

    def __init__(self, 
                 x_spawn: float, 
                 y_spawn: float, 
                 velocity: float, 
                 screen_height: int,
                 gap_height: int, # Number of blocks missing to form gap
                 gap_loc: int, # Number of blocks from the top of the screen the gap is located at
                 sprite: pygame.Surface) -> None: # Block sprite

        super().__init__(x_spawn, y_spawn, velocity, sprite)
        self.screen_height = screen_height
        self.BLOCK_SIZE = 48 # The size of the sprite for a single block

        # Calculate number of blocks required to fill screen
        self.num_blocks = round(self.screen_height/self.BLOCK_SIZE)

        # Calculate gap
        self.gap_range = (gap_loc, gap_loc + gap_height)

        # Create blocks
        self.blocks = self.create_blocks()

        self.passed = False # Track if the player has passed this obstacle

    # -- Create blocks --
    # The reason we break down the obstacles into blocks is to allow for obstacles with
    # gaps at different locations, like those in the original Flappy Bird.
    def create_blocks(self) -> list[ObstacleBlock]:
        o = []
        current_block = 0
        for i in range(self.num_blocks):
            if i < self.gap_range[0] or i > self.gap_range[1]:
                o.append(Obstacle.ObstacleBlock(self.x, # Block y value
                                                current_block, 
                                                self.velocity, 
                                                self.sprite))        
            current_block += self.BLOCK_SIZE
        return o

    def update(self, dt) -> None:
        self.x += self.velocity * dt
        # Update obstacle
        for b in self.blocks:
            b.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        for b in self.blocks:
            b.render(screen)

    def info(self) -> str:
        result = []
        for b in self.blocks:
            result.append(b.info())
        return "Obstacle debug"

# Manages the obstacles and collisions between obstacles and 
# the player
class Environment:
    def __init__(self, 
                 obstacle_velocity: float, 
                 freq: int,
                 obstacle_gap: int,
                 screen: pygame.Surface,
                 sprites: dict,
                 player: Player) -> None:
        
        self.obstacles = [] # Contains all the obstacles currently active
        self.obstacle_spawn_point = 1280 # Obstacles spawn just off screen to the right
        self.obstacle_velocity = obstacle_velocity
        self.new_obstacle_timer = 0 
        self.obstacle_gap = obstacle_gap # Size of gap in obstacles
        self.freq = freq # Obstacle frequency
        self.screen = screen
        self.sprites = sprites
        self.player = player
        self.score_tracker = 0 # Tracks how many times the player has passed an obstacle

    def remove_obstacle(self) -> None:
        self.obstacles.pop(0) # Remove the oldest obstacle from the list

    def add_obstacle(self, obstacle: Obstacle) -> None:
        self.obstacles.append(obstacle)

    def update_obstacles(self, dt) -> None:
        for o in self.obstacles:
            o.update(dt)
            if o.x < -200: # Remove obstacle if it has reached the edge of the screen
                self.remove_obstacle()

            # Check for player passing obstacle
            if o.x < self.player.x and not o.passed:
                o.passed = True
                self.score_tracker += 1

        if self.new_obstacle_timer > self.freq: # Time to spawn a new obstacle

            # Randomize gap location
            gap = random.randint(2,10)

            o = Obstacle(self.obstacle_spawn_point,
                0,
                self.obstacle_velocity,
                self.screen.get_height(),
                self.obstacle_gap,
                gap,
                self.sprites["obstacle"])
            self.add_obstacle(o)
            self.new_obstacle_timer = 0

        self.new_obstacle_timer += 1

    def update(self, dt) -> None:
        self.update_obstacles(dt)

    def render(self, screen: pygame.Surface) -> None:
        for o in self.obstacles:
            o.render(screen)

    def info(self) -> list[str]:
        obstacles_info = []
        for o in self.obstacles:
            obstacles_info.append(o.info())
        return obstacles_info 

# Debugging text to be displayed on the screen if game is started in debug mode
class DebugText:
    def __init__(self, x: int, y: int, player: Player, env: Environment) -> None:
        self.player = player
        self.env = env
        self.font = pygame.font.SysFont("Arial", 12)
        self.text = self.create_debug_text()
        self.rendered = self.font.render(self.text, True, "white")
        self.x = x
        self.y = y

    def create_debug_text(self) -> str:
        debug1 = str(self.env.info())
        debug2 = str(self.player.info())
        return debug1 + " " + debug2

    def update(self) -> None:
        self.text = self.create_debug_text()

    def render(self, screen: pygame.Surface) -> None:
        self.rendered = self.font.render(self.text, True, "white")
        screen.blit(self.rendered, (self.x, self.y)) 

# Stores the score to render as text to the screen.
class Score:
    def __init__(self, x, y) -> None:
        self.font = pygame.font.SysFont("Calibri", 36)
        self.score = 0
        self.text = str(self.score)
        self.x = x
        self.y = y

    # Adds 1 to the score
    def add_score(self) -> None:
        self.score += 1

    def update(self) -> None:
        self.text = str(self.score)

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.font.render(self.text, True, "white"), (self.x, self.y))

# Handles switching between scenes
class SceneManager:
    def __init__(self) -> None:
        self.scenes = {}
        self.quit = False

    def initialize(self, scenes: dict, starting_scene: str) -> None:
        self.scenes = scenes
        self.current_scene = self.scenes[starting_scene]

    def set_scene(self, new_scene: str) -> None:
        self.current_scene = self.scenes[new_scene]

    def get_scene(self) -> None:
        return self.current_scene
    
    # Resets main scene
    def reset_main(self) -> None:
        new_scene = MainScene(self, 
                              self.scenes["main"].screen,  
                              self.scenes["main"].sprites, 
                              self.scenes["main"].debug)
        self.scenes["main"] = new_scene

    def quit_game(self) -> None:
        self.quit = True


# A scene is a collection of objects that are set to be updated and rendered
# in any given frame. It allows us to quickly switch between, for instance, a start menu
# and the main game scene, or different areas in an RPG.
class Scene:
    def __init__(self, manager: SceneManager, 
                 screen: pygame.Surface, 
                 sprites: dict,
                 debug: bool) -> None:
        self.manager = manager
        self.screen = screen
        self.sprites = sprites
        self.debug = debug

    def update(self) -> None:
        pass

    def render(self) -> None:
        pass

    def poll_events(self) -> None:
        pass

# Start menu
class StartScene(Scene):
    def __init__(self, manager: SceneManager, 
                 screen: pygame.Surface, 
                 sprites: dict,
                 debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)
        self.font = pygame.font.SysFont("Arial", 36)
        self.text = "Press Space to begin."
        self.text_x = 400
        self.text_y = 200

    def update(self) -> None:
        pass

    def render(self) -> None:
        # Clear screen
        self.screen.fill("black")

        self.screen.blit(self.font.render(self.text, True, "white"), (self.text_x, self.text_y))       

        # Update the display
        pygame.display.update() 

    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

            if event.type == pygame.KEYDOWN: # If a key has been pressed

                if event.key == pygame.K_SPACE:
                    self.manager.set_scene("main")

# Main game scene
class MainScene(Scene):

    def __init__(self, 
                 manager: SceneManager, 
                 screen: pygame.Surface, 
                 sprites: dict, 
                 debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)

        # GAME PARAMS #
        self.GRAVITY_CONSTANT = 1700
        self.PLAYER_VEL = 200
        self.JUMP_CONSTANT = -450
        self.OBS_FREQ = 800
        self.OBS_VEL = -200
        self.OBS_GAP = 2

        self.previous_time = None

        # Set up player
        self.player = Player(self.screen.get_width()/2, 
                             self.screen.get_height()/2, 
                             self.PLAYER_VEL, 
                             self.GRAVITY_CONSTANT,
                             self.sprites["player"]) 
        
        # Set up environment
        self.env = Environment(self.OBS_VEL, 
                               self.OBS_FREQ,
                               self.OBS_GAP,
                               self.screen,
                               self.sprites,
                               self.player) # Environment has access to entire sprite dictionary
        
        # Set up score
        self.score = Score(self.screen.get_width()/2, 50)

        self.debug_text = DebugText(50, 50, self.player, self.env)

    def update(self) -> None:

        if self.previous_time is None: # First run through the loop needs a previous_time value to compute delta time
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now 

        # Update player
        self.player.update(dt)
        # Update environment
        self.env.update(dt)

        # Check death conditions
        if self.player_collision() or self.player.y > self.screen.get_height() - 30:
            self.player.play_death_sound()
            self.manager.set_scene("death")

        # Update score if player passes an obstacle
        if self.env.score_tracker > self.score.score:
            self.score.add_score()
        
        # Update score text
        self.score.update()

        # Update debug text
        if self.debug:  
            self.debug_text.update()

    def render(self) -> None:
        # Clear screen
        self.screen.fill("black")

        # Draw background
        self.screen.blit(self.sprites["background"], (0, 0))

        # Draw player
        self.player.render(self.screen)
        # Draw environment
        self.env.render(self.screen)
        # Draw score
        self.score.render(self.screen)

        if self.debug:
            self.debug_text.render(self.screen)

        # Update the display
        pygame.display.update() 

    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

            if event.type == pygame.KEYDOWN: # If a key has been pressed

                if event.key == pygame.K_SPACE:
                    self.player.velocity = self.JUMP_CONSTANT # Jump!
                    self.player.play_jump_sound()

    # Checks for a player collision with an obstacle.
    # Returns True if a collision is detected.
    def player_collision(self) -> bool:
        for o in self.env.obstacles:
            for b in o.blocks:
                if b.rect.colliderect(self.player.rect):
                    return True
        return False

# Death screen
class DeathScene(Scene):
    def __init__(self, manager: SceneManager, 
                 screen: pygame.Surface, 
                 sprites: dict, 
                 debug: bool) -> None:
        super().__init__(manager, screen, sprites, debug)
        self.font = pygame.font.SysFont("Arial", 36)
        self.text = "You died! Press space to restart."
        self.text_x = 400
        self.text_y = 200

    def update(self) -> None:
        pass

    def render(self) -> None:
        # Clear screen
        self.screen.fill((59, 3, 3))

        self.screen.blit(self.font.render(self.text, True, "white"), (self.text_x, self.text_y))
        # Update the display
        pygame.display.update() 

    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()

            if event.type == pygame.KEYDOWN: # If a key has been pressed

                if event.key == pygame.K_SPACE:
                    self.manager.reset_main()
                    self.manager.set_scene("main")



# Main game class
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
                  "main": MainScene(self.scene_manager, self.screen, self.sprites, self.debug), 
                  "death": DeathScene(self.scene_manager, self.screen, self.sprites, self.debug)}
        self.scene_manager.initialize(scenes, "start")

        # Play music
        pygame.mixer.music.load("sfx/music.wav")
        # pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.1)

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

        sprites["player"] = pygame.image.load("gfx/ball.png").convert_alpha()
        sprites["obstacle"] = pygame.image.load("gfx/block.png").convert_alpha()
        sprites["background"] = pygame.image.load("gfx/bg.png").convert_alpha()

        return sprites
    
    # Set debug mode on or off
    def set_debug(self, debug: bool) -> None:
        self.debug = debug


# Main code
g = Game()
# g.set_debug(True)
g.run()

