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
    pulse_half_max_time_batch = dm.importPulseFile("half_max_times")
    comparePeakTimes(pulse_half_max_time_batch)


def comparePeakTimes(half_max_times):

    SiPM_name = "SiPM-AFP"
    SiPM_chan = md.getChannelNameForSensor(SiPM_name)
    SiPM_index = int(SiPM_chan[-1])
    data_graph = dict()
    
    print "Channel of SiPM",SiPM_chan
    
    all_channels = half_max_times.dtype.names
    
    channels = []
    
    for chan in all_channels:
        if chan != all_channels[SiPM_index]:
            channels.append(chan)

    canvas = ROOT.TCanvas("Timing","timing")
    
    filled_entries = np.zeros(len(half_max_times), dtype=half_max_times.dtype)
    
    for chan in channels:
    
        data_graph[chan] = ROOT.TH1D("timing_"+chan+"_histogram","Time difference distribution between SiPM and " + md.getNameOfSensor(chan) + " "+str(int(chan[-1:])+1),3000,-30,30)
        # outside the range, if there are filled values
        for entry in range(0, len(half_max_times)):
            timeDifference = half_max_times[entry][chan]-half_max_times[entry][SiPM_index]

            if half_max_times[entry][chan] > 0.0 and half_max_times[entry][SiPM_index] > 0.0:
                
                data_graph[chan].Fill(timeDifference*1000)


        for entry in range(0, len(half_max_times)):
            timeDifference = half_max_times[entry][chan]-half_max_times[entry][SiPM_index]

            if half_max_times[entry][chan] > 0.0 and half_max_times[entry][SiPM_index]:
                if abs(timeDifference) < data_graph[chan].GetMean():
                    filled_entries[entry][chan] = 1.0
                    
                    
        produceTH1Plot(data_graph[chan], chan, canvas)

    count = 0
    
    print len(filled_entries)

    for entry in range(0, len(filled_entries)):
        for chan in channels:
        
            if filled_entries[chan][entry] == 1.0:
            
                if count == 30:
                    break

                count += 1
                print chan, entry



def produceTH1Plot(graph, chan, canvas):

    headTitle = "Time difference between SiPM and " + md.getNameOfSensor(chan)
    fileName = ".pdf"

    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+";" + "Time (ps)" + "; " + "Entries (N)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw()
    canvas.Update()
    canvas.Print("../../HGTD_material/plots_hgtd_efficiency_sep_2017/timing/timing_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

