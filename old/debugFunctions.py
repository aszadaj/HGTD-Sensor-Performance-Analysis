
import ROOT
import numpy as np
import pickle
import root_numpy as rnm
import json
import pandas as pd

def main_debugFunctions(runInfo):

    print "debugFunctions"

    for runNumber in runInfo.keys():
        debugFunctionsPerFile(runNumber,runInfo[runNumber])
        print "Done with run " + str(runNumber)


def getRunInfo():
    
    fileName = "/Users/aszadaj/cernbox/SH203X/HGTD_material/runlist_HGTD_September_2017/tb_sep17_run_log/RunLog-Table1.csv"
    df = pd.read_csv(fileName)
    
    runInfo = dict()
    
    for index in range(0,len(df)):
        runInfo[df.iloc[index,0]] = df.iloc[index,1]
   
    return runInfo



# The code obtains amplitudes and rise time for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def debugFunctionsPerFile(runNumber,timeStamp):
    
    # elements are inverted, positive value for extremal amplitude value
    data, sensors, first_entry, last_entry = importFileData(timeStamp)

    amplitude, risetime, small_amplitude, criticalValues = importPulseProperties(runNumber)
    
    difference_values = pointDifferences(data,criticalValues)
    
    produceDistributionPlots(difference_values, sensors, runNumber, timeStamp)
    
    #exportResults(difference_values,runNumber)
    
    #pedestal = importNoiseProperties(runNumber)

# Get smallest point differences, for each entry among all channels. Return as a dictionary, one value per entry and channel
def pointDifferences(data,criticalValues):

    pointDiff = dict()
    
    for chan in data.dtype.names:
        pointDiff[chan] = np.empty(0)

    for chan in data.dtype.names:
        for entry in range(0,len(data)):
            
            # Obtain data points w/o critical amplitude values
            indices = np.argwhere(data[entry][chan] < criticalValues[chan])
            data_wo_critical_values = np.take(data[entry][chan], indices)
            
            # Unique: gets unique values and sorts them.
            # Diff: calculates differences between neighbouring points
            min_difference = np.diff(np.unique(data_wo_critical_values)).min()
            pointDiff[chan] = np.append(pointDiff[chan], min_difference)

    return pointDiff


# Import ROOT file and choose which entries to import
def importFileData(timeStamp):

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
    
    # Note, these names are specific for the file specified above
    # Here implement import sensors name, not important for now
    sensors = ["W9-LGA35","50D-GBGR2","W4-LG12","SiPM-AFP","W4-S215","W4-S215","W4-S215","W4-S215"]
    
    data = rnm.root2array(dataFileName, start=int(first_entry), stop=int(last_entry))
    
    # Get provide sensor name and convert to positive mV values
    for chan in data.dtype.names:
        data[chan] = np.multiply(data[chan],-1000)

    return data, sensors, first_entry, last_entry



# Import JSON file for pedestal and noise information from noise analysis
def importNoiseProperties(runNumber):
    
    fileName = "/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources_copy/pedestal_"+str(runNumber)+".json"
    
    # load from file:
    with open(fileName, 'r') as f:
        
        try:
            data = json.load(f)
        
        # if the file is empty the ValueError will be thrown
        except ValueError:
            
            print "The file  " + str(fileName) + " is empty or cannot be read."
            data = {}

    return data["p"]


# Reads information from dedicated .csv file
def getMetaData(timeStamp):

    fileName = "/Users/aszadaj/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_" + str(timeStamp) + str(".csv")
    return pd.read_csv(fileName, header=None)

# Get file length from meta data
def getFileLength(timeStamp):
    
    matrix = getMetaData(timeStamp)
    return matrix.sum(axis=0)[24]/8

# Obtain time scope for respective file
def getTimeScope(timeStamp):

    matrix = getMetaData(timeStamp)
    
    timeScope = matrix.iloc[0,4]
    
    # Return value in ns
    return timeScope*1000000000


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



# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importPulseProperties(runNumber):
    
    amplitude = ""
    risetime = ""
    small_amplitude = ""
    criticalValues = ""
    
    with open("/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-Analysis/resources_copy/pulse_info_"+str(runNumber)+".pkl","rb") as input:
        
        amplitude = pickle.load(input)
        risetime = pickle.load(input)
        small_amplitude = pickle.load(input)
        criticalValues = pickle.load(input)
    
    # Convert all values to positive
    amplitude.update((x, y*-1) for x, y in amplitude.items())
    small_amplitude.update((x, y*-1) for x, y in small_amplitude.items())
    criticalValues.update((x, y*-1) for x, y in criticalValues.items())
    
    return amplitude, risetime, small_amplitude, criticalValues

# Export difference value as a .pkl file
def exportResults(difference_values,runNumber):
    
    with open("/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources_copy/point_differences_"+str(runNumber)+".pkl","wb") as output:
        
        # difference_values is a dictionary with channels as keys
        pickle.dump(difference_values,output,pickle.HIGHEST_PROTOCOL)


def getRunMetaData():
    
    fileName = "/Users/aszadaj/cernbox/SH203X/HGTD_material/runlist_HGTD_September_2017/tb_sep17_run_log/RunLog-Table1.csv"
    df = pd.read_csv(fileName)
    
    print df
    
    runInfo = dict()
    
#    for index in range(0,len(df)):
#        runInfo[df.iloc[index,0]] = df.iloc[index,1]

    return runInfo


runInfo = getRunInfo()

