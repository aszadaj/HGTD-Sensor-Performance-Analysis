import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import tracking_plot as tplot
import tracking_plot_pos as tpos
import data_management as dm

#md.setupATLAS()

ROOT.gROOT.SetBatch(True)

# Function appends tracking files and oscilloscope files and
# matches the sizes of them
def trackingAnalysis():

    dm.checkIfRepositoryOnStau()
    startTime = md.dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart TRACKING analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:
    
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers

        startTimeBatch = md.dm.getTime()
    
        results_batch = []
        
        print "\n Importing and concatenating...\n"

        for index in range(0, len(runLog)):
        
            md.defineGlobalVariableRun(runLog[index])
            
            if (md.isTrackingFileAvailable()):
                
                print "Run", md.getRunNumber()
                peak_values_run = dm.importPulseFile("peak_value")
                tracking_run = dm.importTrackingFile()
                time_difference_peak_run = dm.importTimingFile("linear")
                time_difference_cfd05_run = dm.importTimingFile("linear_cfd05")
    
                # Slice the peak values to match the tracking files
                if len(peak_values_run) > len(tracking_run):
                
                    peak_values_run                    = np.take(peak_values_run, np.arange(0, len(tracking_run)))
                    time_difference_peak_run           = np.take(time_difference_peak_run, np.arange(0, len(tracking_run)))
                    time_difference_cfd05_run          = np.take(time_difference_cfd05_run, np.arange(0, len(tracking_run)))

                results_batch.append([peak_values_run, tracking_run, time_difference_peak_run, time_difference_cfd05_run])
    
        
        if len(results_batch) != 0:
            print "\nProducing plots for batch " + str(md.getBatchNumber()) + ".\n"

            peak_values                     = np.empty(0, dtype=results_batch[0][0].dtype)
            tracking                        = np.empty(0, dtype=results_batch[0][1].dtype)
            time_difference_peak            = np.empty(0, dtype=results_batch[0][2].dtype)
            time_difference_cfd05           = np.empty(0, dtype=results_batch[0][3].dtype)

            for results_run in results_batch:
                peak_values                      = np.concatenate((peak_values, results_run[0]), axis = 0)
                tracking                         = np.concatenate((tracking,  results_run[1]), axis = 0)
                time_difference_peak             = np.concatenate((time_difference_peak,  results_run[2]), axis = 0)
                time_difference_cfd05            = np.concatenate((time_difference_cfd05,  results_run[3]), axis = 0)
        
            tplot.produceTrackingGraphs(peak_values, tracking, time_difference_peak, time_difference_cfd05)
            #tpos.produceTrackingGraphs(peak_values, tracking)


            print "\nDone with batch",runLog[0][5],"Time analysing: "+str(md.dm.getTime()-startTimeBatch)+"\n"


    print "\nDone with TRACKING analysis. Time analysing: "+str(md.dm.getTime()-startTime)+"\n"

