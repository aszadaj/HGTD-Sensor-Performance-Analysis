import ROOT
import metadata as md
import numpy as np
import root_numpy as rnm
import data_management as dm


ROOT.gStyle.SetOptFit()


# Concatenate all runs for each batch. When the files are concatenated, produce plots for that batch until
# all batches are considered.
def noisePlots():

    print "\nStart producing NOISE plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"
        
        dm.checkIfRepositoryOnStau()

        noise_average   = np.empty(0)
        noise_std       = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers

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
        
            produceNoisePlots(noise_average, noise_std)

    print "Done with producing NOISE plots.\n"


def produceNoisePlots(noise_average, noise_std):
    
    global canvas, chan
    
    noise_average, noise_std = dm.convertNoiseData(noise_average, noise_std)
    
    canvas = ROOT.TCanvas("Noise", "noise")

    pedestal_graph = dict()
    noise_graph = dict()
    
    channels = noise_average.dtype.names
    #channels = ["chan0"]
 
    # First fill pedestal and noise histograms and create fits
    for chan in channels:
        
        # Automized constants for setting the range of the TH1 graph
        width = 6
        
        pedestal_mean = np.average(noise_average[chan][np.nonzero(noise_average[chan])])
        pedestal_width  = np.std(noise_average[chan][np.nonzero(noise_average[chan])])
        
        pedestal_min = pedestal_mean - width * pedestal_width
        pedestal_max = pedestal_mean + width * pedestal_width
        
  
        noise_mean = np.average(noise_std[chan][np.nonzero(noise_std[chan])])
        noise_width  = np.std(noise_std[chan][np.nonzero(noise_std[chan])])
        
        noise_min = noise_mean - width * noise_width
        noise_max = noise_mean + width * noise_width
        
        
        pedestal_graph[chan] = ROOT.TH1D("Pedestal " + md.getNameOfSensor(chan), "pedestal"+chan, 1000, pedestal_min, pedestal_max)
        
        noise_graph[chan]    = ROOT.TH1D("Noise " + md.getNameOfSensor(chan), "noise"+chan, 1000, noise_min, noise_max)

        for entry in range(0, len(noise_average)):

            if noise_std[entry][chan] != 0:
                pedestal_graph[chan].Fill(noise_average[entry][chan])
                noise_graph[chan].Fill(noise_std[entry][chan])
    
        # Automized constants for setting the range of the Gauss Fit
        width = 4.5
    
        pedestal_min = pedestal_mean - width * pedestal_width
        pedestal_max = pedestal_mean + width * pedestal_width
        
        noise_min = noise_mean - width * noise_width
        noise_max = noise_mean + width * noise_width
        
        pedestal_graph[chan].Fit("gaus","","", pedestal_min, pedestal_max)
        noise_graph[chan].Fit("gaus","","", noise_min, noise_max)


        headTitle = "Standard deviation values "+md.getNameOfSensor(chan)+", Sep 2017 B"+str(md.getBatchNumber())
        xAxisTitle = "Standard deviation (mV)"
        yAxisTitle = "Number of entries (N)"
        fileName = str(md.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/noise/noise_plots/noise_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistograms(noise_graph[chan], titles)
        
        
        headTitle = "Average values (pedestal) "+md.getNameOfSensor(chan)+", Sep 2017 B"+str(md.getBatchNumber())
        xAxisTitle = "Average value (mV)"
        yAxisTitle = "Number of entries (N)"
        fileName = str(md.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/noise/pedestal_plots/pedestal_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistograms(pedestal_graph[chan], titles)


# Produce histograms
def exportHistograms(graphList, titles):

    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw()
    canvas.Update()
    canvas.Print(titles[3])

