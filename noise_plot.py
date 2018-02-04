import ROOT
import metadata as md
import numpy as np
import data_management as dm

# Note, the function receives in SI units and with negative impulses.

ROOT.gStyle.SetOptFit()

def noisePlots():

    print "Start producing NOISE plots... \n"
    
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"
        
        dm.checkIfRepositoryOnStau()

        noise_average   = np.empty(0)
        noise_std       = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)

        availableRunNumbersNoise        = md.readFileNames("noise_noise")
        availableRunNumbersPedestal     = md.readFileNames("noise_pedestal")
      
        for runNumber in runNumbers:
            
            if runNumber in availableRunNumbersPedestal:
            
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
                
                print "Importing run", md.getRunNumber(), "\n"
                
                if noise_average.size == 0:
                
                    noise_average  = dm.importNoiseFile("pedestal")
                    noise_std      = dm.importNoiseFile("noise")

                else:

                    noise_average = np.concatenate((noise_average, dm.importNoiseFile("pedestal")), axis = 0)
                    noise_std = np.concatenate((noise_std, dm.importNoiseFile("noise")), axis = 0)
    
        if len(noise_average) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"
        
            produceNoiseDistributionPlots(noise_average, noise_std)

    print "Done with producing NOISE plots.\n"

def produceNoiseDistributionPlots(noise_average, noise_std):
    
 
    channels = noise_average.dtype.names
    pedestal_graph = dict()
    noise_graph = dict()
    
    noise_average, noise_std = dm.convertNoiseData(noise_average, noise_std)
    
    for chan in channels:
        
        constant_sigma = 5
        
        pedestal_min = np.average(noise_average[chan]) - constant_sigma*np.std(noise_average[chan])
        pedestal_max = np.average(noise_average[chan]) + constant_sigma*np.std(noise_average[chan])
        
        noise_min = np.average(noise_std[chan]) - constant_sigma*np.std(noise_std[chan])
        noise_max = np.average(noise_std[chan]) + constant_sigma*np.std(noise_std[chan])
        
        
        pedestal_graph[chan] = ROOT.TH1D("Pedestal, channel "+str(int(chan[-1:])), "pedestal"+chan, 1000, pedestal_min, pedestal_max)
        noise_graph[chan]    = ROOT.TH1D("Noise, channel "+str(int(chan[-1:])), "noise"+chan, 1000, noise_min, noise_max)


        for entry in range(0, len(noise_average)):
        
            if noise_std[entry][chan] != 0:
                pedestal_graph[chan].Fill(noise_average[entry][chan])
                noise_graph[chan].Fill(noise_std[entry][chan])
    

        pedestal_graph[chan].Fit("gaus","","", pedestal_min, pedestal_max)
        noise_graph[chan].Fit("gaus","","", noise_min, noise_max)


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

