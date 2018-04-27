import ROOT
import root_numpy as rnm
import numpy as np

import pulse_calculations as p_calc
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis():

    dm.defineDataFolderPath()
    startTime = dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart PULSE analysis, batches:", md.batchNumbers
    
    for runLog in runLog_batch:
    
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers
    
        startTimeBatch = dm.getTime()
        dm.getTime()
    
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
      
        for index in range(0, len(runLog)):
        
            md.defineGlobalVariableRun(runLog[index])
            
            print "Run", md.getRunNumber()
            
            variable_array = pulseAnalysisPerRun()
            dm.exportPulseData(variable_array)
                        
            print "Done with run", md.getRunNumber(), "\n"

        print "Done with batch", runLog[0][5], "Time analysing: "+str(dm.getTime()-startTimeBatch)+"\n"

    print "Done with PULSE analysis. Time analysing: "+str(dm.getTime()-startTime)+"\n"


# Analyze pulse analysis for each run
def pulseAnalysisPerRun():
    
    # Configure inputs for multiprocessing
    max = md.getNumberOfEvents()
    step = 10000
    threads = 4

    # Quick Analysis
    if md.maxEntries != 0:
        max = step = md.maxEntries
        threads = 1
    
    p = Pool(4)
    ranges = range(0, max, step)
    
    dataPath = dm.getDataPath()
    pedestal = dm.importNoiseFile("pedestal")
    noise    = dm.importNoiseFile("noise")
    
    # Form of results
    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step), ranges)
    
    # Used for debugging
    #results = multiProcess(dataPath, pedestal, noise, 0, step)
    
    # results change form, now each element is a variable
    results_variables = p_calc.concatenateResults(results)

    return results_variables


# Multiprocessing
def multiProcess(dataPath, pedestal, noise, begin, end):

    data = rnm.root2array(dataPath, start=begin, stop=end)
    
    return p_calc.pulseAnalysis(data, pedestal, noise)




