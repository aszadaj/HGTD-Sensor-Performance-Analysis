import ROOT
import metadata as md
import numpy as np
import data_management as dm

# Note, the function receives in SI units and with negative impulses.

ROOT.gStyle.SetOptFit()

def noisePlots():
    
    for batchNumber in md.batchNumbers:
        
        dm.checkIfRepositoryOnStau()

        noise_average   = np.empty(0)
        noise_std       = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)

        availableRunNumbersNoise        = md.readFileNames("noise_noise")
        availableRunNumbersPedestal     = md.readFileNames("noise_pedestal")
        
        count = 0
        for runNumber in runNumbers:
            
            if runNumber in availableRunNumbersPedestal and count < 1:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
                
                if noise_average.size == 0:
                
                    noise_average  = dm.importNoiseFile("pedestal")
                    noise_std      = dm.importNoiseFile("noise")

                else:

                    noise_average = np.concatenate((noise_average, dm.importNoiseFile("pedestal")), axis = 0)
                    noise_std = np.concatenate((noise_std, dm.importNoiseFile("noise")), axis = 0)
                    
            count +=1
            
        produceNoiseDistributionPlots(noise_average, noise_std)


def produceNoiseDistributionPlots(noise_average, noise_std):
    
    
    channels = noise_average.dtype.names
    pedestal_graph = dict()
    noise_graph = dict()
    
    noise_average, noise_std = dm.convertNoiseData(noise_average, noise_std)
    
    for chan in channels:
        
        pedestal_mean   = np.average(np.take(noise_average[chan], np.nonzero(noise_average[chan]))[0])
        noise_mean      = np.average(np.take(noise_std[chan], np.nonzero(noise_std[chan]))[0])
        
    
        noise_graph[chan]    = ROOT.TH1D("Noise, channel "+str(int(chan[-1:])), "noise"+chan, 1000, noise_mean-3, noise_mean+3)
        pedestal_graph[chan] = ROOT.TH1D("Pedestal, channel "+str(int(chan[-1:])), "pedestal"+chan, 1000, pedestal_mean-3, pedestal_mean+3)


        for entry in range(0, len(noise_average)):
        
            if noise_average[entry][chan] != 0:
                pedestal_graph[chan].Fill(noise_average[entry][chan])
                noise_graph[chan].Fill(noise_std[entry][chan])
    
        
        pedestal_graph[chan].Fit("gaus","","", pedestal_graph[chan].GetMean()-3, pedestal_graph[chan].GetMean()+3)
        noise_graph[chan].Fit("gaus","","", noise_graph[chan].GetMean()-3, noise_graph[chan].GetMean()+3)


    canvas_pedestal = ROOT.TCanvas("Pedestal per channel", "Pedestal per channel")
    canvas_noise = ROOT.TCanvas("Noise per channel", "Noise per channel")
   
    for chan in channels:
    
        titleAbove = "Distribution of standard deviation values (noise) from each entry, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Standard deviation (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(noise_graph[chan], titleAbove, xAxisTitle, yAxisTitle)
        
        
        titleAbove = "Distribution of noise mean values (pedestal) from each entry, batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) +", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Mean value (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(pedestal_graph[chan], titleAbove, xAxisTitle, yAxisTitle)
        
        fileName = str(md.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/noise/pedestal_plots/pedestal_"+str(md.getBatchNumber())+"_"+chan+".pdf"
        
        exportGraph(pedestal_graph[chan], canvas_pedestal, fileName)
        
        fileName = str(md.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/noise/noise_plots/noise_"+str(md.getBatchNumber())+"_"+chan+".pdf"
        
        exportGraph(noise_graph[chan], canvas_noise, fileName)
    
    del canvas_pedestal, canvas_noise



# Define the setup for graphs
# Input: dictionary with TH1 objects, and title information for the graph
def setGraphAttributes(graphList,titleAbove,xAxisTitle,yAxisTitle):
    
    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    setTitleAboveGraph = titleAbove
    graphList.SetTitle(setTitleAboveGraph)


# Produce PDF file for selected chan
# Input: dictionary with TH1 objects, TCanvas object and filename for the produced file
# Output: mean value for selected dictionary and chan
def exportGraph(graphList,canvas,fileName):
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)



def convertNoiseData(noise_std, noise_average):
    
    for chan in noise_std.dtype.names:
        noise_average[chan] =  np.multiply(noise_average[chan], 1000)
        noise_std[chan] = np.multiply(noise_std[chan], 1000)

    return noise_average, noise_std
