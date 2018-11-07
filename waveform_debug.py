### This is a debugging function aimed to analyze waveforms and check the functions if they are working properly ###
# Can be run by
# python graph.py

# This can be run when the pulseAnalysis() for the given run/batch is done.
# The oscilloscope file is required to run this file.


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
event = 151999
number_of_plots = 3

# Print selected event for sensor and batch
def printWaveform(batchNumber, sensor, event = 0):

    # Factor N used in pulse_calculations.py
    N = 4.27
    
    # Define
    runNumber = md.getAllRunNumbers(batchNumber)[0]
    md.defineRunInfo(md.getRowForRunNumber(runNumber))
    dm.defineDataFolderPath()
    chan = md.getChannelNameForSensor(sensor)
    md.setChannelName(chan)
    dataPath = dm.getOscilloscopeFilePath()
    
    # Import properties to be studied
    rise_time_import = dm.exportImportROOTData("pulse", "rise_time")
    peak_value_import = dm.exportImportROOTData("pulse", "pulse_amplitude")
    max_sample = dm.exportImportROOTData("pulse", "max_sample")
    peak_time_import = dm.exportImportROOTData("pulse", "peak_time")
    points_import = dm.exportImportROOTData("pulse", "points")
    charge_import = dm.exportImportROOTData("pulse", "charge")

    # Randomly select event based on a property and import it
    if event == 0:
    
        # Here one can modify the condition which randomly selects an event. Event number must be 0
        condition = charge_import[chan] > 10 * 10**-15
        selected_event =  np.argwhere(condition).flatten()
        np.random.shuffle(selected_event)
        event = selected_event[0]
        
    data_import = rnm.root2array(dataPath, start=event, stop=event+1)
    
    data = data_import[chan][0]
    data = -data
    
    # Set linear fit
    timeScope = 0.1
    noise, pedestal = p_calc.calculateNoiseAndPedestal(data)
    threshold = N * noise + pedestal

    
    # Define point difference for 2nd degree fit
    signal_limit_DUT = 0.3547959
    point_difference = 2
    
    peak_value, peak_time, poly_fit = p_calc.calculatePeakValue(data, pedestal, signal_limit_DUT, True)
    rise_time, cfd, linear_fit, linear_fit_indices = p_calc.calculateRiseTime(data, pedestal, True)
    charge = p_calc.calculateCharge(data, pedestal)
    point_count = p_calc.calculatePoints(data, threshold)
    max_sample = np.amax(data) - pedestal

    # Create TMultigraph and define underlying graphs

    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    legend = ROOT.TLegend(0.65, 0.9, 0.9, 0.6)


    graph_waveform = ROOT.TGraph(1002)
    graph_threshold = ROOT.TGraph(2)
    graph_peak_value = ROOT.TGraph(2)
    graph_max_sample = ROOT.TGraph(2)
    graph_cfd = ROOT.TGraph(2)
    graph_peak_time = ROOT.TGraph(2)
    graph_10 = ROOT.TGraph(2)
    graph_90 = ROOT.TGraph(2)
    graph_pedestal = ROOT.TGraph(2)
    graph_noise = ROOT.TGraph(2)
    graph_linear_fit = ROOT.TGraph(len(linear_fit_indices))
    graph_2nd_deg_fit = ROOT.TGraph(point_difference*2+1)

    # Define points for all selected values
    
    # Fill shade between threshold and waveform
    # This one is adapted for Batch 102, W9-LGA35, event 151999
    n = np.sum((data > pedestal) & (np.nonzero(data)[0] > 431) & (np.nonzero(data)[0] < 452))+1
    charge_fill = ROOT.TGraph(2*n)
    fillOnce = True

    for index in range(0, len(data)):
        
        graph_waveform.SetPoint(index, index*0.1, data[index]*1000)
  
        if index > 431 and fillOnce:
            
            for i in range(0, n):

                charge_fill.SetPoint(i,   0.1 * (i+index),     data[i+index] * 1000)
                charge_fill.SetPoint(n+i, 0.1 * (n-i+index-1), pedestal * 1000)
            
            fillOnce = False

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

    # Set points to draw lines
    graph_threshold.SetPoint(0,0, threshold*1000)
    graph_threshold.SetPoint(1,1002, threshold*1000)

    graph_noise.SetPoint(0,0, noise*1000)
    graph_noise.SetPoint(1,1002, noise*1000)

    graph_pedestal.SetPoint(0,0, pedestal*1000)
    graph_pedestal.SetPoint(1,1002, pedestal*1000)
    
    graph_peak_value.SetPoint(0,0, peak_value*1000)
    graph_peak_value.SetPoint(1,1002, peak_value*1000)
    
    graph_max_sample.SetPoint(0,0, max_sample*1000)
    graph_max_sample.SetPoint(1,1002, max_sample*1000)
    
    graph_cfd.SetPoint(0, cfd, -30)
    graph_cfd.SetPoint(1, cfd, 500)

    graph_peak_time.SetPoint(0, peak_time, -30)
    graph_peak_time.SetPoint(1, peak_time, 500)

    
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
    graph_cfd.SetLineStyle(7)

    
    graph_2nd_deg_fit.SetLineColor(3)
    graph_peak_value.SetLineColor(4)
    graph_linear_fit.SetLineColor(1)
    graph_cfd.SetLineColor(8)
    graph_peak_time.SetLineColor(8)
    graph_pedestal.SetLineColor(6)
    graph_noise.SetLineColor(7)
    graph_threshold.SetLineColor(1)

    graph_max_sample.SetLineColor(2)

    graph_10.SetLineColor(7)
    graph_90.SetLineColor(7)

    graph_linear_fit.SetMarkerColorAlpha(1, 0.0)
    graph_2nd_deg_fit.SetMarkerColorAlpha(1, 0.0)

    charge_fill.SetFillStyle(3013)
    charge_fill.SetFillColor(4)
    


    # Add the graphs to multigraph
    multi_graph.Add(graph_waveform)
    multi_graph.Add(graph_noise)
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
    legend.AddEntry(graph_waveform, "Waveform " + md.getSensor(), "l")
    legend.AddEntry(graph_noise, "Noise: "+str(noise*1000)[:4]+" mV", "l")
    legend.AddEntry(graph_pedestal, "Pedestal: "+str(pedestal*1000)[:4]+" mV", "l")
    legend.AddEntry(graph_threshold, "Threshold: "+str(threshold*1000)[:5]+" mV", "l")
    #legend.AddEntry(graph_max_sample, "Max sample: "+str(max_sample*1000)[:5]+" mV", "l")
    #legend.AddEntry(graph_waveform, "Points above threshold: "+str(point_count), "l")
    legend.AddEntry(graph_peak_value, "Pulse amplitude: "+str(peak_value[0]*1000)[:5]+" mV", "l")
    legend.AddEntry(graph_peak_time, "Time at peak: " + str(peak_time[0])[0:4] + " ns", "l")
    legend.AddEntry(graph_linear_fit, "Rise time: "+str(rise_time*1000)[:5]+" ps", "l")
    #legend.AddEntry(graph_90, "10% and 90% limit", "l")
    legend.AddEntry(graph_cfd, "CFD0.5: " + str(cfd)[0:4] + " ns", "l")
    legend.AddEntry(charge_fill, "Charge: "+str(charge*10**15)[:5]+" fC", "f")



    # Define the titles and draw the graph

    xAxisTitle = "Time [ns]"
    yAxisTitle = "Voltage [mV]"
    headTitle = "Waveform " + md.getSensor()
    multi_graph.Draw("ALP")
    legend.Draw()
    multi_graph.SetTitle(headTitle)
    multi_graph.GetXaxis().SetTitle(xAxisTitle)
    multi_graph.GetYaxis().SetTitle(yAxisTitle)

    # Set ranges on axis
    multi_graph.GetYaxis().SetRangeUser(-30,350)
    multi_graph.GetXaxis().SetRangeUser(cfd-1,cfd+2.5) # This centers the canvas around the cfd time location point
    #multi_graph.GetXaxis().SetRangeUser(0,100)


    # Export the PDF file
    fileName = dm.getPlotsSourceFolder()+"/waveforms/waveform"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(event)+"_"+str(sensor)+".pdf"

    canvas.Print(fileName)

    print "PDF Produced at", fileName+"."


# Print the graph 'number_of_plots' times
def mainPrint():

    
    if event == 0:
        i = 0
        while i < number_of_plots:
            i+=1
            printWaveform(batch, sensor, event)

    else:
        printWaveform(batch, sensor, event)

mainPrint()
