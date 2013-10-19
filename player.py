import pygame, sys
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

windowSurfaceObj = pygame.display.set_mode((640, 640))
pygame.display.set_caption('Music Player')

blackColor = pygame.Color(0, 0, 0)
redColor = pygame.Color(255, 0, 0)
greenColor = pygame.Color(0, 255, 0)
blueColor = pygame.Color(0, 0, 255)
whiteColor = pygame.Color(255, 255, 255)
mousex, mousey = 0, 0

while True:
    windowSurfaceObj.fill(blackColor)
    pygame.draw.rect(windowSurfaceObj, whiteColor, (10, 10, 50, 100))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEMOTION:
            mousex, mousey = event.pos
        elif event.type == MOUSEBUTTONUP:
            if event.button in (1, 2, 3):
                print "mouse click"
            if event.button in (4, 5):
                print "scroll mouse"

        elif event.type == KEYDOWN:
            if event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
                print "Arrow key"
            if event.key == K_a:
                print "a pressed"
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))

    pygame.display.update()
    fpsClock.tick(60)

