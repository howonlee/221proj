import pygame, sys, utils, model, operator
from pygame.locals import *
import pygame.mixer # depends on mixer, you should have SDL_mixer
import numpy as np

class Game:
    def __init__(self, showPredictions=True, confMatFile="./confmatrix.txt"):
        self.showPredictions = showPredictions
        self.currNoteState = [0] * utils.numNotes
        self.predictionState = [False] * utils.numNotes
        self.keyRects = []
        for note, val in enumerate(self.currNoteState):
            self.keyRects.append(utils.makeNoteRect(note, utils.numNotes))
        self.allNotes = []
        self.modelRects = [] #(note, (left, top, width, height))
        self.noteRects = [] #(note, (left, top, width, height))
        self.soundMapping = utils.initSoundMappings()
        #MODELS#
        self.confMatrix = np.zeros((utils.numNotes, utils.numNotes), dtype=np.int)
        self.confMatFile = confMatFile
        self.nbModel = model.trainNB(model.jsb["train"])

    def predict(self, model, fn):
        #curry into this function
        data = map(operator.itemgetter(0), self.allNotes[-5:])
        data = map(lambda x: utils.midiNoteMapping[x], data)
        pred = fn(data, model[0], model[1])
        self.predictionState = map(lambda x: False, self.predictionState)
        self.predictionState[utils.reverseMidiNoteMapping[pred]] = True

    def predictNB(self):
        self.predict(self.nbModel, model.makeNBPred)

    def turnNoteOn(self, noteNum):
        self.soundMapping[noteNum].play(loops=-1)
        self.currNoteState[noteNum] = 1
        print noteNum, " : ", self.currNoteState[noteNum]
        print "current note: ", utils.midiNoteMapping[noteNum]
        if True in self.predictionState:
            predicted = self.predictionState.index(True)
            self.confMatrix[noteNum, predicted] += 1
        note = [noteNum, pygame.time.get_ticks(), -1]
        print note
        self.noteRects.append(utils.makeNoteRect(noteNum, 1))
        self.allNotes.append(note)
        if (len(self.allNotes) > 5):
            self.predictNB()

    def turnNoteOff(self, noteNum):
        self.soundMapping[noteNum].stop()
        self.currNoteState[noteNum] = 0
        print noteNum, " : ", self.currNoteState[noteNum]
        lastNote = next(x for x in reversed(self.allNotes) if x[0] == noteNum)
        lastNote[2] = pygame.time.get_ticks()
        print lastNote

    def drawRectSet(self, rects):
        for rect in rects:
            color = utils.getNoteColor(rect[0], False)
            if self.showPredictions:
                color = utils.getNoteColor(rect[0], self.predictionState[rect[0]])
            pygame.draw.rect(windowSurfaceObj, color, rect[1])


if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan)
    pygame.init()
    pygame.mixer.init(44100, -16, 2, buffer=512)
    pygame.mixer.set_num_channels(12)
    fpsClock = pygame.time.Clock()
    windowSurfaceObj = pygame.display.set_mode((utils.winWidth, utils.winHeight))
    pygame.display.set_caption('Music Player')
    gObj = Game()
    while True:
        windowSurfaceObj.fill(utils.blackColor)
        gObj.noteRects = utils.updateNoteRects(gObj.noteRects, gObj.currNoteState)
        gObj.drawRectSet(gObj.keyRects)
        gObj.drawRectSet(gObj.noteRects)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))
                if event.key == K_SPACE:
                    #this is so that the confusion matrix ends up
                    #as an awesome latex matrix
                    np.savetxt(gObj.confMatFile, gObj.confMatrix, "%d", delimiter=" & ", newline=' \\\\\n')
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    gObj.turnNoteOn(noteNum)
            elif event.type == KEYUP:
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    gObj.turnNoteOff(noteNum)
        pygame.display.update()
        fpsClock.tick(60)
