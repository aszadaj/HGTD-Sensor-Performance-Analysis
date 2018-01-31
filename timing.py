import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import data_management as dm
import timing_plot as t_plot
import timing_calculations as t_calc


ROOT.gROOT.SetBatch(True)

# Start analysis of selected run numbers
def timingAnalysis(batchNumbers):

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(batchNumbers)
    print "\nStart TIMING analysis, batches:", batchNumbers

    for runLog in runLog_batch:
 
        # Create batches to use them to plot results
        time_difference_batch = np.empty(0)
        peak_value_batch = np.empty(0)
        peak_time_batch = np.empty(0)
        
        # Restrict run numbers
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers]
    
        startTimeBatch = md.getTime()
        md.printTime()
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            md.defineGlobalVariableRun(runLog[index])
            
            if (md.isTimingDataFilesAvailable()):
                
                print "Run", md.getRunNumber()
                
                # Import files per run
                peak_time_run = dm.importPulseFile("peak_time")
                peak_value_run = dm.importPulseFile("peak_value")
                
                time_difference_run = t_calc.timingAnalysisPerRun(peak_time_run)
                
                if len(time_difference_batch) == 0:
                
                    time_difference_batch = time_difference_batch.astype(time_difference_run.dtype)
                    peak_value_batch = peak_value_batch.astype(peak_value_run.dtype)
                    peak_time_batch = peak_time_batch.astype(peak_time_run.dtype)
         
                # Export per run number
                dm.exportTimingData(time_difference_run)
                
                # Concatenate to plot all results
                time_difference_batch = np.concatenate((time_difference_batch, time_difference_run))
                peak_value_batch = np.concatenate((peak_value_batch, peak_value_run))
                peak_time_batch = np.concatenate((peak_time_batch, peak_time_run))
               
                print "Done with run", md.getRunNumber(), "\n"


        if len(time_difference_batch) != 0:
        
            # Done with the for loop and appending results, produce plots
            print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"

            t_plot.produceTimingDistributionPlots(time_difference_batch, peak_value_batch, peak_time_batch)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],"\n"


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

