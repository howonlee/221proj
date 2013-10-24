import pygame, sys, numpy, math
from pygame.locals import *

winHeight = 900
winWidth = 1440
numNotes = 12
blackColor = pygame.Color(0, 0, 0)
whiteColor = pygame.Color(255, 255, 255)
currNoteMapping = {K_a : 0, K_w: 1, K_s : 2, K_e : 3, K_d: 4, K_f: 5, K_j: 6, K_i: 7, K_k: 8, K_o: 9, K_l: 10, K_SEMICOLON:11}
#the midi mapping is for being a feature for the data
midiNoteMapping = {}
for i in range(67, 97):
    midiNoteMapping[i - 72] = i
reverseMidiNoteMapping = dict((v,k) for k,v in midiNoteMapping.items())

def getNoteColor(note):
    notehash = ((note + 5) * 2654435761) % (2 ** 32)
    r = (notehash & 0xFF0000) >> 16
    g = (notehash & 0x00FF00) >> 8
    b = (notehash & 0x0000FF)
    return pygame.Color(r, g, b)

def initSoundMappings():
    soundMappings = {}
    for i in range(numNotes):
        soundMappings[i] = pygame.sndarray.make_sound(bufs[i])
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

"""
NOTE TONE GENERATION
"""
freqs = [523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61, 880.0, 932.32, 987.76]
duration = 1.0 #seconds
sample_rate = 44100
n_samples = int(round(duration * sample_rate))
bufs = []
for i in range(numNotes):
    bufs.append(numpy.zeros((n_samples, 2), dtype=numpy.int16))
    max_sample = 2 ** (16 - 1) - 1
    for s in range(n_samples):
        t = float(s) / sample_rate #time in seconds
        bufs[i][s][0] = int(round(max_sample*(math.cos(2*math.pi*freqs[i]*t)) ** 20))
        bufs[i][s][1] = int(round(max_sample*(math.cos(2*math.pi*freqs[i]*t)) ** 20))
