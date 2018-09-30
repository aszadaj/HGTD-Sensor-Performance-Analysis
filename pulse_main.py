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

    # Set the time scope to 0.1 ns.
    md.defTimeScope()

    dm.setFunctionAnalysis("pulse_analysis")
    
    defineNameOfProperties()
    
    dm.defineDataFolderPath()
    startTime = dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart PULSE analysis, batches:", md.batchNumbers
    
    for runLog in runLog_batch:
    
         # Restrict to some run numbers
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers]
    
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


# Subdivide the file (has 4GB) to analyze by parts. Start pool.
def pulseAnalysisPerRun():
    
    # Set how many events should be run
    max = md.getNumberOfEvents()
    
    # Set steps for multiprocessing
    step = 10000
    
    # Adapt number of threads depending on the computer and number of cores of the processor
    threads = 4
    
    # Start the pool
    p = Pool(threads)
    ranges = range(0, max, step)
    
    # Get path import noise and start the pool
    dataPath = dm.getOscilloscopeFilePath()
    # Start processing pool
    
    results = p.map(lambda part: signalAnalysis(dataPath, [part, part + step]), ranges)
    
    
    # Concatenate the results (which have different form from multiprocessing)
    results_variables = p_calc.concatenateResults(results)
    
    # Clear the pool
    p.clear()
    
    # Export data
    for index in range(0, len(var_names)):
        dm.exportImportROOTData("pulse", var_names[index], results_variables[index])




# Data input is in negative voltage values, but the methods handles them in "positive manner"
# The output is the listed characteristics below
def signalAnalysis(dataPath, ranges):

    data = rnm.root2array(dataPath, start=ranges[0], stop=ranges[1])

    properties = [np.zeros(len(data), dtype = data.dtype) for _ in range(len(var_names))]

    # Maximum signal output
    signal_limit_DUT = p_calc.getSignalLimit(data)

    for chan in data.dtype.names:
        
        for event in range(0, len(data)):
        
            variables = [data[chan][event], signal_limit_DUT[chan], md.getThresholdSamples(chan)]
            
            results = p_calc.getPulseCharacteristics(variables)

            for type in range(0, len(results)):
                
                properties[type][event][chan] = results[type]

    
    return properties

def defineNameOfProperties(results=False):

    global var_names
    
    # This is for export of data and plotting those
    if not results:
        var_names = ["noise", "pedestal", "peak_value", "rise_time", "charge", "cfd", "peak_time", "points", "max_sample"]
    
    # This is export of results from plots
    else:
        var_names = ["noise", "pedestal", "peak_value", "rise_time", "charge"]



