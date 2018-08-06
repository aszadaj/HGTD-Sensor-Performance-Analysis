import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import run_log_metadata as md
import data_management as dm
import timing_plot as t_plot
import timing_calculations as t_calc


ROOT.gROOT.SetBatch(True)

# Start analysis of selected run numbers
def timingAnalysis():

    dm.defineDataFolderPath()
    
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    print "\nStart TIMING analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:
 
        # Restrict run numbers
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers]

        
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
      
        for index in range(0, len(runLog)):
            
            md.defineGlobalVariableRun(runLog[index])
                
            print "Run", md.getRunNumber()
            
            # Import files per run
            peak_time = dm.importPulseFile("peak_time")
            cfd05 = dm.importPulseFile("cfd05")
            
            # Perform calculations linear
            time_diff_peak = t_calc.getTimeDifferencePerRun(peak_time)
            time_diff_cfd05 = t_calc.getTimeDifferencePerRun(cfd05)
            
            # Export per run number linear
            dm.exportTimeDifferenceData(time_diff_peak, time_diff_cfd05 )
        
            if md.getBatchNumber()/100 != 6:
                # Perform calculations sys eq
                time_diff_peak_sys_eq = t_calc.getTimeDifferencePerRunSysEq(peak_time)
                time_diff_cfd05_sys_eq = t_calc.getTimeDifferencePerRunSysEq(cfd05)

                # Export per run number sys eq
                dm.exportTimeDifferenceDataSysEq(time_diff_peak_sys_eq, time_diff_cfd05_sys_eq)
            
            print "Done with run", md.getRunNumber(), "\n"

        print "Done with batch", runLog[0][5], "\n"

    print "Done with TIMING analysis\n"


