import ROOT
import numpy as np
import root_numpy as rnm
import pathos

import pulse_calculations as p_calc
import run_log_metadata as md
import data_management as dm

# Number of threads for multiprocesing
threads = 4

# number of events per iteration and thread
step = 10000

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis():

    dm.setFunctionAnalysis("pulse_analysis")
    defineNameOfProperties()
    startTime = dm.getTime()
    
    print "\nStart PULSE analysis, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
        
        runNumbers = md.getAllRunNumbers(batchNumber)
        
        # Restrict to some run numbers
        if md.limitRunNumbers != "all":
            runNumbers = runNumbers[0:md.limitRunNumbers]
        
        startTimeBatch = dm.getTime()
    
        print "Batch:", batchNumber, len(runNumbers), "run files.\n"
      
        for runNumber in runNumbers:
            
            md.defineRunInfo(md.getRowForRunNumber(runNumber))
            
            if not dm.checkIfFileAvailable():
                continue
            
            pulseAnalysisPerRun()
            
        print "Done with batch", batchNumber, "Time analysing: "+str(dm.getTime()-startTimeBatch)+"\n"
    
    print "Done with PULSE analysis. Time analysing: "+str(dm.getTime()-startTime)+"\n"


# Subdivide the file (has 4GB) to analyze by parts. Start pool.
def pulseAnalysisPerRun():
    
    print "Run", md.getRunNumber()
    
    # Define pool attributes, threads and number of events in each thread
    ranges = range(0, md.getNumberOfEvents(), step)
    
    # Start Pool
    Pool = pathos.multiprocessing.ProcessPool(threads)
    results = Pool.map(lambda part: signalAnalysis(part, part + step), ranges)
    
    # Concatenate results for each variable
    results_variables = p_calc.concatenateResults(results)
    
    # Clear and restart the pool
    Pool.clear()
    Pool.terminate()
    Pool.restart()
    
    # Export data
    for index in range(0, len(var_names)):
        dm.exportImportROOTData("pulse", var_names[index], results_variables[index])

    print "Done with run", md.getRunNumber(), "\n"


# Data input is in negative voltage values, but the methods handles them in "positive values"
# The output is the listed characteristics below
def signalAnalysis(start, stop):
    
    data = rnm.root2array(dm.getOscilloscopeFilePath(), start=start, stop=stop)

    properties = [np.zeros(len(data), dtype = data.dtype) for _ in range(len(var_names))]

    # Maximum signal output
    signal_limit = getSignalLimit(data)

    for chan in data.dtype.names:
        
        for event in range(0, len(data)):
        
            results = p_calc.getPulseCharacteristics(data[chan][event], signal_limit[chan], getThresholdSamples(chan))

            for type in range(0, len(results)):
                
                properties[type][event][chan] = results[type]


    return properties


def defineNameOfProperties():

    global var_names
    
    var_names = ["noise", "pedestal", "pulse_amplitude", "rise_time", "charge", "cfd", "peak_time", "points", "max_sample"]


# Get maximum values for given channel and oscilloscope
def getSignalLimit(data):
    
    signal_limit = np.empty(1, dtype=dm.getDTYPE())
    
    for chan in data.dtype.names:
        signal_limit[chan] = np.amin(np.concatenate(data[chan]))
    
    return signal_limit


# These are set values for each sensor. These values are determined between a plot for:
# Plot between maximum sample value and point above the threshold. In this way
# one can cut away pulses which are treated as noise
def getThresholdSamples(chan):
    
    sensor = md.getSensor(chan)
    
    if sensor == "50D-GBGR2" or sensor == "W9-LGA35":
        number_samples = 5
    
    elif sensor == "SiPM-AFP" or sensor == "W4-RD01":
        number_samples = 50
    
    elif sensor == "W4-LG12" or sensor == "W4-S203" or sensor == "W4-S215" or sensor == "W4-S1061":
        number_samples = 10
    
    elif sensor == "W4-S204_6e14":
        number_samples = 3
    
    elif sensor == "W4-S1022":
        number_samples = 7
    
    
    return number_samples
