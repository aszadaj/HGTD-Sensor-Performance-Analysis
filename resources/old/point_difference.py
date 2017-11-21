
import ROOT
import numpy as np
import pickle
import root_numpy as rnm
import pandas as pd

#### INFO ###

# This file analyses smallest point difference among each entry, for each channel and each provided file.
# Most important function which does the job: pointDifferences(...)


# This main function will analyse files with corresponding run number (see bottom of the file)
def main_pointDifference(runInfo):

    print "point difference"

    for runNumber in runInfo.keys():
        pointDifferencePerFile(runNumber,runInfo[runNumber])
        print "Done with run " + str(runNumber)


# Get point differences per run number/file
def pointDifferencePerFile(runNumber,timeStamp):
    
    # Imports data points, expressed in inverted mV-values
    data, sensors, first_entry, last_entry = importFileDataLong(timeStamp)

    # Get critcal amplitude values calculated earlier
    criticalValues = importPulseProperties(runNumber)
    
    # Get the smallest difference value, for each channel and entry
    difference_values = pointDifferences(data,criticalValues)
    
    # Produce distribution plots
    produceDistributionPlots(difference_values, sensors, runNumber, timeStamp)

# Get smallest point differences, for each entry among all channels. Return as a dictionary, one value per entry and channel
def pointDifferences(data,criticalValues):
    
    # Channel names
    channels = data.dtype.names
    
    # Dictionary for collecting smallest difference values, for each channel
    difference_values = dict()
    
    # Just to avoid problems with appending in next loop
    for chan in channels:
        difference_values[chan] = np.empty(0)
    
    
    for chan in channels:
        for entry in range(0,len(data)):
            
            # Obtain data points w/o critical amplitude values
            indices = np.argwhere(data[entry][chan] < criticalValues[chan])
            data_wo_critical_values = np.take(data[entry][chan], indices)
            
            # Unique: gets unique values and sorts them.
            # Diff: calculates differences between neighbouring points
            min_difference = np.diff(np.unique(data_wo_critical_values)).min()
            difference_values[chan] = np.append(difference_values[chan], min_difference)

    return difference_values


# Import ROOT file and choose which entries to import
def importFileDataFast(timeStamp):

    fileLength = getFileLength(timeStamp)
    
    first_entry = raw_input ("From which entry? (0-"+str(fileLength)+") or m as max: ")

    last_entry = 0
    
    if first_entry != "m":
        
        last_entry = raw_input ("Until which entry? ("+str(first_entry)+"-"+str(fileLength)+") or 'l' as last: ")
        
        if last_entry == "l":
        
            last_entry = fileLength
    else:
        
        first_entry = 0
        last_entry = fileLength

    dataFileName = "/Users/aszadaj/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"
    
    # Future fix to adapt for each run number
    sensors = ["W9-LGA35","50D-GBGR2","W4-LG12","SiPM-AFP","W4-S215","W4-S215","W4-S215","W4-S215"]
    
    data = rnm.root2array(dataFileName, start=int(first_entry), stop=int(last_entry))
    
    # Get provide sensor name and convert to positive mV values
    for chan in data.dtype.names:
        data[chan] = np.multiply(data[chan],-1000)

    return data, sensors, first_entry, last_entry

def importFileDataLong(timeStamp):

    dataFileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"
    
    # Note, these names are specific for the file specified above
    # Here implement import sensors name, not important
    sensors = ["W9-LGA35","50D-GBGR2","W4-LG12","SiPM-AFP","W4-S215","W4-S215","W4-S215","W4-S215"]
    
    data = rnm.root2array(dataFileName)
    
    # Get provide sensor name and convert to positive mV values
    for chan in data.dtype.names:
        data[chan] = np.multiply(data[chan],-1000)

    return data, sensors, 0, getFileLength(timeStamp)


# Reads information from dedicated .csv file
def getMetaData(timeStamp):

    fileName = "/Users/aszadaj/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_" + str(timeStamp) + str(".csv")
    return pd.read_csv(fileName, header=None)

# Get file length from meta data
def getFileLength(timeStamp):
    
    matrix = getMetaData(timeStamp)
    return matrix.sum(axis=0)[24]/8


# Create 8 plots, for each channel across all entries, for amplitudes and rise times
def produceDistributionPlots(difference_values,sensors,runNumber,timeStamp):
    
    canvas = ROOT.TCanvas("point_differences", "Point differences")

    graph = dict()
    
    for chan in difference_values.keys():
       
        graph[chan] = ROOT.TH1D("point_differences_"+chan,"Point Differences "+chan,800,0.013,0.0132)
        
        index = int(chan[-1:])
    
        for entry in range(0,len(difference_values[chan])):
            graph[chan].Fill(difference_values[chan][entry])

        defineAndProduceHistogram(graph[chan],canvas,chan,sensors[index],runNumber,timeStamp)



# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,chan,sensor,runNumber,timeStamp):
    
    xAxisTitle = "Point Differences (mV)"
    yAxisTitle = "Number (N)"
    fileName = "point_difference/point_difference_"+str(runNumber)+"_"+chan+".pdf"
    titleAbove = "Distribution of point differences, for Sep 2017 Run "+str(runNumber)+", for channel " + chan + ", sensor: " + str(sensor)
    
    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    setTitleAboveGraph = titleAbove
    graphList.SetTitle(setTitleAboveGraph)
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)


# Import info evaluated earlier
def importPulseProperties(runNumber):
    
    amplitude = ""
    risetime = ""
    small_amplitude = ""
    criticalValues = ""
    
    with open("/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-Analysis/resources/pulse_info_"+str(runNumber)+".pkl","rb") as input:
        
        amplitude = pickle.load(input)
        risetime = pickle.load(input)
        small_amplitude = pickle.load(input)
        criticalValues = pickle.load(input)
    
    # Convert values to positive
    criticalValues.update((x, y*-1) for x, y in criticalValues.items())
    
    return criticalValues


