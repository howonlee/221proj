import pygame, sys, utils, model, operator, thread
from pygame.locals import *
import pygame.mixer # depends on mixer, you should have SDL_mixer

pygame.init()
pygame.mixer.init(44100, -16, 2, buffer=512)
pygame.mixer.set_num_channels(12)
fpsClock = pygame.time.Clock()
windowSurfaceObj = pygame.display.set_mode((utils.winWidth, utils.winHeight))
pygame.display.set_caption('Music Player')

currNoteState = [0] * 30
predictionState = [False] * 30
keyRects = []
for note, val in enumerate(currNoteState):
    keyRects.append(utils.makeNoteRect(note, 20))
allNotes = []
modelRects = [] #(note, (left, top, width, height))
noteRects = [] #(note, (left, top, width, height))
soundMapping = utils.initSoundMappings()

#MODELS#
prevPred = -1
confMatrix = []
nbModel = model.trainNB(model.jsb["train"])

while True:
    windowSurfaceObj.fill(utils.blackColor)
    noteRects = utils.updateNoteRects(noteRects, currNoteState)
    for rect in keyRects:
        pygame.draw.rect(windowSurfaceObj, utils.getNoteColor(rect[0], predictionState[rect[0]]), rect[1])
    for rect in noteRects:
        pygame.draw.rect(windowSurfaceObj, utils.getNoteColor(rect[0], predictionState[rect[0]]), rect[1])
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.mixer.quit()
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key in utils.currNoteMapping:
                noteNum = utils.currNoteMapping[event.key]
                soundMapping[noteNum].play(loops=-1)
                currNoteState[noteNum] = 1
                print noteNum, " : ", currNoteState[noteNum]
                print "current note: ", utils.midiNoteMapping[noteNum]
                note = [noteNum, pygame.time.get_ticks(), -1]
                allNotes.append(note)
                nbdata = []
                if (len(allNotes) > 5):
                    nbData = map(operator.itemgetter(0), allNotes[-5:])
                    nbData = map(lambda x: utils.midiNoteMapping[x], nbData)
                    pred = model.makeNBPred(nbData, nbModel[0], nbModel[1])
                    predictionState = map(lambda x: False, predictionState)
                    predictionState[utils.reverseMidiNoteMapping[pred]] = True
                    print "prediction: ", pred
                print note
                noteRects.append(utils.makeNoteRect(noteNum, 1))
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
        elif event.type == KEYUP:
            if event.key in utils.currNoteMapping:
                noteNum = utils.currNoteMapping[event.key]
                soundMapping[noteNum].stop()
                currNoteState[noteNum] = 0
                print noteNum, " : ", currNoteState[noteNum]
                lastNote = next(x for x in reversed(allNotes) if x[0] == noteNum)
                lastNote[2] = pygame.time.get_ticks()
                print lastNote

    pygame.display.update()
    fpsClock.tick(60)
