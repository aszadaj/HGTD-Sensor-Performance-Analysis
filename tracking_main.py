import ROOT
import numpy as np
import root_numpy as rnm

import run_log_metadata as md
import tracking_plot as tplot
import data_management as dm

ROOT.gROOT.SetBatch(True)

# Function appends tracking files and oscilloscope files and
# matches the sizes of them
def trackingAnalysis():

    dm.setFunctionAnalysis("tracking_analysis")
    dm.defineDataFolderPath()
    startTime = dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart TRACKING analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:
    
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers

        startTimeBatch = dm.getTime()
        
        # Set a condition of at least two run numbers to be analyzed
        if len(runLog) < 2:
            continue

        results_batch = []

        for index in range(0, len(runLog)):
            
            md.defineGlobalVariableRun(runLog[index])

            if not dm.checkIfFileAvailable():
                continue
            
            # note, here take the max sample instead, since peak_values can be limited, can affect the efficiency plots!
            #peak_values_run = dm.exportImportROOTData("pulse", "max_sample", False)
            peak_values_run = dm.exportImportROOTData("pulse", "peak_value", False)
            charge_run = dm.exportImportROOTData("pulse", "charge", False)
            rise_times_run = dm.exportImportROOTData("pulse", "rise_time", False)
            time_difference_peak_run = dm.exportImportROOTData("timing", "linear", False)
            time_difference_cfd_run = dm.exportImportROOTData("timing", "linear_cfd", False)

            tracking_run = dm.exportImportROOTData("tracking", "", False)
 
            # Slice the peak values to match the tracking files
            if len(peak_values_run) > len(tracking_run):
            
                peak_values_run                    = np.take(peak_values_run, np.arange(0, len(tracking_run)))
                charge_run                         = np.take(charge_run, np.arange(0, len(tracking_run)))
                rise_times_run                     = np.take(rise_times_run, np.arange(0, len(tracking_run)))
                time_difference_peak_run           = np.take(time_difference_peak_run, np.arange(0, len(tracking_run)))
                time_difference_cfd_run          = np.take(time_difference_cfd_run, np.arange(0, len(tracking_run)))

            else:
            
                tracking_run                       = np.take(tracking_run, np.arange(0, len(peak_values_run)))

            results_batch.append([peak_values_run, charge_run, rise_times_run, tracking_run, time_difference_peak_run, time_difference_cfd_run])


        
        if len(results_batch) != 0:
            print "\nProducing plots for batch " + str(md.getBatchNumber()) + ".\n"

            peak_values                     = np.empty(0, dtype=results_batch[0][0].dtype)
            charge                          = np.empty(0, dtype=results_batch[0][1].dtype)
            rise_times                      = np.empty(0, dtype=results_batch[0][2].dtype)
            tracking                        = np.empty(0, dtype=results_batch[0][3].dtype)
            time_difference_peak            = np.empty(0, dtype=results_batch[0][4].dtype)
            time_difference_cfd           = np.empty(0, dtype=results_batch[0][5].dtype)

            for results_run in results_batch:
                peak_values                      = np.concatenate((peak_values, results_run[0]), axis = 0)
                charge                           = np.concatenate((charge, results_run[1]), axis = 0)
                rise_times                       = np.concatenate((rise_times,  results_run[2]), axis = 0)
                tracking                         = np.concatenate((tracking,  results_run[3]), axis = 0)
                time_difference_peak             = np.concatenate((time_difference_peak,  results_run[4]), axis = 0)
                time_difference_cfd            = np.concatenate((time_difference_cfd,  results_run[5]), axis = 0)
        
            # This function calculates the center position and exports the file as position_XXX.root.
            # One time only.
            #t_calc.calculateCenterOfSensorPerBatch(peak_values, tracking)
            
            tplot.produceTrackingGraphs(peak_values, charge, rise_times, time_difference_peak, time_difference_cfd, tracking)
            
            print "\nDone with batch",runLog[0][5],"Time analysing: "+str(md.dm.getTime()-startTimeBatch)+"\n"


    print "\nDone with TRACKING analysis. Time analysing: "+str(md.dm.getTime()-startTime)+"\n"

