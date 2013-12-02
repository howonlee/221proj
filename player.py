import pygame, sys, utils, model, operator, psutil, os, pickle, datetime
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
        self.octave = 1 #assumes that note 48 is in the data...
        for note, val in enumerate(self.currNoteState):
            self.keyRects.append(utils.makeNoteRect(note, utils.numNotes))
        self.allNotes = []
        self.modelRects = [] #(note, (left, top, width, height))
        self.noteRects = [] #(note, (left, top, width, height))
        self.soundMapping = utils.initSoundMappings()
        self.confMatList = []
        self.confMatrix = np.zeros((12, 12), dtype=np.int)
        self.avgF1s = []
        self.memoryList = []
        self.cpuList = []
        #MODELS#
        mmModel, mmModel3, hmmModel, qModel, mmKatzModel, mmKneserNeyModel = model.train(model.clusterData)
        self.mmModel = mmModel
        self.mmModel3 = mmModel3
        self.hmmModel = hmmModel
        self.qModel = qModel
        self.mmKatzModel = mmKatzModel
        self.mmKneserNeyModel = mmKneserNeyModel

    def predictNotes(self):
        if self.predictor == "MM":
            self.predict(self.mmModel, model.makeMMPred)
        elif self.predictor == "MM3":
            self.predict(self.mmModel3, model.makeMM3Pred)
        elif self.predictor == "HMM":
            self.predict(self.hmmModel, model.makeHMMPred)
        elif self.predictor == "Q":
            self.predict(self.qModel, model.makeQLearningPred)
        elif self.predictor == "KATZ":
            self.predict(self.mmKatzModel, model.makeMMKatzPred)
        elif self.predictor == "KN":
            self.predict(self.mmKneserNeyModel, model.makeMMKneserNeyPred)

    def predict(self, model, fn):
        #curry into this function
        data = map(operator.itemgetter(0), self.allNotes[-10:])
        data = map(lambda x: utils.midiNoteMapping[x], data)
        pred = fn(data, model)
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
            if model.maxNote > (self.octave + 2) * 12 + model.minNote:
                if 1 not in self.currNoteState:
                    self.octave += 1
                    print "compare maxnote to : ", ((self.octave) * 12) + model.minNote
                    print "maxnote is: ", model.maxNote
        if top[1] == utils.OCTAVE_DOWN:
            if model.minNote < self.octave * 12:
                if 1 not in self.currNoteState:
                    self.octave -= 1

    def turnNoteOn(self, noteNum):
        assert(self.currNoteState[noteNum] == 0)
        self.soundMapping[noteNum].play(loops=-1)
        self.currNoteState[noteNum] = 1
        print noteNum, " : ", self.currNoteState[noteNum]
        print "current note: ", utils.midiNoteMapping[noteNum]
        if True in self.predictionState:
            predicted = self.predictionState.index(True)
            self.confMatrix[noteNum % 12, predicted % 12] += 1
            if self.predictor == "Q":
                print "begin reward sequence"
                reward = 0
                if (noteNum % 12) == (predicted % 12):
                    print "good reward!"
                    reward = 1
                prevNote = self.allNotes[-1][0]
                print "before learning: ", self.qModel.q
                self.qModel.learn(prevNote, predicted, reward, noteNum)
                print "after learning: ", self.qModel.q
            #learn q learning here
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

    def drawRectSet(self, rects):
        for rect in rects:
            color = utils.getNoteColor(rect[0], False)
            if self.showPredictions:
                color = utils.getNoteColor(rect[0], self.predictionState[rect[0]])
            pygame.draw.rect(windowSurfaceObj, color, rect[1])

    def saveComputerData(self):
        pid = os.getpid()
        proc = psutil.Process(pid)
        self.memoryList.append(proc.get_memory_info().vms)
        self.cpuList.append(proc.get_cpu_percent(interval=0)) #this returns immediately

    def saveData(self):
        self.saveComputerData()

        self.confMatList.append(self.confMatrix.copy())
        lastConfMat = self.confMatList[-1]
        correctList = [np.diagonal(lastConfMat)[i] for i in xrange(lastConfMat.shape[0])]
        rowSums = list(np.sum(lastConfMat, axis=1)) #sums of each row
        colSums = list(np.sum(lastConfMat, axis=0)) #sums of each column
        precisions = []
        recalls = []
        f1s = []
        for i in xrange(len(correctList)):
            if rowSums[i] != 0:
                precisions.append(float(correctList[i]) / float(rowSums[i]))
            else:
                precisions.append(-1)
            if colSums[i] != 0:
                recalls.append(float(correctList[i]) / float(colSums[i]))
            else:
                recalls.append(-1)
        for i in xrange(len(correctList)):
            if precisions[i] != -1 and recalls[i] != -1 and ((precisions[i] + recalls[i]) != 0):
                f1s.append(2*((precisions[i] * recalls[i]) / (precisions[i] + recalls[i])))
        if not f1s:
            return
        avg = sum(f1s) / len(f1s)
        self.avgF1s.append(avg)

    def saveNoteData(self, datestr):
        data = {}
        data["train"] = []
        quadAllNotes = [map(lambda x: x[0], self.allNotes[x:x+4]) for x in xrange(0, len(self.allNotes), 4)]
        data["train"].append(quadAllNotes)
        with open("./usr/noteData_%s.pickle" % datestr, 'w') as f:
            pickle.dump(data, f)

    def makeGraphs(self):
        #save final confusion matrix in textfile
        datestr = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        #delimiter's whacky and stuff to be better at latexing
        np.savetxt("./usr/confMat_%s.txt" % datestr, self.confMatrix, "%d", delimiter=" & ", newline=' \\\\\n')
        self.saveNoteData(datestr)
        self.saveAcc(datestr)
        self.saveF1(datestr)
        self.saveMemory(datestr)
        self.saveCPU(datestr)

    def saveAcc(self, datestr):
        correctList = map(lambda x: x.trace(), self.confMatList)
        totalList = map(lambda x: x.sum(), self.confMatList)
        accList = []
        for i in xrange(len(totalList)):
            if totalList[i] > 0.5:
                accList.append(float(correctList[i]) / float(totalList[i]))
        print "acclist: ", accList
        plt.figure(0)
        plt.plot(accList)
        plt.ylabel("Accuracy Over Time")
        plt.savefig("./usr/acc_%s.png" % datestr, bbox_inches=0) #save this properly instead

    def saveF1(self, datestr):
        plt.figure(1)
        plt.plot(self.avgF1s)
        print "f1s: ", self.avgF1s
        plt.ylabel("Average F1 Score Over All Classes")
        plt.savefig("./usr/f1_%s.png" % datestr, bbox_inches=0) #save this properly instead

    def saveMemory(self, datestr):
        plt.figure(2)
        plt.plot(self.memoryList)
        print "memory: ", self.memoryList
        plt.ylabel("Virtual Memory Used")
        plt.savefig("./usr/mem_%s.png" % datestr, bbox_inches=0) #save this properly instead

    def saveCPU(self, datestr):
        plt.figure(3)
        plt.plot(self.cpuList)
        print "cpu: ", self.cpuList
        plt.ylabel("Percent Available CPU used")
        plt.savefig("./usr/cpu_%s.png" % datestr, bbox_inches=0) #save this properly instead

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
    pygame.time.set_timer(USEREVENT+1, 2000) #for saving data
    pygame.time.set_timer(USEREVENT+2, 1) #for playing notes
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
                    g.predictor = "KATZ"
                if event.key == K_6:
                    g.predictor = "KN"
                if event.key == K_g:
                    g.addActionQueue(-1, utils.OCTAVE_DOWN)
                if event.key == K_h:
                    g.addActionQueue(-1, utils.OCTAVE_UP)
                if event.key == K_0:
                    g.showPredictions = not g.showPredictions
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key] + (12 * g.octave)
                    g.addActionQueue(noteNum, utils.NOTE_ON)
            elif event.type == KEYUP:
                if event.key in utils.currNoteMapping:
                    noteNum = utils.currNoteMapping[event.key] + (12 * g.octave)
                    g.addActionQueue(noteNum, utils.NOTE_OFF)
            elif event.type == USEREVENT + 1:
                g.saveData()
            elif event.type == USEREVENT + 2:
                g.popActionQueue()
        pygame.display.update()
        fpsClock.tick(60)
