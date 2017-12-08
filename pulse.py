import ROOT
import root_numpy as rnm
import numpy as np

import pulse_calculations as p_calc
import pulse_plot as p_plot
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis(numberOfBatches):
    
    sigma = 8
    p_calc.defineSigmaConstant(sigma)
    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(numberOfBatches)
   
    print "\nStart pulse analysis", numberOfBatches, "batch(es).\n"
    print "Sigma:", p_calc.getSigmaConstant(), "\n"

    for runLog in runLog_batch:
    
        results_batch = []
    
        startTimeBatch = md.getTime()
        md.printTime()
        totalNumberOfRuns = len(runLog)
        
        print "Batch:", runLog[0][5], "\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isRootFileAvailable(md.getTimeStamp())):
                
                results_batch.append(pulseAnalysisPerRun())
        
                md.printTime()
                print "Done with run " + str(runNumber) + ".\n"
        
            else:
                print "WARNING! There is no root file for run number: " + str(runNumber) + "\n"
    
        # Done with the for loop and appending results, export and produce files
        
        print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
        
        amplitudes = np.empty(0, dtype=results_batch[0][0].dtype)
        rise_times = np.empty(0, dtype=results_batch[0][1].dtype)
        peak_times = np.empty(0, dtype=results_batch[0][2].dtype)
        criticalValues = np.empty(0, dtype=results_batch[0][3].dtype)
    
        for results in results_batch:
            amplitudes = np.concatenate((amplitudes, results[0]), axis = 0)
            rise_times = np.concatenate((rise_times, results[1]), axis = 0)
            peak_times = np.concatenate((peak_times, results[2]), axis = 0)
            criticalValues = np.concatenate((criticalValues, results[3]), axis = 0)
        
        dm.exportPulseData(amplitudes, rise_times, peak_times, criticalValues)

        dm.exportPulseData(amplitudes, rise_times, peak_times, criticalValues)
        p_plot.producePulseDistributionPlots(amplitudes, rise_times)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],".\n"

# Perform noise, pulse and telescope analysis
def pulseAnalysisPerRun():
    
    startTimeRun = md.getTime()
    
    # Configure inputs for multiprocessing
    p = Pool(dm.threads)
    max = md.getNumberOfEvents()
    step = 5000
    ranges = range(0, max, step)

    md.printTime()
    print "Start analysing run number: " + str(md.getRunNumber()) + " with "+str(max)+ " events ...\n"
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    pedestal    = dm.importNoiseFile("pedestal")
    noise       = dm.importNoiseFile("noise")
    
    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step), ranges)
 
    # Note, here the function receives the results from multiprocessing
    results = p_calc.removeUnphyscialQuantities(results, noise)
    
    return results


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, pedestal, noise, begin, end):
    
    data = rnm.root2array(dataPath, start=begin, stop=end)
    amplitudes, rise_times, peak_times = p_calc.pulseAnalysis(data, pedestal, noise)
    
    return amplitudes, rise_times, peak_times
