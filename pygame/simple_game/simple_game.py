import pygame, time, random

class Entity:
    def __init__(self, 
                 x: float, 
                 y: float, 
                 sprite: pygame.Surface) -> None:
        
        self.x = x
        self.y = y
        self.sprite = sprite

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass

class Collectible(Entity):
    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        super().__init__(x, y, sprite)
        self.rect = self.sprite.get_rect()

    def randomize_position(self) -> None:
        self.x = random.randint(50, 1250)
        self.y = random.randint(50, 670)
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))

class Player(Entity):
    def __init__(self, x: float, 
                 y: float, 
                 sprite: pygame.Surface,
                 boundaries: tuple) -> None:
        super().__init__(x, y, sprite)
        self.angle = 0 # Orientation of player
        self.direction = "up" # Orientation not tied to angle
        self.velocity = 200 # Speed of player
        self.moving = False # Is player moving
        self.boundaries = boundaries
        self.rect = self.sprite.get_rect()

    def update(self, dt) -> None:
        if self.moving:
            self.move(dt)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))

    def set_angle(self, new_angle: int) -> None:
        rotation = new_angle - self.angle
        self.sprite = pygame.transform.rotate(self.sprite, rotation)
        self.angle = new_angle

    def set_direction(self, new_dir: str) -> None:
        self.direction = new_dir
 
    def move(self, dt) -> None:
        if self.direction == "up":
            self.y -= self.velocity * dt
        elif self.direction == "down":
            self.y += self.velocity * dt       
        elif self.direction == "left":
            self.x -= self.velocity * dt      
        elif self.direction == "right":
            self.x += self.velocity * dt
        
        # Prevent player from exiting the screen
        self.x = min((self.boundaries[0] - 48), self.x)
        self.x = max((0, self.x))

        self.y = min((self.boundaries[1] - 48, self.y))
        self.y = max((0, self.y))
           

class Text:
    def __init__(self, x, y, text) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.SysFont("Calibri", 36)

    def set_text(self, new_text: str) -> None:
        self.text = new_text

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        self.rendered = self.font.render(self.text, True, "white")
        screen.blit(self.rendered, (self.x, self.y)) 

# Main game class
class Game:
    def __init__(self) -> None:
        # Initialize global game variables
        pygame.init() 
        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.sprites = self.load_sprites()
        self.score = 0

        # Keybinds
        self.keybinds = {pygame.K_w: (0, "up"),
                         pygame.K_d: (270, "right"),
                         pygame.K_s: (180, "down"),
                         pygame.K_a: (90, "left")}

        # Initialize game entities
        self.player = Player(50, 
                             50, 
                             self.sprites["spaceship"], 
                             (self.screen.get_width(), self.screen.get_height()))
        self.collectible = Collectible(0, 0, self.sprites["collectible"])
        self.collectible.randomize_position()
        self.text = Text(600, 50, "Mouse position: ")

        # Load sounds
        pygame.mixer.music.load("sfx/music.ogg")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play()

        self.collect_sound = pygame.mixer.Sound("sfx/collect.wav")
        self.collect_sound.set_volume(0.5)

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

            if event.type == pygame.KEYDOWN and event.key in self.keybinds:
                self.player.set_angle(self.keybinds[event.key][0])
                self.player.set_direction(self.keybinds[event.key][1])
                self.player.moving = True
            
            if event.type == pygame.KEYUP and event.key in self.keybinds:
                if self.keybinds[event.key][1] == self.player.direction:
                    self.player.moving = False
                

    def update(self) -> None:
        # Compute delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now 

        # Update player
        self.player.update(dt)

        # Check collision between player and collectible
        if self.player.rect.colliderect(self.collectible.rect):
            self.collectible.randomize_position()
            self.collect_sound.play() # Play sound
            # Increase player speed
            self.player.velocity += 100
            self.score += 1

        self.text.update()
        self.text.set_text(str(self.score))

    def render(self) -> None:
        # Clear screen
        self.screen.fill("black")

        # Render background
        self.screen.blit(self.sprites["background"], (0, 0))

        # Render player
        self.player.render(self.screen)

        # Render collectible
        self.collectible.render(self.screen)

        # Render text
        self.text.render(self.screen)

        # Update the display
        pygame.display.update() 

    # Load sprite textures into pygame as surfaces. 
    # Returns a dictionary of names to surfaces.
    def load_sprites(self) -> dict: 
        sprites = {}

        sprites["collectible"] = pygame.image.load("gfx/collectible.png").convert_alpha()
        sprites["background"] = pygame.image.load("gfx/simple_game_bg.png").convert_alpha()
        sprites["spaceship"] = pygame.image.load("gfx/ship.png").convert_alpha()

        # Downscale
        sprites["spaceship"] = pygame.transform.scale(sprites["spaceship"], (48, 48))

        return sprites
    
# Main code
g = Game()
g.run()