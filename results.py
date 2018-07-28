import ROOT
import root_numpy as rnm
import numpy as np
import os
import math

import metadata as md
import data_management as dm


def produceResults():

    dm.defineDataFolderPath()
    
    print "\nStart RESULTS"
    
    resultGraphs = dict()
    legend = dict()
    
    canvas = ROOT.TCanvas("Results", "Results")
    
    sensorNames = md.getAllSensorNames()
    
    # ROOT data source
    sourceResultsFiles = dm.getSourceFolderPath() + "results_data_hgtd_efficiency_sep_2017/"
    
    categories = ["noise", "pedestal", "peak_value", "charge", "rise_time", "timing_normal", "timing_system", "timing_normal_cfd05", "timing_system_cfd05"]


    resultsDict = dict()

    
    # loop through each category
    for category in categories:
    
        print category, "\n"
    
        category_graph = ROOT.TMultiGraph()
        legend_graph = ROOT.TLegend(0.7, 0.9, 0.9, 0.6)
        
        graph = dict()
        
        for sensor in sensorNames:
        
            graph[sensor] = dict()
            sensor_data = dict()
            
            # Create TGraphErrors for each sensor, temperature and position (in the case of array pads)
            for temperature in md.availableTemperatures():
                
                graph[sensor][temperature] = dict()
                sensor_data[temperature] = dict()
                
                # availableDUTPositions(sensor) consider only one pad so far.
                
                for DUT_pos in md.availableDUTPositions(sensor):
                    graph[sensor][temperature][DUT_pos] = ROOT.TGraphErrors()
                    sensor_data[temperature][DUT_pos] = []
                    
                    # Change each marker type and color
                    setMarkerType(graph[sensor][temperature][DUT_pos], sensor, DUT_pos, temperature)
        
            # Import results for the sensor and category
            fileDirectory = sourceResultsFiles + sensor + "/" + category + "/"
            files = readFileNames(fileDirectory)

            
            # here are imported all files, that is for each pad, temperature and bias voltage
            for file in files:

                chan = "chan" + file[file.find("chan")+4]
                results = rnm.root2array(fileDirectory+file)
                
                batchNumber = getBatchNumberFromFile(file)
                md.defineGlobalVariableRun(md.getRowForBatchNumber(batchNumber))
        
                if batchNumber in omitBadDataBatches(chan):
                    continue
            
                
                value = results[0][0]
                error = results[1][0]
                voltage = md.getBiasVoltage(sensor)
                temperature = str(md.getTemperature())
                DUT_pos = md.getDUTPos(chan)
                sensor_data[temperature][DUT_pos].append([voltage, value, error])


            oneSensorInLegend = True
            
            # availableDUTPositions(sensor) consider only one pad so far.
            for DUT_pos in md.availableDUTPositions(sensor):
            
                if DUT_pos in ["3_0", "3_1", "3_3", "8_1", "7_2", "7_3"]:
                    continue
                
                for temperature in md.availableTemperatures():
                
                    sensor_data[temperature][DUT_pos].sort()
                    
                    
                    i = 0
                    for data in sensor_data[temperature][DUT_pos]:
                        
                        constant = 1
                        if category == "charge":
                            constant = 1./(0.46) # Divide by MIP charge = Gain
                    
                        graph[sensor][temperature][DUT_pos].SetPoint(i, data[0], data[1]*constant)
                        graph[sensor][temperature][DUT_pos].SetPointError(i, 0, data[2])
                        
                        i += 1
                    
                    if graph[sensor][temperature][DUT_pos].GetN() != 0:
                        category_graph.Add(graph[sensor][temperature][DUT_pos])
                        
                        if oneSensorInLegend:
                            legend_graph.AddEntry(graph[sensor][temperature][DUT_pos], sensor, "p")
                        
                        oneSensorInLegend = False
            

    
    
        category_graph.Draw("APL")
        setGraphAttributes(category_graph, category, sensor)


        legend_graph.Draw()
        
        # Draw extra legend with information about the coloring
        legend_text = ROOT.TLatex()
        legend_text.SetTextSize(0.035)
        legend_text.SetNDC(True)
        legend_text.DrawLatex(.7, .55, "Marker color")
        legend_text.DrawLatex(.7, .5, "#color[2]{Red}    = 22\circC")
        legend_text.DrawLatex(.7, .45, "#color[4]{Blue}   = -30\circC")
        legend_text.DrawLatex(.7, .4, "#color[3]{Green} = -40\circC")
        
        fileName = dm.getSourceFolderPath() + "results_hgtd_efficiency_sep_2017/" + "/" + category + "_results.pdf"
        canvas.Print(fileName)


# Read in results files for each category
def readFileNames(directory):

    availableFiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store']
    availableFiles.sort()
    
    return availableFiles


def getBatchNumberFromFile(file):
    return int(file[file.find("chan")-4:file.find("chan")-1])


def omitBadDataBatches(chan):

    list = [801, 802, 803, 804, 805, 806]

    sensor = md.getNameOfSensor(chan)

    if sensor == "W4-RD01":

        list.append(606)
    
    elif sensor == "W4-S203":

        list.append(704)
        list.append(705)
        list.append(706)

    elif sensor == "W4-S215":
    
        list.append(405)
        list.append(406)
        list.append(706)
    
    elif sensor == "W4-S1022":
        
        list.append(405)
        list.append(705)
        list.append(706)

    elif sensor == "W4-S1061":
        
        list.append(406)
        list.append(705)
        list.append(706)


    return list


def setGraphAttributes(category_graph, category, sensor):

    # Define titles, head and axes
    if category == "noise":
        titleGraph = "Noise values per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Noise [mV]"
        y_lim = [0, 10]
    
    elif category == "pedestal":
        titleGraph = "Pedestal values per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Pedestal [mV]"
        y_lim = [-10, 10]

    elif category == "peak_value":
    
        titleGraph = "Pulse amplitude values per voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Pulse amplitude [mV]"
        y_lim = [0, 300]

    elif category == "charge":
    
        titleGraph = "Gain values per voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Gain"
        y_lim = [0, 200]

    elif category == "rise_time":
        
        titleGraph = "Rise time values per voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Rise time [ps]"
        y_lim = [0, 2000]

    elif category == "timing_normal":
    
        titleGraph = "Time resolution values per voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]


    elif category == "timing_normal_cfd05":
    
        titleGraph = "Time resolution values per voltage (cfd05)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]

    elif category == "timing_system":
    
        titleGraph = "Time resolution values per voltage (system)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]

    elif category == "timing_system_cfd05":
    
        titleGraph = "Time resolution values per voltage (system, cfd05)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]

    category_graph.SetTitle(titleGraph)
    category_graph.GetXaxis().SetTitle(xTitle)
    category_graph.GetYaxis().SetTitle(yTitle)

    category_graph.GetXaxis().SetLimits(0, 500)
    category_graph.SetMinimum(y_lim[0])
    category_graph.SetMaximum(y_lim[1])

    # Future fix, set ranges


def setMarkerType(graph, sensor, pos, temperature, marker_style = False):

    size = 1
    
    # Red 22 deg C
    if temperature == "22":
        color = 2
    
    # Blue -30 deg C
    elif temperature == "-30":
        color = 4

    # Green -40 deg C
    else:
        color = 8

    if sensor == "W9-LGA35":
        marker = 20

    elif sensor == "W4-S203":
        marker = 21

    elif sensor == "W4-S215":
        marker = 22
        
        if pos == "3_0":
            size = 1.2
        
        elif pos == "3_1":
             size = 1.4
        
        elif pos == "3_2":
             size = 1.6

        elif pos == "3_3":
             size = 1.8

    elif sensor == "50D-GBGR2":
        marker = 23

    elif sensor == "W4-LG07":
        marker = 24

    elif sensor == "W4-LG12":
        marker = 25

    elif sensor == "W4-S1061":
        marker = 26

    elif sensor == "W4-S1022":
        marker = 27

    elif sensor == "W4-S204_6e14":
        marker = 28
        if pos == "7_0":
            size = 1.2
        
        elif pos == "7_2":
            size = 1.4
        
        elif pos == "7_3":
            size = 1.8


    elif sensor == "W4-RD01":
        marker = 29
        if pos == "7_0":
            size = 1.2
        
        elif pos == "7_2":
            size = 1.4


    if marker_style:
        graph.SetMarkerColor(1)
    else:
        graph.SetMarkerColor(color)

    graph.SetMarkerStyle(marker)
    graph.SetMarkerSize(size)


