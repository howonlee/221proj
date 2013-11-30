import pygame, sys, utils, model, operator
from pygame.locals import *
import pygame.mixer # depends on mixer, you should have SDL_mixer
import numpy as np

class Game:
    def __init__(self, showPredictions=True, predictor="MM", confMatFile="./confmatrix.txt"):
        self.showPredictions = showPredictions
        self.currNoteState = [0] * utils.numNotes
        self.predictionState = [False] * utils.numNotes
        self.keyRects = []
        if predictor not in ["MM", "MM3", "HMM", "Q"]:
            predictor = "MM"
        self.predictor = predictor
        for note, val in enumerate(self.currNoteState):
            self.keyRects.append(utils.makeNoteRect(note, utils.numNotes))
        self.allNotes = []
        self.modelRects = [] #(note, (left, top, width, height))
        self.noteRects = [] #(note, (left, top, width, height))
        self.soundMapping = utils.initSoundMappings()
        #MODELS#
        self.confMatrix = np.zeros((utils.numNotes, utils.numNotes), dtype=np.int)
        self.confMatFile = confMatFile
        self.mmModel = model.trainMM(model.jsb["train"])
        self.mmModel3 = model.trainMMOrder3(model.jsb["train"])
        self.hmmModel = model.trainHMM(model.jsb["train"])
        self.qModel = model.trainQLearning(model.jsb["train"])

    def predictNotes(self):
        if self.predictor == "MM":
            self.predict(self.mmModel, model.makeMMPred)
        elif self.predictor == "MM3":
            self.predict(self.mmModel3, model.makeMM3Pred)
        elif self.predictor == "HMM":
            self.predict(self.hmmModel, model.makeHMMPred)
        elif self.predictor == "Q":
            self.predict(self.qModel, model.makeQLearningPred)

    def predict(self, model, fn):
        #curry into this function
        data = map(operator.itemgetter(0), self.allNotes[-10:])
        data = map(lambda x: utils.midiNoteMapping[x], data)
        pred = fn(data, model[0], model[1])
        self.predictionState = map(lambda x: False, self.predictionState)
        self.predictionState[utils.reverseMidiNoteMapping[pred]] = True

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
        if (len(self.allNotes) > 10):
            self.predictNotes()

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

    def saveData(self):
        #need to record memory data, too
        np.savetxt(self.confMatFile, self.confMatrix, "%d", delimiter=" & ", newline=' \\\\\n')


if __name__ == "__main__":
    assert(len(sys.argv) < 3)
    predOpt = "MM"
    if len(sys.argv) == 2: #means that we have a pred
        predOpt = str(sys.argv[1])
        print predOpt
    np.set_printoptions(threshold=np.nan)
    pygame.init()
    pygame.mixer.init(44100, -16, 2, buffer=512)
    pygame.mixer.set_num_channels(12)
    pygame.time.set_timer(USEREVENT+1, 1000) #for saving data
    fpsClock = pygame.time.Clock()
    windowSurfaceObj = pygame.display.set_mode((utils.winWidth, utils.winHeight))
    pygame.display.set_caption('Music Player')
    g = Game(predictor = predOpt)
    while True:
        windowSurfaceObj.fill(utils.blackColor)
        g.noteRects = utils.updateNoteRects(g.noteRects, g.currNoteState)
        g.drawRectSet(g.keyRects)
        g.drawRectSet(g.noteRects)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    g.turnNoteOn(noteNum)
            elif event.type == KEYUP:
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    g.turnNoteOff(noteNum)
            elif event.type == USEREVENT + 1:
                g.saveData()
        pygame.display.update()
        fpsClock.tick(60)
