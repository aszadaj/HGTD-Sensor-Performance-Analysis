import ROOT
import root_numpy as rnm
import numpy as np
import os
import math

import metadata as md
import data_management as dm

def produceResults():
    
    dm.checkIfRepositoryOnStau()
    startTime = md.dm.getTime()
   
    runLog = md.getRunLog()
    
    fileDirectoryResults = dm.getSourceFolderPath() + "results/"
    
    print "\nStart RESULTS"
    
    resultGraphs = dict()
    legend = dict()
    
    canvas = ROOT.TCanvas("Results", "Results")
    
    sensorNames = md.getAllSensorNames()
    #sensorNames = ["W4-S1061"]
    
    sourceResultsFiles = dm.getSourceFolderPath() + "results_hgtd_efficiency_sep_2017/"
    sensorNames.remove("SiPM-AFP")
    
    #typesDirectories = ["noise/", "pulse/", "timing/normal/", "timing/system/"]
    typesDirectories = ["noise/"]

    for sensor in sensorNames:
    
        print "\nSensor", sensor
        fileDirectory = sourceResultsFiles + sensor + "/"
        
        for type in typesDirectories:
            
            if type == "noise/":
                
                # Force select noise instead of pedestal
                #categories = ["pedestal"]
                categories = ["noise", "pedestal"]
                
            elif type == "pulse/":
                
                categories = ["max_amplitude", "rise_time"]
                #categories = ["rise_time"]
            
                
            elif type == "timing/normal/":
                categories = ["time_resolution_DUT"]
            
            elif type == "timing/system/":
                categories = ["time_resolution_DUT_sys_eq"]

            resultsDict = dict()

            for category in categories:
            
                resultsDict.clear()
            
                resultsDict["22"] = []
                resultsDict["-30"] = []
                resultsDict["-40"] = []
            
                resultGraphs[category] = ROOT.TMultiGraph()
                legend[category] = ROOT.TLegend(0.6, 0.9, 0.9, 0.7)

                if category == "noise":
                    titleGraph = "Noise values per bias voltage "
                    xTitle = "Bias voltage [V]"
                    yTitle = "Noise [mV]"
                
                elif category == "pedestal":
                    titleGraph = "Pedestal values per bias voltage "
                    xTitle = "Bias voltage [V]"
                    yTitle = "Pedestal [mV]"

                elif category == "max_amplitude":
                
                    # Change if you have mean values or not
                    titleGraph = "Pulse (MPV) values per voltage "
                    #titleGraph = "Pulse (mean value) values per voltage "
                    xTitle = "Bias voltage [V]"
                    yTitle = "Pulse amplitude [mV]"

                elif category == "rise_time":
                    
                    # Change of you have mean values from fit or not
                    titleGraph = "Rise time values per voltage "
                    xTitle = "Bias voltage [V]"
                    yTitle = "Rise time [ps]"

                elif category == "time_resolution_DUT":
                
                    titleGraph = "Time resolution values per voltage "
                    xTitle = "Bias voltage [V]"
                    yTitle = "Time resolution [ps]"

                files = readFileNames(fileDirectory+type)
             
                for file in files:
                    
                    fileName = fileDirectory+type+file
                    results = rnm.root2array(fileName)
                
                    if type == "pulse/":

                        selected_results = results[category][0][0]
                    
                        # For mean values
                        #selected_results = results[category][0][1]
                    
                    else:
                        selected_results = results[category][0]

                    batchNumber = getBatchNumberFromFile(file)
                    md.defineGlobalVariableRun(md.getRowForBatchNumber(batchNumber))
                    voltage = md.getBiasVoltage(sensor)
                    temperature = str(md.getTemperature())
                    resultsDict[temperature].append([voltage, selected_results])
            
                # At this point, all info is collected
        
            
                colorNumber = 6
                markerStyle = 8

                graph = dict()
                
                for temperature in resultsDict.keys():
                    if len(resultsDict[temperature]) != 0:
                        graph[category] = ROOT.TGraph()

                        graph[category].SetMarkerColor(colorNumber)
                        graph[category].SetMarkerStyle(markerStyle)
                        i = 0

                        for voltage_x_value in resultsDict[temperature]:
                            graph[category].SetPoint(i, voltage_x_value[0], voltage_x_value[1])
                            i += 1
                    

                        resultGraphs[category].Add(graph[category])
                        legend[category].AddEntry(graph[category], str(temperature) + " \circC, " + str(round(graph[category].GetMean(2),3)) + " \pm "+ str(round(graph[category].GetRMS(2),3)) + " mV" , "p")

                        colorNumber += 1
                        markerStyle += 1
          
                    
                resultGraphs[category].Draw("AP")
                legend[category].SetTextSize(0.03)
                legend[category].SetBorderSize(1)
                legend[category].Draw()
                
                resultGraphs[category].SetTitle((titleGraph+" "+sensor))
                resultGraphs[category].GetXaxis().SetTitle(xTitle)
                resultGraphs[category].GetYaxis().SetTitle(yTitle)

                yMin = resultGraphs[category].GetHistogram().GetMinimum()
                yMax = resultGraphs[category].GetHistogram().GetMaximum()
                d = yMax-yMin

                dist = 10

                y_low = yMin - dist*d
                y_high = yMax + dist*d


                # Adapt this depending on graph
                resultGraphs[category].SetMinimum(y_low)
                resultGraphs[category].SetMaximum(y_high)



                canvas.Update()

                fileName = fileDirectoryResults +category+"/" + category + "_results_"+sensor+".pdf"
                
                canvas.Print(fileName)

                canvas.Clear()


def readFileNames(directory):


    # select those which have rise time reference
    if directory.find("timing") != -1:
        availableFiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store' and f.find("cfd05") != -1]
    
    else:
        availableFiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store']
    availableFiles.sort()

    return availableFiles


def getBatchNumberFromFile(file):
    if file[0] == "n" or file[0] == "p":
        return int(file[6:9])
    
    elif file[0] == "t":
        return int(file[7:10])


