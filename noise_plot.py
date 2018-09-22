import ROOT
import numpy as np
import root_numpy as rnm

import run_log_metadata as md
import data_management as dm

ROOT.gStyle.SetOptFit()

# Concatenate all runs for each batch. When the files are concatenated, produce plots for that batch until
# all batches are considered.
def noisePlots():

    print "\nStart producing NOISE plots, batches:", md.batchNumbers
        
    dm.defineDataFolderPath()
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"

        runNumbers = md.getAllRunNumbers(batchNumber)
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(2)]
        var_names = ["noise", "pedestal"]
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers


        for runNumber in runNumbers:
            
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
            
            if runNumber not in md.getRunsWithSensor(md.sensor):
                continue
            
            print "Importing run", md.getRunNumber(), "\n"
            
            for index in range(0, len(var_names)):
                numpy_arrays[index] = np.concatenate((numpy_arrays[index], dm.exportImportROOTData("noise_plot", var_names[index], False)), axis = 0)

    
        if len(numpy_arrays[0]) != 0:
       
            produceNoisePlots(numpy_arrays[0], numpy_arrays[1])

    print "Done with producing NOISE plots.\n"


def produceNoisePlots(noise_std, noise_average):
    
    global canvas, chan
    
    dm.changeIndexNumpyArray(noise_std, 1000)
    dm.changeIndexNumpyArray(noise_average, -1000)
    
    canvas = ROOT.TCanvas("Noise", "noise")
    
    # First fill pedestal and noise histograms and create fits
    for chan in noise_average.dtype.names:
      
        print md.getNameOfSensor(chan), "\n"
        
        noise_avg_std, pedestal_avg_std = getAvgStd(noise_std, noise_average)
        noise_ranges, pedestal_ranges = getRanges(noise_avg_std, pedestal_avg_std, 6)
        
        noise_th1d    = ROOT.TH1D("Noise", "noise", 100, noise_ranges[0], noise_ranges[1])
        pedestal_th1d = ROOT.TH1D("Pedestal", "pedestal", 100, pedestal_ranges[0], pedestal_ranges[1])

        for entry in range(0, len(noise_average)):
            if noise_std[entry][chan] != 0:
                noise_th1d.Fill(noise_std[entry][chan])
                pedestal_th1d.Fill(noise_average[entry][chan])
    
    
        noise_ranges, pedestal_ranges = getRanges(noise_avg_std, pedestal_avg_std, 3)

        noise_th1d.Fit("gaus","Q","", noise_ranges[0], noise_ranges[1])
        pedestal_th1d.Fit("gaus","Q","", pedestal_ranges[0], pedestal_ranges[1])
        
        exportHistogramsAndResults(noise_th1d, pedestal_th1d)

        del pedestal_th1d, noise_th1d



def exportHistogramsAndResults(noise_th1d, pedestal_th1d):

    noise_result    = np.empty(2, dtype=[('noise', '<f8')])
    pedestal_result = np.empty(2, dtype=[('pedestal', '<f8')])
    
    noise_result["noise"]       = [noise_th1d.GetFunction("gaus").GetParameter(1), noise_th1d.GetFunction("gaus").GetParError(1)]
    pedestal_result["pedestal"] = [pedestal_th1d.GetFunction("gaus").GetParameter(1), pedestal_th1d.GetFunction("gaus").GetParError(1)]


    dm.exportImportROOTData("results", "noise", True, noise_result, chan)
    dm.exportImportROOTData("results", "pedestal", True, pedestal_result, chan)

    exportHistograms(noise_th1d)
    exportHistograms(pedestal_th1d)


# Produce histograms
def exportHistograms(graphList):

    canvas.Clear()

    ROOT.gStyle.SetOptStat("ne")
    ROOT.gStyle.SetOptFit(0012)
    
    titles = getPlotAttributes(graphList.GetTitle())

    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw()
    canvas.Update()
    dm.exportImportROOTHistogram(titles[3], True, graphList)
    canvas.Print(titles[3])
    

def getPlotAttributes(name):

    
    if name.find("noise") != -1:

        head_title_type = "Noise"
        xAxisTitle = "Standard deviation [mV]"
 
    else:

        head_title_type = "Pedestal"
        xAxisTitle = "Average value [mV]"


    headTitle = head_title_type + " - " + md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
    fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder()+"/"+md.getNameOfSensor(chan)+"/noise/"+name+"_plots/"+name+"_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    return [headTitle, xAxisTitle, "Entries", fileName]


def getAvgStd(noise_std, noise_average):
    
    noise_avg   = np.average(noise_std[chan][np.nonzero(noise_std[chan])])
    noise_std  = np.std(noise_std[chan][np.nonzero(noise_std[chan])])
    
    pedestal_avg = np.average(noise_average[chan][np.nonzero(noise_average[chan])])
    pedestal_std  = np.std(noise_average[chan][np.nonzero(noise_average[chan])])

    return [noise_avg, noise_std], [pedestal_avg, pedestal_std]


def getRanges(noise_avg_std, pedestal_avg_std, N):

    noise_ranges = [noise_avg_std[0] - N * noise_avg_std[1], noise_avg_std[0] + N * noise_avg_std[1]]
    pedestal_ranges = [pedestal_avg_std[0] - N * pedestal_avg_std[1], pedestal_avg_std[0] + N * pedestal_avg_std[1]]

    return noise_ranges, pedestal_ranges


