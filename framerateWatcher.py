import sys
import traceback
from datetime import datetime
import ac


class FramerateWatcher():
    # some tweakable constants
    shortAveragePeriod = 0.25     # in seconds
    longAveragePeriod = 5.0       # in seconds
    spikeThreshold = 10.0         # in percentage. minimum variation of shortAvg (relative to longAvg) to be considered a spike
    graphLength = 500             # amount of values (FPS readings) the graph will plot in OX axis

    def __init__(self, ac_version):
        def initStats():
            self.lastShortAverageTime=datetime.now()# time the short running average was last computed
            self.shortAverageFramecount = 0         # needed for computing short avg
            self.shortAverages = []                 # needed for computing long avg framerate
            self.shortAverage = 0                   # last computed short avg framerate
            self.longAverage = 0                    # last computed long avg framerate
            self.spikes = []                        # most recent major spikes. each spike is a tuple: (datetime, shortAverage, deviationPercentage)
        def initWindow(widgetWidth, widgetHeight):
            self.window = ac.newApp(self.getName())
            ac.setSize(self.window, widgetWidth,widgetHeight)
        def initErrorLabel(widgetWidth):
            self.errorLabel = ac.addLabel(self.window,"")
            ac.setPosition(self.errorLabel, widgetWidth, 0) # print errors aside from the widget
        def initInfoLabel():
            self.infoLabel = ac.addLabel(self.window,"")
            ac.setPosition(self.infoLabel, 5, 25) # skip the customary top-left icon of the widget
        def initGraph(widgetWidth, widgetHeight):
            posY = 250
            self.graph = ac.addGraph(self.window, "")
            ac.setPosition(self.graph, 0, posY)
            ac.setSize(self.graph, widgetWidth, widgetHeight-posY) # enlarge graph till the bottom end of the widget
            ac.addSerieToGraph(self.graph, 0,0,1) # instant framerate
            ac.addSerieToGraph(self.graph, 1,0,0) # short running avg
            ac.addSerieToGraph(self.graph, 0,1,0) # long running avg
            return 3 #amount of series
        def fillGraph(series):
            for serie in range(series):
                for i in range(FramerateWatcher.graphLength):
                    ac.addValueToGraph(self.graph, serie, 0.0)
        w,h = 400, 400
        initStats()
        initWindow(w, h)
        initErrorLabel(w)
        initInfoLabel()
        series = initGraph(w, h)
        fillGraph(series) # purely for cosmetic purposes

    def getName(self):
        return self.__class__.__name__

    def update(self, dt):
        try:
            now = datetime.now()
            self.shortAverageFramecount += 1
            self.instantFramerate = 1.0 / min(1.0, dt) # safeguard against division by zero
            if self.shortAvgElapsed(now) > FramerateWatcher.shortAveragePeriod:
                self.computeShortRunningAverage(now)
                self.computeLongRunningAverage()
                self.checkForSpikes(now)
                self.updateGraphScale()
            self.updateGraphValues()
            self.updateLabelValues()
        except Exception: # won't catch syntax errors; those will freak out AC, which AFAIK leaves no trace about what happened exactly...
            updateErrorLabel()

    def shortAvgElapsed(self, now):
        """ returns seconds elapsed since the short average was last computed """
        return (now - self.lastShortAverageTime).total_seconds()

    def updateErrorLabel(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        text = repr(traceback.format_exception(exc_type, exc_value, exc_traceback)).replace("\\n", "\n")
        ac.setText(self.errorLabel, text)            

    def updateLabelValues(self):
        def getBasicStatsStr():
            result = ""
            result += "%.1f FPS instant framerate\n"         %(self.instantFramerate)
            result += "%.1f FPS short running avg (%.1fs)\n" %(self.shortAverage, FramerateWatcher.shortAveragePeriod)
            result += "%.1f FPS long running avg (%.1fs)\n"  %(self.longAverage,  FramerateWatcher.longAveragePeriod)
            return result
        def getSpikesStr():
            result = "---- Recent major spikes (>%.1f%%)----\n" %(FramerateWatcher.spikeThreshold)
            for spike in reversed(self.spikes):
                result += "%.1f FPS"            % spike["framerate"]
                result += "(%.1f%% deviation)" % (spike["deviation"] * 100.)
                result += "at %s"          % (str(spike["timestamp"].time())[:-3])
                result += "\n"
            return result
        ac.setText(self.infoLabel, getBasicStatsStr() + getSpikesStr())

    def updateGraphValues(self):
        ac.addValueToGraph(self.graph, 0, self.instantFramerate)
        ac.addValueToGraph(self.graph, 1, self.shortAverage)
        ac.addValueToGraph(self.graph, 2, self.longAverage)

    def updateGraphScale(self):
        minFps = 0
        maxFps = self.longAverage * 1.50 # don't stick graph lines to the top, leave some margin
        ac.setRange(self.graph, minFps, maxFps, FramerateWatcher.graphLength)

    def computeShortRunningAverage(self, now):
        def removeOldShortAverages():
            while (self.shortAverages[-1][0] - self.shortAverages[0][0]).total_seconds() > FramerateWatcher.longAveragePeriod:
                self.shortAverages = self.shortAverages[1:]
        self.shortAverage = self.shortAverageFramecount / self.shortAvgElapsed(now)
        self.shortAverages.append((now, self.shortAverage))
        removeOldShortAverages()
        self.lastShortAverageTime = now
        self.shortAverageFramecount = 0

    def computeLongRunningAverage(self):
        framerates = [f[1] for f in self.shortAverages]
        self.longAverage = sum(framerates) / len(framerates)

    def checkForSpikes(self, now):
        deviation = (self.longAverage - self.shortAverage) / self.longAverage
        if deviation > FramerateWatcher.spikeThreshold/100.: # only negative deviations. positive framerate spikes ain't that bad
            spike = { "timestamp": now, "framerate": self.shortAverage, "deviation": deviation }
            self.spikes.append(spike)
            self.spikes = self.spikes[-7:]

			
frw = None

def acMain(ac_version):
    global frw
    frw = FramerateWatcher(ac_version)
    return frw.getName()
	
def acUpdate(deltaT):
    global frw
    frw.update(deltaT)    
