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
def timingAnalysis():

    dm.checkIfRepositoryOnStau()
    
    startTime = dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    print "\nStart TIMING analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:
 
        # Restrict run numbers
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers]
    
        startTimeBatch = dm.getTime()
        dm.printTime()
        
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
      
        for index in range(0, len(runLog)):
            
            md.defineGlobalVariableRun(runLog[index])
                
            print "Run", md.getRunNumber()
            
            # Import files per run
            peak_time_run = dm.importPulseFile("peak_time")
            cfd05 = dm.importPulseFile("cfd05")
            
            # Perform calculations
            time_difference_linear_run = t_calc.timingAnalysisPerRun(peak_time_run)
            time_difference_linear_cfd05_run = t_calc.timingAnalysisPerRun(cfd05)
            
            time_difference_sys_eq_run = t_calc.timingAnalysisPerRunSysEq(peak_time_run)
            time_difference_sys_eq_cfd05_run = t_calc.timingAnalysisPerRunSysEq(cfd05)

            
            # Export per run number
            dm.exportTimingLinearData(time_difference_linear_run)
            dm.exportTimingLinearRiseTimeRefData(time_difference_linear_cfd05_run)
            
            dm.exportTimingSysEqData(time_difference_sys_eq_run)
            dm.exportTimingSysEqRiseTimeRefData(time_difference_sys_eq_cfd05_run)
            
            print "Done with run", md.getRunNumber(), "\n"


        print "Done with batch", runLog[0][5], "Time analysing: "+str(dm.getTime()-startTimeBatch)+"\n"

    print "Done with TIMING analysis. Time analysing: "+str(dm.getTime()-startTime)+"\n"


