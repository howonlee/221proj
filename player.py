import pygame, sys
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

winHeight = 640
winWidth = 640
windowSurfaceObj = pygame.display.set_mode((winHeight, winWidth))
pygame.display.set_caption('Music Player')

blackColor = pygame.Color(0, 0, 0)
whiteColor = pygame.Color(255, 255, 255)
def getNoteColor(note):
    notehash = ((note + 5) * 2654435761) % (2 ** 32)
    r = (notehash & 0xFF0000) >> 16
    g = (notehash & 0x00FF00) >> 8
    b = (notehash & 0x0000FF)
    print "r: ", r
    print "g: ", g
    print "b: ", b
    return pygame.Color(r, g, b)

mousex, mousey = 0, 0
currNoteState = [0, 0, 0]
keyRects = []
for note, val in enumerate(currNoteState):
    top = ((winHeight / len(currNoteState)) * note) + 5
    left = (winWidth / 4) * 3
    width = 50
    height = 20
    keyRects.append([note, [top, left, width, height]])
currNoteMapping = {K_a : 0, K_s : 1, K_d : 2}
allNotes = []
noteRects = [] #note, (top, left, width, height)

while True:
    windowSurfaceObj.fill(blackColor)
    for rect in keyRects:
        pygame.draw.rect(windowSurfaceObj, getNoteColor(rect[0]), rect[1])
    for rect in noteRects:
        pygame.draw.rect(windowSurfaceObj, getNoteColor(rect[0]), rect[1])
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in currNoteMapping:
                noteNum = currNoteMapping[event.key]
                currNoteState[noteNum] = 1
                print noteNum, " : ", currNoteState[noteNum]
                note = [noteNum, pygame.time.get_ticks(), -1]
                allNotes.append(note)
                print note
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
        elif event.type == KEYUP:
            if event.key in currNoteMapping:
                noteNum = currNoteMapping[event.key]
                currNoteState[noteNum] = 0
                print noteNum, " : ", currNoteState[noteNum]
                lastNote = next(x for x in reversed(allNotes) if x[0] == noteNum)
                lastNote[2] = pygame.time.get_ticks()
                print lastNote

    pygame.display.update()
    fpsClock.tick(60)

