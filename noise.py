import ROOT
import numpy as np
import root_numpy as rnm
import json
import pandas as pd

def main_noise(runInfo):

    print "noise"
    
    for runNumber in runInfo.keys():
        noiseAnalysisPerFile(runNumber,runInfo[runNumber])
        print "Done with run " +str(runNumber)


# Analyse noise for selected file
def noiseAnalysisPerFile(runNumber,timeStamp):
    
    pedestals,noise,data,channels = setUpData(timeStamp)
    
    filterData(pedestals,noise,data)
    
    pedestal_final, noise_final = getPedestalStd(pedestals,noise,channels,runNumber)
    
    exportInfo(pedestal_final,runNumber)


# Import ROOT file(s), set up TH1 objects for each channel
# Input: file name and until which entry to read in
# Output: two dictionaries with TH1 objects for pedestals and noises, and channel name types
def setUpData(timeStamp):
    
    dataFileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"

    data = rnm.root2array(dataFileName)
    
    # TH1 objects
    pedestals = dict()
    noise = dict()

    channels = data.dtype.names # gets names for the leafs in TTree file

    for channel in channels:
        
        pedestals[channel] = ROOT.TH1D("Pedestal "+channel,"Pedestal "+channel,100,-10,10)
        noise[channel] = ROOT.TH1D("Noise "+channel,"Noise "+channel,100,0,10)


    return pedestals,noise,data,channels


def setUpDataOld(timeStamp):
    
    fileLength = getFileLength(timeStamp)
    
    end = raw_input ("Until which entry? (0-"+str(fileLength)+") or m as max: ")
    
    dataFileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"

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

# Select data wrt to condition for less than 25 mV and fill histograms for pedestals and noises
# Input: TH1-objects for pedestals and noises for each channel, and data points
def filterData(pedestals,noise,data):
    
    for event in data:
        
        for chan in data.dtype.names:
            
            pulse_compatible_samples = event[chan]<-25*0.001
            max_index = np.where(pulse_compatible_samples)[0][0] - 3 if len( np.where(pulse_compatible_samples)[0] ) else 1002
            
            chan_average = np.average(event[chan][0:max_index])*1000
            chan_std = np.std(event[chan][0:max_index])*1000
            
            pedestals[chan].Fill(chan_average)
            noise[chan].Fill(chan_std)

# Create histograms and get pedestal and noise value for each channel
# Input: TH1-objects for pedestals and noises for each channel, and channel name types
# Output: pedestal and noise value for each channel. 8 values for each dictionary
def getPedestalStd(pedestals,noise,channels,runNumber):
    
    canvas_pedestal = ROOT.TCanvas("Pedestal per Channel", "Pedestal per Channel")
    canvas_noise = ROOT.TCanvas("Noise per Channel", "Noise per Channel")
    pedestal_final = dict()
    noise_final = dict()
    for chan in channels:
        
        titleAbove = "Distribution of mean values (pedestal) for run "+str(runNumber)+", for each entry, for " + chan
        xAxisTitle = "Pedestal mean value (mV)"
        yAxisTitle = "Number of entries (N)"
        setGraphAttributes(pedestals[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        titleAbove = "Distribution of standard deviation values (noise amplitude) for run "+str(runNumber)+" foreach entry, for " + chan
        xAxisTitle = "Standard deviation (mV)"
        yAxisTitle = "Number of entrie (N)"
        setGraphAttributes(noise[chan],titleAbove,xAxisTitle,yAxisTitle)
        
        fileName = "pedestal_distributions/pedestal_"+str(runNumber)+"_"+chan+".pdf"
        pedestal_final[chan] = exportGraph(pedestals[chan],canvas_pedestal,fileName)
        
        fileName = "pedestal_distributions/noise_"+str(runNumber)+"_"+chan+".pdf"
        noise_final[chan] = exportGraph(noise[chan],canvas_noise,fileName)

    return pedestal_final, noise_final

# Define the setup for graphs
# Input: dictionary with TH1 objects, and title information for the graph
def setGraphAttributes(graphList,titleAbove,xAxisTitle,yAxisTitle):
    
    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    setTitleAboveGraph = titleAbove
    graphList.SetTitle(setTitleAboveGraph)

# Produce PDF file for selected channel
# Input: dictionary with TH1 objects, TCanvas object and filename for the produced file
# Output: mean value for selected dictionary and channel
def exportGraph(graphList,canvas,fileName):
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)
    return graphList.GetMean()

# Export pedestal info into .json file
def exportInfo(pedestal,runNumber):
    # save to file:
    data = {}
    fileName = "/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pedestal_"+str(runNumber)+".json"
    with open(fileName, "w") as f:
        data["p"] = pedestal
        json.dump(data,f)

# Reads information from dedicated .csv file
def getFileLength(timeStamp):
    
    fileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_" + str(timeStamp) + str(".csv")
    df = pd.read_csv(fileName, header=None)
    
    fileLength =  df.sum(axis=0)[24]/8

    return fileLength

# Generates which runs are considered located in runlist.csv with corresponding time stamps.
def getRunInfo():
    
    fileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/runlist.csv"
    df = pd.read_csv(fileName, header=None, sep="\t")
    
    runInfo = dict()
    
    for index in range(0,len(df)):
        runInfo[df.iloc[index,0]] = df.iloc[index,1]

    return runInfo

