import pygame, sys, utils
from pygame.locals import *
import pygame.mixer # depends on mixer, you should have SDL_mixer

pygame.init()
pygame.mixer.init(frequency=44100, buffer=1024)
pygame.mixer.set_num_channels(16)
fpsClock = pygame.time.Clock()
windowSurfaceObj = pygame.display.set_mode((utils.winWidth, utils.winHeight))
pygame.display.set_caption('Music Player')

mousex, mousey = 0, 0
currNoteState = [0] * utils.numNotes
keyRects = []
for note, val in enumerate(currNoteState):
    keyRects.append(utils.makeNoteRect(note, 20))
currNoteMapping = {K_a : 0, K_w: 1, K_s : 2, K_e : 3, K_d: 4, K_f: 5, K_j: 6, K_i: 7, K_k: 8, K_o: 9, K_l: 10, K_SEMICOLON:11}
soundMapping = utils.initSoundMappings()
#the midi mapping is for being a feature for the data
midiNoteMapping = {0 : 74, 1: 75, 2: 76, 3: 77, 4: 78, 5: 79, 6: 80, 7: 81, 8: 82, 9: 83, 10: 84, 11: 85}
allNotes = []

modelRects = [] #(note, (left, top, width, height))
noteRects = [] #(note, (left, top, width, height))

while True:
    windowSurfaceObj.fill(utils.blackColor)
    noteRects = utils.updateNoteRects(noteRects, currNoteState)
    for rect in keyRects:
        pygame.draw.rect(windowSurfaceObj, utils.getNoteColor(rect[0]), rect[1])
    for rect in noteRects:
        pygame.draw.rect(windowSurfaceObj, utils.getNoteColor(rect[0]), rect[1])
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.mixer.quit()
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
                noteRects.append(utils.makeNoteRect(noteNum, 1))
                soundMapping[noteNum].play(loops=-1)
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
        elif event.type == KEYUP:
            if event.key in currNoteMapping:
                noteNum = currNoteMapping[event.key]
                currNoteState[noteNum] = 0
                print noteNum, " : ", currNoteState[noteNum]
                lastNote = next(x for x in reversed(allNotes) if x[0] == noteNum)
                lastNote[2] = pygame.time.get_ticks()
                soundMapping[noteNum].stop()
                print lastNote

    pygame.display.update()
    fpsClock.tick(60)
