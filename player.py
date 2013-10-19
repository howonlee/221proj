import pygame, sys
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

winHeight = 900
winWidth = 1440
windowSurfaceObj = pygame.display.set_mode((winWidth, winHeight))
pygame.display.set_caption('Music Player')

blackColor = pygame.Color(0, 0, 0)
whiteColor = pygame.Color(255, 255, 255)
def getNoteColor(note):
    notehash = ((note + 5) * 2654435761) % (2 ** 32)
    r = (notehash & 0xFF0000) >> 16
    g = (notehash & 0x00FF00) >> 8
    b = (notehash & 0x0000FF)
    return pygame.Color(r, g, b)
def makeNoteRect(note, height):
    left = ((winWidth / len(currNoteState)) * note) + 5
    top = (winHeight / 5) * 4
    width = 50
    return [note, [left, top, width, height]]

mousex, mousey = 0, 0
currNoteState = [0] * 12
keyRects = []
for note, val in enumerate(currNoteState):
    keyRects.append(makeNoteRect(note, 20))
currNoteMapping = {K_a : 0, K_w: 1, K_s : 2, K_e : 3, K_d: 4, K_f: 5, K_j: 6, K_i: 7, K_k: 8, K_o: 9, K_l: 10, K_SEMICOLON:11}
allNotes = []
noteRects = [] #note, (left, top, width, height)


def updateNoteRects():
    global noteRects
    for rect in noteRects:
        note = rect[0]
        rect[1][1] -= 1 #move top up
    for note, val in enumerate(currNoteState):
        if val:
            lastRect = next(x for x in reversed(noteRects) if x[0] == note)
            lastRect[1][3] += 1 #increase height

while True:
    windowSurfaceObj.fill(blackColor)
    updateNoteRects()
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
                noteRects.append(makeNoteRect(noteNum, 1))
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

