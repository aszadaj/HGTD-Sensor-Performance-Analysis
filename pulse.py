import ROOT
import root_numpy as rnm
import numpy as np

import pulse_calculations as p_calc
import pulse_plot as p_plot
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

#md.setupATLAS()
ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis(numberOfRuns, step, sigma):
    
    p_calc.defineSigmaConstant(sigma)
    dm.checkIfRepositoryOnStau()
    totalNumberOfRuns = numberOfRuns
    startTime = md.getTime()
    
    print "\n"
    md.printTime()
    print "\nStart pulse analysis, " + str(numberOfRuns) + " file(s)."
    print "Sigma: " + str(p_calc.getSigmaConstant()) + "\n"
   
    runLog = md.restrictToUndoneRuns(md.getRunLog(), "pulse")
    #runLog = md.restrictToBatch(md.getRunLog(), 507)
 
   
    for row in runLog:
    
        md.defineGlobalVariableRun(row)
        runNumber = md.getRunNumber()
        
        if (md.isRootFileAvailable(md.getTimeStamp())):
            
            pulseAnalysisPerRun(step)
            md.printTime()
            print "Done with run " + str(runNumber) + ".\n"
    
        else:
            print "There is no root file for run number: " + str(runNumber) + "\n"
        
        numberOfRuns -= 1
        
        if numberOfRuns == 0:
        
            print "\nFinished with analysis of " + str(totalNumberOfRuns) + " files."
            print "Time analysing: " + str(md.getTime() - startTime) +"\n"
            break
        
        
# Perform noise, pulse and telescope analysis
def pulseAnalysisPerRun(step):
    
    startTimeRun = md.getTime()
    
    p = Pool(dm.threads)
    max = md.getNumberOfEvents()
    ranges = range(0, max, step)
    
    md.printTime()
    print "Start analysing run number: " + str(md.getRunNumber()) + " with "+str(max)+ " events ...\n"
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    pedestal    = dm.importNoiseFile("pedestal")
    noise       = dm.importNoiseFile("noise")
    
    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step), ranges)

    endTime = md.getTime()
    
    md.printTime()
    print "Done with multiprocessing. Time analysing: "+str(endTime-startTimeRun)+"\n"
    print "Start with final analysis and exporting...\n"
    
    results = getResultsFromMultiProcessing(results)
    
    amplitudes, rise_times, criticalValues, peak_times = p_calc.removeUnphyscialQuantities(results, noise)
    
    dm.exportPulseData(amplitudes, rise_times, peak_times, criticalValues)
    p_plot.producePulseDistributionPlots(amplitudes, rise_times)
    
    print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-endTime)+"\n"


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, pedestal, noise, begin, end):
    
    data = rnm.root2array(dataPath, start=begin, stop=end)
    amplitudes, rise_times, peak_times = p_calc.pulseAnalysis(data, pedestal, noise)
    
    return amplitudes, rise_times, peak_times


# Receive results from multiprocessing function
def getResultsFromMultiProcessing(results):

    # Future fix, append is slow
    amplitudes = np.zeros(0, dtype=results[-1][0].dtype)
    rise_times = np.zeros(0, dtype=results[-1][0].dtype)
    peak_times = np.zeros(0, dtype=results[-1][0].dtype)
    
    for i in range(0, len(results)):
        amplitudes = np.append(amplitudes, results[i][0])
        rise_times = np.append(rise_times, results[i][1])
        peak_times = np.append(peak_times, results[i][2])
    
    
    return [amplitudes, rise_times, peak_times]


