import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import data_management as dm


ROOT.gROOT.SetBatch(True)


def timingAnalysis(numberOfBatches):
    
    startTime = getTime()
    printTime()
    print "Start timing analysis batches:", numberOfBatches,"\n"

    dm.checkIfRepositoryOnStau()
    
    # Structure: each element is a run log consisting of all runs
    runLogs = md.getRunLogBatches(numberOfBatches)
    
    for runLog in runLogs:
        timingAnalysisPerBatch(runLog)
    
    print "\nDone analysing, time analysing: " + str(getTime()-startTime) + "\n"


def timingAnalysisPerBatch(runLog):

    md.defineGlobalVariableRun(runLog[0])
    peak_times_batch = dm.importPulseFile("peak_time")
    comparePeakTimes(peak_times_batch)


def comparePeakTimes(peak_times):

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    SiPM_index = int(SiPM_chan[-1])
    data_graph = dict()
    
    all_channels = peak_times.dtype.names
    
    channels = []
    
    for chan in all_channels:
    
        peak_times[chan] = np.multiply(peak_times[chan], 1000) # convert to picoseconds
        
        if chan != all_channels[SiPM_index]:
            channels.append(chan)

    canvas = ROOT.TCanvas("Timing","timing")
    
    mean_time_SiPM = np.average(np.take(peak_times[SiPM_chan], np.nonzero(peak_times[SiPM_chan]))[0])
    
    for chan in channels:
    
        mean_time_chan = np.average(np.take(peak_times[chan], np.nonzero(peak_times[chan]))[0])
        mean_time = mean_time_SiPM - mean_time_chan
       
        data_graph[chan] = ROOT.TH1D("timing_"+chan+"_histogram","Time difference distribution between SiPM and " + md.getNameOfSensor(chan) + " " + str(int(chan[-1:])+1),1000,mean_time*0.8,mean_time*1.2)
        
        for entry in range(0, len(peak_times)):
        
            if peak_times[entry][chan] != 0.0 and peak_times[entry][chan] != 0.0:

                timeDifference = peak_times[entry][SiPM_chan] - peak_times[entry][chan]
             
                data_graph[chan].Fill(timeDifference)

        produceTH1Plot(data_graph[chan], chan, canvas)


def produceTH1Plot(graph, chan, canvas):

    headTitle = "Time difference between SiPM and " + md.getNameOfSensor(chan)
    fileName = ".pdf"

    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+";" + "Time (ps)" + "; " + "Entries (N)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw()
    canvas.Update()
    canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

