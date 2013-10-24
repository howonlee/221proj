import pygame, sys, utils, model, operator, thread
from pygame.locals import *
import pygame.mixer # depends on mixer, you should have SDL_mixer

class Game:
    def __init__(self):
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
        self.confMatrix = [] #for later
        self.nbModel = model.trainNB(model.jsb["train"])

if __name__ == "__main__":
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
        for rect in gObj.keyRects:
            pygame.draw.rect(windowSurfaceObj,
                    utils.getNoteColor(rect[0], gObj.predictionState[rect[0]]),
                    rect[1])
        for rect in gObj.noteRects:
            pygame.draw.rect(windowSurfaceObj,
                    utils.getNoteColor(rect[0], gObj.predictionState[rect[0]]),
                    rect[1])
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    gObj.soundMapping[noteNum].play(loops=-1)
                    gObj.currNoteState[noteNum] = 1
                    print noteNum, " : ", gObj.currNoteState[noteNum]
                    print "current note: ", utils.midiNoteMapping[noteNum]
                    note = [noteNum, pygame.time.get_ticks(), -1]
                    gObj.allNotes.append(note)
                    nbdata = []
                    if (len(gObj.allNotes) > 5):
                        nbData = map(operator.itemgetter(0), gObj.allNotes[-5:])
                        nbData = map(lambda x: utils.midiNoteMapping[x], nbData)
                        pred = model.makeNBPred(nbData, gObj.nbModel[0], gObj.nbModel[1])
                        gObj.predictionState = map(lambda x: False, gObj.predictionState)
                        gObj.predictionState[utils.reverseMidiNoteMapping[pred]] = True
                        print "prediction: ", pred
                    print note
                    gObj.noteRects.append(utils.makeNoteRect(noteNum, 1))
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))
            elif event.type == KEYUP:
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    gObj.soundMapping[noteNum].stop()
                    gObj.currNoteState[noteNum] = 0
                    print noteNum, " : ", gObj.currNoteState[noteNum]
                    lastNote = next(x for x in reversed(gObj.allNotes) if x[0] == noteNum)
                    lastNote[2] = pygame.time.get_ticks()
                    print lastNote
        pygame.display.update()
        fpsClock.tick(60)
