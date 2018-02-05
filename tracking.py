
import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import tracking_plot as tplot
import data_management as dm

#md.setupATLAS()

ROOT.gROOT.SetBatch(True)

def trackingAnalysis():

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart TRACKING analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:
    
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers

        startTimeBatch = md.getTime()
    
        results_batch = []

        for index in range(0, len(runLog)):
           
            md.defineGlobalVariableRun(runLog[index])
            
            if (md.isTrackingFileAvailable()):
                
                print "Run", md.getRunNumber()
                peak_values_run = dm.importPulseFile("peak_value")
                tracking_run = dm.importTrackingFile()
             
                # Slice the peak values to match the tracking files
                if len(peak_values_run) > len(tracking_run):
                
                    peak_values_run = np.take(peak_values_run, np.arange(0,len(tracking_run)))
                
                # Or the other way around if the other file is shorter (for quick analysis)
                else:
                
                    tracking_run = np.take(tracking_run, np.arange(0,len(peak_values_run)))
            

                results_batch.append([peak_values_run, tracking_run])
                
                print "Done with run", md.getRunNumber(), "\n"
        
        
        if len(results_batch) != 0:
            print "Producing plots for batch " + str(md.getBatchNumber()) + ".\n"

            peak_values = np.empty(0, dtype=results_batch[0][0].dtype)
            tracking    = np.empty(0, dtype=results_batch[0][1].dtype)

            for results_run in results_batch:
                peak_values = np.concatenate((peak_values, results_run[0]), axis = 0)
                tracking    = np.concatenate((tracking,  results_run[1]), axis = 0)

            tplot.produceTrackingGraphs(peak_values, tracking)

            print "Done with batch",runLog[0][5],"Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"
            

    print "Done with TRACKING analysis. Time analysing: "+str(md.getTime()-startTime)+"\n"

# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

