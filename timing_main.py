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

    dm.setFunctionAnalysis("timing_analysis")
    dm.defineDataFolderPath()
    
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    print "\nStart TIMING RESOLUTION analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:
 
        # Restrict run numbers
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers]

        
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
      
        for index in range(0, len(runLog)):
        
            md.defineGlobalVariableRun(runLog[index])
            
            if not dm.checkIfFileAvailable():
                continue
            
            print "Run", md.getRunNumber()
            
            # Import files per run
            peak_time = dm.exportImportROOTData("pulse", "peak_time", False)
            cfd = dm.exportImportROOTData("pulse", "cfd", False)
            
            # Perform linear calculations
            time_diff_peak = t_calc.getTimeDifferencePerRun(peak_time)
            time_diff_cfd = t_calc.getTimeDifferencePerRun(cfd)
            
            # Export per run number linear
            dm.exportImportROOTData("timing", "linear", True, time_diff_peak)
            dm.exportImportROOTData("timing", "linear_cfd",True, time_diff_cfd)
        
            if md.getBatchNumber()/100 != 6:
                # Perform calculations sys eq
                time_diff_peak_sys_eq = t_calc.getTimeDifferencePerRunSysEq(peak_time)
                time_diff_cfd_sys_eq = t_calc.getTimeDifferencePerRunSysEq(cfd)

                # Export per run number sys eq
                dm.exportImportROOTData("timing", "sys_eq", True, time_diff_peak_sys_eq)
                dm.exportImportROOTData("timing", "sys_eq_cfd", True, time_diff_cfd_sys_eq)
            
            print "Done with run", md.getRunNumber(), "\n"

        print "Done with batch", runLog[0][5], "\n"

    print "Done with TIMING RESOLUTION analysis\n"


