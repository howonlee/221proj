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
currNoteState = [0, 0, 0]
currNoteMapping = {K_a : 0, K_s : 1, K_d : 2}
allNotes = []
rectDir = (100, 0, 0, 30) #top, left, width, height

while True:
    windowSurfaceObj.fill(blackColor)
    pygame.draw.rect(windowSurfaceObj, whiteColor, (10, 10, 50, 100))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in currNoteMapping:
                currNoteState[currNoteMapping[event.key]] = 1
                print currNoteMapping[event.key], " : ", currNoteState[currNoteMapping[event.key]]
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
        elif event.type == KEYUP:
            if event.key in currNoteMapping:
                currNoteState[currNoteMapping[event.key]] = 0
                print currNoteMapping[event.key], " : ", currNoteState[currNoteMapping[event.key]]

    pygame.display.update()
    fpsClock.tick(60)

