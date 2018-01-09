
import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import telescope_plot as tplot
import data_management as dm

#md.setupATLAS()

ROOT.gROOT.SetBatch(True)

def telescopeAnalysis(batchNumbers):

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(batchNumbers)
    print "\nStart pulse analysis, batches:", batchNumbers

    for runLog in runLog_batch:
    
        results_batch = []
        
        # DEBUG # Comment out this line to consider all files in batch
        runLog = runLog[0:2] # Restrict to some run numbers
    
        startTimeBatch = md.getTime()
        md.printTime()
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isRootFileAvailable(md.getTimeStamp())):
                
                print "Run", md.getRunNumber()
                peak_values_run = dm.importPulseFile("peak_value")
                telescope_data_run = dm.importTelescopeFile()
                
                # Slice the peak values to match the telescope files
                peak_values_run = np.take(peak_values_run, np.arange(0,len(telescope_data_run)))
                
                results_batch.append([peak_values_run, telescope_data_run])
                print "Done with run", md.getRunNumber(), "\n"
        
            else:
                print "WARNING! There is no root file for run number: " + str(runNumber) + "\n"
    
        # Done with the for loop and appending results, produce plots
        print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
        
        peak_values     = np.empty(0, dtype=results_batch[0][0].dtype)
        telescope_data  = np.empty(0, dtype=results_batch[0][1].dtype)
    
        for results_run in results_batch:
            peak_values     = np.concatenate((peak_values, results_run[0]), axis = 0)
            telescope_data  = np.concatenate((telescope_data,  results_run[1]), axis = 0)
     
     
        tplot.produceTelescopeGraphs(telescope_data, peak_values)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],".\n"



# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

