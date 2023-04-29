import pygame

pygame.init()
running = True
window = pygame.display.set_mode((1280, 720))

while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()