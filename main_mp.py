import ROOT
import root_numpy
import time
import numpy

import pulse as ps
import noise as ns
import pulse_plot as p_plot
import noise_plot as n_plot
import metadata as md

from pathos.multiprocessing import ProcessingPool as Pool
from datetime import datetime

ROOT.gROOT.SetBatch(True) # suppress the creation of canvases on the screen.. much much faster if over a remote connection

def main():

    #setupATLAS()
    # Choose which run was last done and how many files shoud be analysed in next order
    lastRunNumber = 3747 # Ok to run until 3844
    numberOfRuns = 10
    threads = 4
    step = 10000
    
    # Import run log from TB September 2017
    runLog = md.getRunLog(numberOfRuns, lastRunNumber)
    
    # Start processing each selected runs
    for input in runLog:
        
        md.globVar(input)
        
        runNumber = md.getRunNumber()
        
        print "Run number: " + str(runNumber)
        analyseDataForRunNumber(threads, step)
        print "\nDone with run " + str(runNumber) + ".\n"
  
    exit()


########## MAIN ANALYSIS ##########

# Perform noise, pulse and telescope analysis
def analyseDataForRunNumber(threads, step):

    print "\nImporting file for run number " + str(md.getRunNumber()) + " ... \n"
    
    # Start multiprocessing
    p = Pool(threads)
    max = md.getNumberOfEvents()
    ranges = range(0, max, step)
    dataPath = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    printTime()
    print "\nStart Multiprocessing \n"
    
    results = p.map(lambda chunk: oscilloscopeAnalysis(dataPath,chunk,chunk+step),ranges)
    
    printTime()
    print "\nDone with multiprocessing \n"
    
    
    noise_average = numpy.zeros(0, dtype=results[-1][0].dtype)
    noise_std = numpy.zeros(0, dtype=results[-1][0].dtype)
    amplitudes = numpy.zeros(0, dtype=results[-1][0].dtype)
    rise_times = numpy.zeros(0, dtype=results[-1][0].dtype)
    
    for i in range(0,len(results)):
        noise_average = numpy.append(noise_average, results[i][0])
        noise_std = numpy.append(noise_std, results[i][1])
        amplitudes = numpy.append(amplitudes, results[i][2])
        rise_times = numpy.append(rise_times, results[i][3])
    
    
    # Some final analysis
    pedestal, noise = ns.getPedestalNoisePerChannel(noise_average, noise_std)

    amplitudes, rise_times, criticalValues = ps.removeUnphyscialAmplitudes(amplitudes, rise_times, noise)

    # Export and produce distribution plots
 
    ns.exportNoiseInfo(pedestal, noise)
    ns.produceNoiseDistributionPlots(noise_average, noise_std)
    
    ps.exportPulseInfo(amplitudes, rise_times, criticalValues)
    p_plot.producePulseDistributionPlots(amplitudes, rise_times, pedestal)


def oscilloscopeAnalysis(dataPath, begin, end):
    
    data = root_numpy.root2array(dataPath, start=begin, stop=end)
    data = convertOscilloscopeData(data)
    
    noise_average, noise_std = ns.noiseAnalysis(data)
    amplitudes, rise_times = ps.pulseAnalysis(data, noise_average, noise_std)
    
    return noise_average, noise_std, amplitudes, rise_times

    # Future fix, leave it for now
    #data_telescope = importTelescopeData(timeStamp)
    #telescopeAnalysisPerFile(data_telescope, runNumber, timeStamp, sensors[runNumber])


# Import data file,  all entries
def convertOscilloscopeData(data):
  
    # Invert minus sign and change from V to mV
    for chan in data.dtype.names:
        data[chan] = numpy.multiply(data[chan],-1000)

    return data


# Note, the file have only 200K entries
def importTelescopeData():
  
    dataFileName = "~/cernbox/SH203X/HGTD_material/telescope_data_sep_2017/tracking"+str(md.getTimeStamp())+".root"
    data = root_numpy.root2array(dataFileName)
    
    # Convert into mm
    for dimension in data.dtype.names:
        data[dimension] = numpy.multiply(data[dimension], 0.001)
  
    return data, dataFileName


########## OTHER ##########

def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])


def setupATLAS():

    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("./style/AtlasStyle.C")
    ROOT.SetAtlasStyle()



########## MAIN ###########

main()

##########################

