import pygame, sys, numpy, math, operator
from pygame.locals import *

winHeight = 900
winWidth = 1440
numNotes = 36
blackColor = pygame.Color(0, 0, 0)
whiteColor = pygame.Color(255, 255, 255)
currNoteMapping = {K_a : 0, K_w: 1, K_s : 2, K_r : 3, K_d: 4, K_f: 5, K_u: 6, K_j: 7, K_o: 8, K_k: 9, K_l: 11, K_SEMICOLON:12}
#the midi mapping is for being a feature for the data
midiNoteMapping = {}
for i in range(67, 97):
    midiNoteMapping[i - 67] = i
reverseMidiNoteMapping = dict((v,k) for k,v in midiNoteMapping.items())

def argmax(pairs):
    return max(pairs, key=operator.itemgetter(1))[0]
def argmax_iter(vals):
    return argmax(enumerate(vals))

def getNoteColor(note, isHighlighted):
    notehash = ((note + 5) * 2654435761) % (2 ** 32)
    r = (notehash & 0xFF0000) >> 16
    g = (notehash & 0x00FF00) >> 8
    b = (notehash & 0x0000FF)
    if (isHighlighted):
        r = 255
        g = 255
        b = 255
    return pygame.Color(r, g, b)

def initSoundMappings():
    soundMappings = {}
    for i in range(numNotes):
        soundMappings[i] = pygame.sndarray.make_sound(bufs[i])
        soundMappings[i].set_volume(0.05)
    return soundMappings

def makeNoteRect(note, height):
    left = ((winWidth / numNotes) * note) + 5
    top = (winHeight / 5) * 4
    width = 25
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
freqs = freqs + map(lambda x: x * 2, freqs) + map(lambda x: x * 4, freqs)
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
