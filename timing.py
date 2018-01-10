import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import data_management as dm
import timing_plot as t_plot


ROOT.gROOT.SetBatch(True)

# Start analysis of selected run numbers
def timingAnalysis(batchNumbers):

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(batchNumbers)
    print "\nStart timing analysis, batches:", batchNumbers

    for runLog in runLog_batch:
    
        time_difference_batch = np.empty(0)
      
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers]
    
        startTimeBatch = md.getTime()
        md.printTime()
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isTimingDataFilesAvailable()):
                
                print "Run", md.getRunNumber()
                peak_time_run = dm.importPulseFile("peak_time")
                print peak_time_run
                time_difference_run = timingAnalysisPerRun(peak_time_run)
                
                if len(time_difference_batch) == 0:
                    time_difference_batch = time_difference_batch.astype(time_difference_run.dtype)
          
                # Export per run number
                
                dm.exportTimingData(time_difference_run)
                
                # Concatenate to plot all results
                time_difference_batch = np.concatenate((time_difference_batch, time_difference_run))
                print "Done with run", md.getRunNumber(), "\n"
        
            else:
                print "WARNING! There is no root file for run number: " + str(runNumber) + "\n"
    
        # Done with the for loop and appending results, produce plots
        print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
        
        if len(time_difference_batch) != 0:
            t_plot.produceTimingDistributionPlots(time_difference_batch)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],"\n"



def timingAnalysisPerRun(data):
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
   
    SiPM_index = int(SiPM_chan[-1])

    time_difference = np.zeros(len(data), dtype = data.dtype)

    for event in range (0, len(data)):
        for chan in data.dtype.names:
            if chan != SiPM_chan and data[chan][event] != 0 and data[SiPM_chan][event] != 0:
                time_difference[chan][event] = data[event][chan] - data[event][SiPM_chan]

    return time_difference


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

