import ROOT
import pickle
import numpy as np
import root_numpy as rnm
import os

import metadata as md
import data_management as dm
import noise_plot as n_plot
import noise_calculations as n_calc

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)

def noiseAnalysis(numberOfRuns, step):
    print "noise"
    dm.checkIfRepositoryOnStau()
    totalNumberOfRuns = numberOfRuns
    startTime = md.getTime()
    
    print "\n"
    md.printTime()
    print "Start noise analysis, " + str(numberOfRuns) + " file(s)."
   
    runLog = md.restrictToUndoneRuns(md.getRunLog(), "noise")
   
    for row in runLog:
    
        md.defineGlobalVariableRun(row)
        runNumber = md.getRunNumber()
        
        if (md.isRootFileAvailable(md.getTimeStamp())):
            
            noiseAnalysisPerRun(step)
            
            md.printTime()
            print "Done with run " + str(runNumber) + ".\n"
    
        else:
            print "There is no root file for run number: " + str(runNumber) + "\n"
        
        
        numberOfRuns -= 1
        if numberOfRuns == 0:
        
            print "\nFinished with analysis of " + str(totalNumberOfRuns) + " files."
            print "Time analysing: " + str(md.getTime() - startTime) +"\n"
            break


def noiseAnalysisPerRun(step):
    
    startTime = md.getTime()
    
    p = Pool(dm.threads)
    max = md.getNumberOfEvents()
    ranges = range(0, max, step)
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    md.printTime()
    print "Start analysing run number: " + str(md.getRunNumber()) + " with "+str(max)+ " events ...\n"
    
    results = p.map(lambda chunk: n_calc.findNoiseAverageAndStd(dataPath,chunk,chunk+step),ranges)

    endTime = md.getTime()
    md.printTime()
    
    print "Done with multiprocessing. Time analysing: "+str(endTime-startTime)+"\n"
    print "Start with final analysis and exporting...\n"
    
    noise_average, noise_std = getResultsFromMultiProcessing(results)
    noise_average, noise_std = n_calc.convertNoise(noise_average, noise_std)
    
    n_plot.produceNoiseDistributionPlots(noise_average, noise_std)
    
    pedestal, noise = n_calc.getPedestalAndNoisePerChannel(noise_average, noise_std)
    dm.exportNoiseData(pedestal, noise)
    
    print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-endTime)+"\n"



# Receive results from multiprocessing function
def getResultsFromMultiProcessing(results):

    # Future fix, append is slow
    noise_average = np.zeros(0, dtype=results[-1][0].dtype)
    noise_std = np.zeros(0, dtype=results[-1][0].dtype)
    
    for i in range(0,len(results)):
        noise_average = np.append(noise_average, results[i][0])
        noise_std = np.append(noise_std, results[i][1])


    return noise_average, noise_std




