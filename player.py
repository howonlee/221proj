import pygame, sys, utils, model, operator, psutil, os, pickle
from pygame.locals import *
import pygame.mixer # depends on mixer, you should have SDL_mixer
import numpy as np
import matplotlib.pyplot as plt

class Game:
    def __init__(self, showPredictions=True, predictor="MM", hidden=False):
        self.showPredictions = showPredictions
        self.currNoteState = [0] * utils.numNotes
        self.predictionState = [False] * utils.numNotes
        self.keyRects = []
        self.actionQueue = []
        if predictor not in ["MM", "MM3", "HMM", "Q"]:
            predictor = "MM"
        self.predictor = predictor
        for note, val in enumerate(self.currNoteState):
            self.keyRects.append(utils.makeNoteRect(note, utils.numNotes))
        self.allNotes = []
        self.modelRects = [] #(note, (left, top, width, height))
        self.noteRects = [] #(note, (left, top, width, height))
        self.soundMapping = utils.initSoundMappings()
        self.confMatList = []
        self.confMatrix = np.zeros((utils.numNotes, utils.numNotes), dtype=np.int)
        self.avgF1s = []
        self.memoryList = []
        self.cpuList = []
        #MODELS#
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
        if self.predictor == "Q":
            self.qModel.learn(state1, action1, reward, state2)
        pred = fn(data, model[0], model[1])
        self.predictionState = map(lambda x: False, self.predictionState)
        midiNote = utils.reverseMidiNoteMapping[pred]
        print "midiNote: ", midiNote
        self.predictionState[midiNote] = True

    def addActionQueue(self, note, action):
        self.actionQueue.append((note, action))

    def popActionQueue(self):
        if not self.actionQueue: return
        top = self.actionQueue.pop()
        assert len(top) == 2
        if top[1] == utils.NOTE_ON:
            self.turnNoteOn(top[0])
        if top[1] == utils.NOTE_OFF:
            self.turnNoteOff(top[0])
        if top[1] == utils.OCTAVE_UP:
            self.octaveUp()
        if top[1] == utils.OCTAVE_DOWN:
            self.octaveDown()

    def turnNoteOn(self, noteNum):
        assert(self.currNoteState[noteNum] == 0)
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
        assert(self.currNoteState[noteNum] == 1)
        self.soundMapping[noteNum].stop()
        self.currNoteState[noteNum] = 0
        print noteNum, " : ", self.currNoteState[noteNum]
        lastNote = next(x for x in reversed(self.allNotes) if x[0] == noteNum)
        lastNote[2] = pygame.time.get_ticks()
        print lastNote

    def octaveUp(self):
        pass

    def octaveDown(self):
        pass

    def drawRectSet(self, rects):
        for rect in rects:
            color = utils.getNoteColor(rect[0], False)
            if self.showPredictions:
                color = utils.getNoteColor(rect[0], self.predictionState[rect[0]])
            pygame.draw.rect(windowSurfaceObj, color, rect[1])

    def saveData(self):
        #need to record memory, cpu data, too
        self.confMatList.append(self.confMatrix[:,:])
        correctList = [numpy.diagonal(confMatList[-1])[i] for i in xrange(confMatList[-1].shape[0])]
        rowSums = list(numpy.sum(confMatList[-1], axis=1)) #sums of each row
        colSums = list(numpy.sum(confMatList[-1], axis=0)) #sums of each column
        precisions = [float(correctList[i]) / float(rowSums[i]) for i in xrange(len(correctList))]
        recalls = [float(correctList[i]) / float(colSums[i]) for i in xrange(len(correctList))]
        f1s = [2*((precisions[i] * recalls[i]) / (precisions[i] + recalls[i])) for i in xrange(len(correctlist))]
        avg = sum(f1s) / len(f1s)
        self.avgF1s.append(avg)
        pid = os.getpid()
        proc = psutil.Process(pid)
        self.memoryList.append(proc.get_memory_info().vms)
        self.cpuList.append(proc.get_cpu_percent(interval=0)) #this returns immediately

    def saveNoteData(self, datestr):
        data = {}
        data["train"] = []
        quadAllNotes = [map(lambda x: x[0], self.allNotes[x:x+4]) for x in xrange(0, len(self.allNotes), 4)]
        data["train"].append(quadAllNotes)
        pickle.dump(data, "./noteData%s" % datestr)

    def makeGraphs(self):
        #save final confusion matrix in textfile
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        #delimiter's whacky and stuff to be better at latexing
        np.savetxt(".confMat%s.txt" % datestr, self.confMatrix, "%d", delimiter=" & ", newline=' \\\\\n')
        self.saveNoteData(datestr)
        self.saveAcc(datestr)
        self.saveF1(datestr)
        self.saveMemory(datestr)
        self.saveCPU(datestr)

    def saveAcc(self, datestr):
        correctList = map(lambda x: x.trace(), self.confMatList)
        totalList = map(lambda x: x.sum(), self.confMatList)
        accList = [float(i) / float(j) for j in totalList for i in correctList]
        plt.plot(accList)
        plt.ylabel("Accuracy Over Time")
        plt.savefig("acc%s.png" % datestr, bbox_inches=0) #save this properly instead

    def saveF1(self, datestr):
        plt.plot(self.avgF1s)
        plt.ylabel("Average F1 Score Over All Classes")
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        plt.savefig("f1%s.png" % datestr, bbox_inches=0) #save this properly instead

    def saveMemory(self, datestr):
        plt.plot(self.memoryList)
        plt.ylabel("Virtual Memory Used")
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        plt.savefig("mem%s.png" % datestr, bbox_inches=0) #save this properly instead

    def saveCPU(self, datestr):
        plt.plot(self.cpuList)
        plt.ylabel("Percent Available CPU used")
        datestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        plt.savefig("cpu%s.png" % datestr, bbox_inches=0) #save this properly instead

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
    pygame.time.set_timer(USEREVENT+2, 5) #for playing notes
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
                    g.makeGraphs()
                    pygame.event.post(pygame.event.Event(QUIT))
                if event.key == K_1:
                    g.predictor = "MM"
                if event.key == K_2:
                    g.predictor = "MM3"
                if event.key == K_3:
                    g.predictor = "HMM"
                if event.key == K_4:
                    g.predictor = "Q"
                if event.key == K_5:
                    g.smooth = "Laplace"
                if event.key == K_6:
                    g.smooth = "Katz"
                if event.key == K_:
                    g.smooth = "KneserNey"
                if event.key == K_g:
                    g.addActionQueue(-1, utils.OCTAVE_DOWN)
                if event.key == K_h:
                    g.addActionQueue(-1, utils.OCTAVE_UP)
                if event.key == K_0:
                    g.showPredictions = not g.showPredictions
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    g.addActionQueue(noteNum, utils.NOTE_ON)
            elif event.type == KEYUP:
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key]
                    g.addActionQueue(noteNum, utils.NOTE_OFF)
            elif event.type == USEREVENT + 1:
                g.saveData()
            elif event.type == USEREVENT + 2:
                g.popActionQueue()
        pygame.display.update()
        fpsClock.tick(60)
