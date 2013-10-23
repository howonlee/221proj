import pygame, sys
from pygame.locals import *

winHeight = 900
winWidth = 1440
numNotes = 12
blackColor = pygame.Color(0, 0, 0)
whiteColor = pygame.Color(255, 255, 255)
currNoteMapping = {K_a : 0, K_w: 1, K_s : 2, K_e : 3, K_d: 4, K_f: 5, K_j: 6, K_i: 7, K_k: 8, K_o: 9, K_l: 10, K_SEMICOLON:11}
#the midi mapping is for being a feature for the data
midiNoteMapping = {0 : 74, 1: 75, 2: 76, 3: 77, 4: 78, 5: 79, 6: 80, 7: 81, 8: 82, 9: 83, 10: 84, 11: 85}

def getNoteColor(note):
    notehash = ((note + 5) * 2654435761) % (2 ** 32)
    r = (notehash & 0xFF0000) >> 16
    g = (notehash & 0x00FF00) >> 8
    b = (notehash & 0x0000FF)
    return pygame.Color(r, g, b)

def initSoundMappings():
    soundMappings = {}
    soundMappings[0] = pygame.mixer.Sound("data/sin_c.wav")
    soundMappings[1] = pygame.mixer.Sound("data/sin_csh.wav")
    soundMappings[2] = pygame.mixer.Sound("data/sin_d.wav")
    soundMappings[3] = pygame.mixer.Sound("data/sin_dsh.wav")
    soundMappings[4] = pygame.mixer.Sound("data/sin_e.wav")
    soundMappings[5] = pygame.mixer.Sound("data/sin_f.wav")
    soundMappings[6] = pygame.mixer.Sound("data/sin_fsh.wav")
    soundMappings[7] = pygame.mixer.Sound("data/sin_g.wav")
    soundMappings[8] = pygame.mixer.Sound("data/sin_gsh.wav")
    soundMappings[9] = pygame.mixer.Sound("data/sin_a.wav")
    soundMappings[10] = pygame.mixer.Sound("data/sin_ash.wav")
    soundMappings[11] = pygame.mixer.Sound("data/sin_b.wav")
    return soundMappings

def makeNoteRect(note, height):
    left = ((winWidth / numNotes) * note) + 5
    top = (winHeight / 5) * 4
    width = 50
    return [note, [left, top, width, height]]

def updateNoteRects(noteRects, currNoteState):
    for rect in noteRects:
        note = rect[0]
        rect[1][1] -= 1 #move top up
    for note, val in enumerate(currNoteState):
        if val:
            lastRect = next(x for x in reversed(noteRects) if x[0] == note)
            lastRect[1][3] += 1 #increase height
    return noteRects
