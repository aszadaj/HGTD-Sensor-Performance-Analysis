
import ROOT
import metadata as md


def produceNoiseDistributionPlots(noise_average, noise_std):
    
    channels = noise_average.dtype.names
    sensors = md.getSensorNames()
    pedestal_graph = dict()
    noise_graph = dict()
    
    for chan in channels:
        
        pedestal_graph[chan] = ROOT.TH1D("Pedestal channel "+str(int(chan[-1:])+1),"pedestal"+chan,300,-5,5)
        noise_graph[chan] = ROOT.TH1D("Noise channel "+str(int(chan[-1:])+1),"noise"+chan,300,0,7)
    
        for entry in range(0,len(noise_average)):
            pedestal_graph[chan].Fill(noise_average[entry][chan])
            noise_graph[chan].Fill(noise_std[entry][chan])
    
    canvas_pedestal = ROOT.TCanvas("Pedestal per channel", "Pedestal per channel")
    canvas_noise = ROOT.TCanvas("Noise per channel", "Noise per channel")
   
    for chan in channels:
    
        chan_index = int(chan[-1:])
        
        titleAbove = "Distribution of noise mean values from each entry, run "+str(md.getRunNumber())+", channel " + str(chan_index+1) +", sensor: " + str(sensors[chan_index])
        xAxisTitle = "Noise mean value (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(pedestal_graph[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        titleAbove = "Distribution of standard deviation values (noise) from each entry, Sep 2017 run "+str(md.getRunNumber())+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
        xAxisTitle = "Standard deviation (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(noise_graph[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        fileName = "plots/pedestal_distributions/pedestal_plots/pedestal_"+str(md.getRunNumber())+"_"+chan+".pdf"
        exportGraph(pedestal_graph[chan],canvas_pedestal,fileName)
        
        fileName = "plots/pedestal_distributions/noise_plots/noise_"+str(md.getRunNumber())+"_"+chan+".pdf"
        exportGraph(noise_graph[chan],canvas_noise,fileName)


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


