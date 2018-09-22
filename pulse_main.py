import ROOT
import numpy as np
import root_numpy as rnm

import pulse_calculations as p_calc
import run_log_metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis():

    dm.setFunctionAnalysis("pulse_analysis")
    dm.defineDataFolderPath()
    startTime = dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart PULSE analysis, batches:", md.batchNumbers
    
    for runLog in runLog_batch:
    
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers
    
        startTimeBatch = dm.getTime()
    
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
      
        for index in range(0, len(runLog)):
        
            md.defineGlobalVariableRun(runLog[index])
            
            if not dm.checkIfFileAvailable():
                continue
                
            print "Run", md.getRunNumber()
            
            pulseAnalysisPerRun()
            
                        
            print "Done with run", md.getRunNumber(), "\n"

        print "Done with batch", runLog[0][5], "Time analysing: "+str(dm.getTime()-startTimeBatch)+"\n"

    print "Done with PULSE analysis. Time analysing: "+str(dm.getTime()-startTime)+"\n"


# Analyze pulse analysis for each run
def pulseAnalysisPerRun():
    
    # Configure inputs for multiprocessing
    max = md.getNumberOfEvents()
    step = 10000
    threads = 4

    p = Pool(threads)
    ranges = range(0, max, step)
    
    dataPath = dm.getDataPath()
    
    noise, pedestal = dm.importNoiseProperties()
    
    # Form of results
    results = p.map(lambda part: multiProcess(dataPath, noise, pedestal, part, part + step), ranges)
    
    # results change form, now each element is a variable
    results_variables = p_calc.concatenateResults(results)
    
    # Watch out, only exporting two arrays
    dm.exportPulseData(results_variables)


# Multiprocessing
def multiProcess(dataPath, noise, pedestal, begin, end):

    data = rnm.root2array(dataPath, start=begin, stop=end)
    results = p_calc.pulseAnalysis(data, noise, pedestal)
    del data
    return results




