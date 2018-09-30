### This is a debugging function aimed to analyze waveforms ###
# It can be run when the files for the given run/batch are produced!


import ROOT
import numpy as np
import root_numpy as rnm

import run_log_metadata as md
import data_management as dm
import pulse_calculations as p_calc

ROOT.gROOT.SetBatch(True)

batch = 102
sensor = "W9-LGA35"

# If event = 0, then the event number will be randomly selected based on condition
event = 0
number_of_plots = 3

# Print selected event for sensor and batch
def printWaveform(batchNumber, sensor, event = 0):

    # Factor N used in pulse_calculations.py
    N = 4.27
    
    runNumber = md.getAllRunNumbers(batchNumber)[0]
    md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
    dm.defineDataFolderPath()
    md.defTimeScope()
    chan = md.getChannelNameForSensor(sensor)
    md.setChannelName(chan)
    dataPath = dm.getOscilloscopeFilePath()
    
    # Import properties to be studied
    rise_time_import = dm.exportImportROOTData("pulse", "rise_time")
    peak_value_import = dm.exportImportROOTData("pulse", "peak_value")
    max_sample = dm.exportImportROOTData("pulse", "max_sample")
    peak_time_import = dm.exportImportROOTData("pulse", "peak_time")
    pedestal_import = dm.exportImportROOTData("results", "pedestal")
    noise_import = dm.exportImportROOTData("results", "noise")
    points_import = dm.exportImportROOTData("pulse", "points")
    charge_import = dm.exportImportROOTData("pulse", "charge")

    # Randomly select event based on a property and import it
    if event == 0:
    
        # Here one can modify the condition which randomly selects an event. Event number must be 0
        condition = peak_value_import[chan] < -0.05
        selected_event =  np.argwhere(condition).flatten()
        np.random.shuffle(selected_event)
        event = selected_event[0]
        
    data_import = rnm.root2array(dataPath, start=event, stop=event+1)
    
    data = data_import[chan][0]
    data = -data
    
    
    

    # Set linear fit
    timeScope = md.getTimeScope()
    noise, pedestal = p_calc.calculateNoiseAndPedestal(data)
    threshold = N * noise + pedestal

    
    # Define point difference for 2nd degree fit
    signal_limit_DUT = 0.3547959327697754
    point_difference = 2
    
    rise_time, cfd, linear_fit, linear_fit_indices = p_calc.calculateRiseTime(data, pedestal, True)
    peak_value, peak_time, poly_fit = p_calc.calculatePeakValue(data, pedestal, signal_limit_DUT, True)
    point_count = p_calc.calculatePoints(data, threshold)
    charge = p_calc.calculateCharge(data, threshold)
    max_sample = np.amax(data) - pedestal

    # Create TMultigraph and define underlying graphs

    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    legend = ROOT.TLegend(0.55, 0.9, 0.9, 0.7)


    graph_waveform = ROOT.TGraph(1002)
    graph_threshold = ROOT.TGraph(2)
    graph_peak_value = ROOT.TGraph(2)
    graph_max_sample = ROOT.TGraph(2)
    graph_cfd = ROOT.TGraph(2)
    graph_peak_time = ROOT.TGraph(2)
    graph_10 = ROOT.TGraph(2)
    graph_90 = ROOT.TGraph(2)
    graph_pedestal = ROOT.TGraph(2)
    graph_linear_fit = ROOT.TGraph(len(linear_fit_indices))
    graph_2nd_deg_fit = ROOT.TGraph(point_difference*2+1)

    # Define points for all selected values
    
    # Fill shade between threshold and waveform

    n = np.sum((data > threshold)) - 1
    charge_fill = ROOT.TGraph(2*n)

    i = 0
    j = 0
    for index in range(0, len(data)):
        graph_waveform.SetPoint(i,index*0.1, data[index]*1000)
        
#        # This is done once
#        if data[index] > threshold and (400 < index < 450):
#            charge_fill.SetPoint(j, index*0.1, data[index]*1000)
#            charge_fill.SetPoint(n+j, (index+n-j)*0.1, data[index+n-j]*1000)
#            j+=1

        i+=1
        

    # Plot based on 5 points
    first_index = np.argmax(data) - point_difference
    last_index = np.argmax(data) + point_difference
    
    poly_fit_range = np.arange(first_index, last_index, 0.1)

    i = 0
    for index in range(0, len(poly_fit_range)):
        time = poly_fit_range[index]*timeScope
        value = poly_fit[0] * np.power(time, 2) + poly_fit[1] * time + poly_fit[2] + pedestal
        graph_2nd_deg_fit.SetPoint(i, time, value*1000)
        i += 1
    
    i = 0
    for index in range(0, len(linear_fit_indices)):
        time = linear_fit_indices[index]*timeScope
        value = linear_fit[0]*time + linear_fit[1]
        graph_linear_fit.SetPoint(i, time, value*1000)
        i+=1

    graph_threshold.SetPoint(0,0, threshold*1000)
    graph_threshold.SetPoint(1,1002, threshold*1000)
    
    graph_peak_value.SetPoint(0,0, peak_value*1000)
    graph_peak_value.SetPoint(1,1002, peak_value*1000)
    
    graph_max_sample.SetPoint(0,0, max_sample*1000)
    graph_max_sample.SetPoint(1,1002, max_sample*1000)
    
    graph_cfd.SetPoint(0, cfd, -30)
    graph_cfd.SetPoint(1, cfd, 500)

    graph_peak_time.SetPoint(0, peak_time, -30)
    graph_peak_time.SetPoint(1, peak_time, 500)
    
    graph_pedestal.SetPoint(0,0, pedestal)
    graph_pedestal.SetPoint(1,1002, pedestal)
    
    graph_10.SetPoint(0,0, peak_value*0.1*1000)
    graph_10.SetPoint(1,1002, peak_value*0.1*1000)
    graph_90.SetPoint(0,0, peak_value*0.9*1000)
    graph_90.SetPoint(1,1002, peak_value*0.9*1000)
    
    # Define line and marker attributes

    graph_waveform.SetLineWidth(2)
    graph_linear_fit.SetLineWidth(3)
    graph_2nd_deg_fit.SetLineWidth(3)
    graph_waveform.SetMarkerStyle(6)
    graph_waveform.SetLineColor(2)

    
    graph_2nd_deg_fit.SetLineColor(4)
    graph_peak_value.SetLineColor(4)
    graph_linear_fit.SetLineColor(1)
    graph_cfd.SetLineColor(8)
    graph_peak_time.SetLineColor(8)
    graph_pedestal.SetLineColor(6)
    graph_threshold.SetLineColor(1)

    graph_max_sample.SetLineColor(2)

    graph_10.SetLineColor(7)
    graph_90.SetLineColor(7)

    graph_linear_fit.SetMarkerColorAlpha(1, 0.0)
    graph_2nd_deg_fit.SetMarkerColorAlpha(1, 0.0)
    
    # Fill
    charge_fill.SetFillStyle(3013)
    charge_fill.SetFillColor(4)
    


    # Add the graphs to multigraph
    multi_graph.Add(graph_waveform)
    multi_graph.Add(graph_threshold)
    multi_graph.Add(graph_2nd_deg_fit)
    multi_graph.Add(graph_linear_fit)
    multi_graph.Add(graph_peak_value)
    #multi_graph.Add(graph_max_sample)
    #multi_graph.Add(graph_10)
    #multi_graph.Add(graph_90)
    multi_graph.Add(graph_cfd)
    multi_graph.Add(graph_peak_time)
    multi_graph.Add(graph_pedestal)
    #multi_graph.Add(charge_fill, "f")

    
    # Add the information to a legend box
    legend.AddEntry(graph_waveform, "Waveform " + md.getNameOfSensor(chan), "l")
    legend.AddEntry(graph_peak_value, "Peak value: "+str(peak_value*1000)[:5]+" mV", "l")
    legend.AddEntry(graph_linear_fit, "Rise time: "+str(rise_time*1000)[:5]+" ps", "l")
    legend.AddEntry(graph_cfd, "CFD " + str(cfd)[0:4] + " ns", "l")
    legend.AddEntry(graph_peak_time, "Peak time " + str(peak_time[0])[0:4] + " ns", "l")
    legend.AddEntry(graph_pedestal, "Pedestal: "+str(pedestal*1000)[:4]+" mV", "l")
    legend.AddEntry(graph_threshold, "Noise: "+str(noise*1000)[:4]+" mV", "l")
    legend.AddEntry(graph_threshold, "Threshold: "+str(threshold*1000)[:5]+" mV", "l")
    legend.AddEntry(charge_fill, "Charge: "+str(charge*10**15)[:5]+" fC", "l")
    legend.AddEntry(graph_max_sample, "Max sample: "+str(max_sample*1000)[:5]+" mV", "l")
    legend.AddEntry(graph_waveform, "Points above threshold: "+str(point_count), "l")
    #legend.AddEntry(graph_90, "10% and 90% limit", "l")


    # Define the titles and draw the graph

    xAxisTitle = "Time [ns]"
    yAxisTitle = "Voltage [mV]"
    headTitle = "Waveform " + md.getNameOfSensor(chan)
    multi_graph.Draw("ALP")
    legend.Draw()
    multi_graph.SetTitle(headTitle)
    multi_graph.GetXaxis().SetTitle(xAxisTitle)
    multi_graph.GetYaxis().SetTitle(yAxisTitle)

    # Set ranges on axis
    multi_graph.GetYaxis().SetRangeUser(-30,450)
    #multi_graph.GetXaxis().SetRangeUser(cfd-3,cfd+5)
    multi_graph.GetXaxis().SetRangeUser(0,100)

    # Export the PDF file
    fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder()+"/waveforms/waveform"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(event)+"_"+str(sensor)+".pdf"

    canvas.Print(fileName)




def mainPrint():

    
    if event == 0:
        i = 0
        while i < number_of_plots:
            i+=1
            printWaveform(batch, sensor, event)

    else:
        printWaveform(batch, sensor, event)

mainPrint()
