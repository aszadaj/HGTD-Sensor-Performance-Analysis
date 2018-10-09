import ROOT
import root_numpy as rnm
import os

import results_calculations as r_calc
import results_plot as r_plot
import run_log_metadata as md
import data_management as dm

def produceResults():

    global canvas
    global oneSensorInLegend
    global processed_sensor
    global bias_voltage_max

    bias_voltage_max = 350
    
    categories = ["noise", "pedestal", "peak_value", "charge", "rise_time", "linear", "system", "linear_cfd", "system_cfd", "linear_gain", "system_gain", "linear_cfd_gain", "system_cfd_gain"]
    #categories = ["linear_gain", "system_gain", "linear_cfd_gain", "system_cfd_gain"]
    
    canvas = ROOT.TCanvas("Results", "Results")
    dm.defineDataFolderPath()
    
    sensorNames = md.getAllSensorNames()
    
    if md.sensor != "":
        sensorNames = [md.sensor]

    resultsDict = dict()
    resultGraphs = dict()
    legend = dict()

    print "\nStart RESULTS"

    # loop through each category
    for category in categories:
    
        print "\n", category, "\n"
    
        category_graph = ROOT.TMultiGraph()
        legend_graph = ROOT.TLegend(0.7, 0.9, 0.9, 0.6)
        
        graph = dict()
        
        for processed_sensor in sensorNames:
            
            print processed_sensor
        
            graph[processed_sensor] = dict()
            sensor_data = dict()
            
            # Create TGraphErrors for each sensor, temperature and position (in the case of array pads)
            for temperature in md.getAvailableTemperatures():
                
                graph[processed_sensor][temperature] = dict()
                sensor_data[temperature] = dict()
                
                # availableDUTPositions(processed_sensor) consider only one pad so far.
                
                for DUT_pos in md.availableDUTPositions(processed_sensor):
                    graph[processed_sensor][temperature][DUT_pos] = ROOT.TGraphErrors()
                    sensor_data[temperature][DUT_pos] = []
                    
                    # Change each marker type and color
                    r_plot.setMarkerType(graph[processed_sensor][temperature][DUT_pos], DUT_pos, temperature)
        
        
            r_calc.importResultsValues(sensor_data, category)
            
            
            r_plot.addValuesToGraph([sensor_data, category, legend_graph, graph, category_graph])
    
            

        r_plot.drawAndExportResults(category, category_graph, legend_graph)

