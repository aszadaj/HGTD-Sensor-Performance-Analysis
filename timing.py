import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import data_management as dm

#md.setupATLAS()
ROOT.gROOT.SetBatch(True)


def timingAnalysis(numberOfRunsPerBatch, numberOfBatches):
    
    startTime = getTime()
    printTime()
    print "Start timing analysis, " +str(numberOfBatches)+" batch(es), " + str(numberOfRunsPerBatch) + " run(s) per batch.\n"

    dm.checkIfRepositoryOnStau()
    runLog = md.getRunLogForTimingAnalysis(numberOfBatches, numberOfRunsPerBatch)
 
    currentBatch = int(runLog[0][5])
    last_row = runLog[-1][3]

    data_batch = [np.empty(0), currentBatch]
    
    for row_number in range(0,len(runLog)): data_batch = timingAnalysisPerBatch(row_number, runLog, data_batch)
    print "\nDone analysing, time analysing: " + str(getTime()-startTime) + "\n"
    
    exit()


def timingAnalysisPerBatch(row_number, runLog, data_batch):

    row = runLog[row_number]

    md.defineGlobalVariableRun(row)
    [peak_times_batch, currentBatch] = [i for i in data_batch]
    peak_times_run = dm.importPulseFile("peak_times")
    
    if peak_times_batch.size == 0:
    
        print "Start analysing batch " + str(currentBatch) + "...\n"
        
        peak_times_batch = np.empty(0, dtype = peak_times_run.dtype)


    if row[5] != runLog[row_number-1][5] and row_number > 0:
    
        print "All runs in batch " + str(currentBatch) + " considered, start analysis...\n"
        md.defineGlobalVariableRun(runLog[row_number-1])
        comparePeakTimes(peak_times_batch)
        
        md.defineGlobalVariableRun(runLog[row_number])
        currentBatch = int(row[5])
        
        printTime()
        print "Start analysing batch " + str(currentBatch) + "...\n"
        peak_times_batch = np.empty(0, dtype = peak_times_run.dtype)


    # Last row
    if row[3] == runLog[-1][3]:
    
        printTime()
        print "All runs in batch " + str(currentBatch) + " considered, producing plots...\n"
        
        peak_times_batch = np.append(peak_times_batch, peak_times_run)
        comparePeakTimes(peak_times_batch)
    
    else:
        
        peak_times_batch = np.append(peak_times_batch, peak_times_run)
    

    return [peak_times_batch, currentBatch]


def comparePeakTimes(peak_times):

    SiPM_name = "SiPM-AFP"
    SiPM_chan = md.getChannelNameForSensor(SiPM_name)
    data_graph = dict()
    
    chans = peak_times.dtype.names
    
    channels = []
    
    SiPM_index = int(SiPM_chan[-1])
    
    for chan in chans:
        if chan != chans[int(SiPM_chan[-1])]:
            channels.append(chan)

    canvas = ROOT.TCanvas("Timing","timing")
    
    low_time_difference = np.empty(len(peak_times), dtype=peak_times.dtype)
    
    for chan in channels:
    
        data_graph[chan] = ROOT.TH1D("timing_"+chan+"_histogram","Time difference distribution between SiPM and " + md.getNameOfSensor(chan) + " "+str(int(chan[-1:])+1),200,35,60)
        for entry in range(0, len(peak_times)):
            timeDifference = abs(peak_times[entry][chan]-peak_times[entry][SiPM_index])*0.1
            data_graph[chan].Fill(timeDifference)
            if timeDifference < 30:
                low_time_difference[entry][chan] = 1.0
        
    
        produceTH1Plot(data_graph[chan], chan, canvas)

    print "low value points"

    for chan in channels:
        print chan
        print np.count_nonzero(low_time_difference[chan]) + "\n"


def produceTH1Plot(graph, chan, canvas):

    headTitle = "Time difference between SiPM and " + md.getNameOfSensor(chan)
    fileName = ".pdf"

    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+";" + "Time (ns)" + "; " + "Entries (N)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw()
    canvas.Update()
    canvas.Print("plots/timing/timing_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

