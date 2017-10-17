import ROOT
import numpy as np
import root_numpy as rnm

def main():
    end = raw_input ("Until which entry? (0-200 000) or m as max: ")
    fileName = "~/cernbox/oscilloscope_data/data_1504818689.tree.root"
    
    pedestals,noise,data,channels = setUpData(fileName,end)
    filterData(pedestals,noise,data)
    noise_info = getPedestalStd(pedestals,noise,channels)


def setUpData(dataFileName,end):
    
    data = ""
    
    if end == "m":
        data = rnm.root2array(dataFileName)
    else:
        data = rnm.root2array(dataFileName,stop=int(end))

    # TH1 objects
    pedestals = dict()
    noise = dict()

    channels = data.dtype.names # gets names for the leafs in TTree file

    for channel in channels:
        
        pedestals[channel] = ROOT.TH1D("Pedestal "+channel,"Pedestal "+channel,100,-10,10)
        noise[channel] = ROOT.TH1D("Noise "+channel,"Noise "+channel,100,0,10)
    
    return pedestals,noise,data,channels


def filterData(pedestals,noise,data):
    
    for event in data:
        
        for chan in data.dtype.names:
            
            pulse_compatible_samples = event[chan]<-25*0.001
            max_index = np.where(pulse_compatible_samples)[0][0] - 3 if len( np.where(pulse_compatible_samples)[0] ) else 1002
            
            chan_average = np.average(event[chan][0:max_index])*1000
            chan_std = np.std(event[chan][0:max_index])*1000
            
            pedestals[chan].Fill(chan_average)
            noise[chan].Fill(chan_std)


def getPedestalStd(pedestals,noise,channels):
    
    canvas_pedestal = ROOT.TCanvas("Pedestal per Channel", "Pedestal per Channel")
    canvas_noise = ROOT.TCanvas("Noise per Channel", "Noise per Channel")

    for chan in channels:
        
        titleAbove = "Distribution of pedestal mean value for each entry, for " + chan
        xAxisTitle = "Pedestal mean value (mV)"
        yAxisTitle = "Number (N)"
        setGraphAttributes(pedestals[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        titleAbove = "Distribution of pedestal standard deviation values for each entry, for " + chan
        xAxisTitle = "Standard distribution (mV)"
        yAxisTitle = "Number (N)"
        setGraphAttributes(noise[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        fileName = "pedestal_channel/distribution_pedestal_"+chan+".pdf"
        exportGraph(pedestals[chan],canvas_pedestal,fileName)
        
        fileName = "pedestal_channel/distribution_noise_"+chan+".pdf"
        exportGraph(noise[chan],canvas_noise,fileName)
# FILL IN RETURN VALUES FOR PEDESTAL AND NOISE FOR EACH FINAL CHANNEL


def setGraphAttributes(graphList,titleAbove,xAxisTitle,yAxisTitle):
    
    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    setTitleAboveGraph = titleAbove
    graphList.SetTitle(setTitleAboveGraph)


def exportGraph(graphList,canvas,fileName):
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)



main()

