
import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import tracking_plot as tplot
import data_management as dm

#md.setupATLAS()

ROOT.gROOT.SetBatch(True)

def trackingAnalysis(batchNumbers):

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(batchNumbers)
    print "\nStart TRACKING analysis, batches:", batchNumbers

    for runLog in runLog_batch:
    
        results_batch = []
        
        # DEBUG # Comment out this line to consider all files in batch
        
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers
    
        startTimeBatch = md.getTime()
        
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isTrackingFileAvailable()):
                
                print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
                
                print "Run", md.getRunNumber()
                peak_values_run = dm.importPulseFile("peak_value")
                tracking_data_run = dm.importTrackingFile()
             
               
                # Slice the peak values to match the tracking files
                if len(peak_values_run) > len(tracking_data_run):
                
                
                    peak_values_run = np.take(peak_values_run, np.arange(0,len(tracking_data_run)))
                
                # Or the other way around if the other file is shorter (for quick analysis)
                else:
                
                    tracking_data_run = np.take(tracking_data_run, np.arange(0,len(peak_values_run)))
                
                
                
                results_batch.append([peak_values_run, tracking_data_run])
                print "Done with run", md.getRunNumber(), "\n"
        
        
        # Done with the for loop and appending results, produce plots
       
        if len(results_batch) != 0:
            print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
            peak_values     = np.empty(0, dtype=results_batch[0][0].dtype)
            tracking_data  = np.empty(0, dtype=results_batch[0][1].dtype)
        
            for results_run in results_batch:
                peak_values     = np.concatenate((peak_values, results_run[0]), axis = 0)
                tracking_data  = np.concatenate((tracking_data,  results_run[1]), axis = 0)
         
            tplot.produceTrackingGraphs(tracking_data, peak_values)
    
            print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],".\n"



# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

