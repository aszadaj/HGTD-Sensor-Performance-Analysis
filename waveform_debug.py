#
#   WAVEFORM DEBUG
#
# This is a debugging function aimed to draw the waveform of a selected event with calculated pulse characteristics.
# It plots the event for a chosen run with lines marking the different characteristics.

#   How to use:
#
# 0. Make sure that the oscilloscope file exists for chosen run
# 1. Define the run, sensor and event. The point is to select one which has a signal from a MIP.
# 2. Run the code by
#
# $ python2 graph.py
#
# The exported graph is then at
#
#   ../folder_sensor_perfomance_tb_sep17/plots_sensors/waveforms/
#


import ROOT
import numpy as np
import root_numpy as rnm

import run_log_metadata as md
import data_management as dm
import pulse_calculations as p_calc

ROOT.gROOT.SetBatch(True)

# Define batch, sensor and event number
runNumber = 3650
sensor = "W9-LGA35"
event = 84866


# Print selected event for sensor and batch
def printWaveform(runNumber, sensor, event = 0):
    
    # Define global variables
    md.defineRunInfo(md.getRowForRunNumber(runNumber))
    dm.defineDataFolderPath()
    chan = md.getChannelNameForSensor(sensor)
    md.setChannelName(chan)
    
    # Create TMultigraph and define underlying graphs
    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    legend = ROOT.TLegend(0.65, 0.9, 0.9, 0.6)

    # Import the event from the oscilloscope file
    data_import = dm.getOscilloscopeData(event, event+1)
    data = -data_import[chan][0]
    
    # Set find noise and pedestal and define the threshold of finding signals
    timeScope = 0.1
    N = 4.27
    noise, pedestal = p_calc.calculateNoiseAndPedestal(data)
    threshold = N * noise + pedestal

    # Define point difference for second degree fit and maximum signal limit (saturated signals)
    signal_limit_DUT = 0.3547959
    point_difference = 2
    
    # Calculate pulse characteristics (based on the methods from pulse_calculations.py)
    peak_value, peak_time, poly_fit = p_calc.calculatePulseAmplitude(data, pedestal, signal_limit_DUT, True)
    rise_time, cfd, linear_fit, linear_fit_indices = p_calc.calculateRiseTime(data, pedestal, True)
    charge = p_calc.calculateCharge(data, pedestal)
    point_count = p_calc.calculatePoints(data, threshold)
    max_sample = np.amax(data) - pedestal


    # Define ROOT objects for each type of graph
    graph_waveform = ROOT.TGraph(len(data))
    graph_threshold = ROOT.TGraph(2)
    graph_pulse_amplitude = ROOT.TGraph(2)
    graph_max_sample = ROOT.TGraph(2)
    graph_cfd = ROOT.TGraph(2)
    graph_peak_time = ROOT.TGraph(2)
    graph_10 = ROOT.TGraph(2)
    graph_90 = ROOT.TGraph(2)
    graph_pedestal = ROOT.TGraph(2)
    graph_noise = ROOT.TGraph(2)
    graph_linear_fit = ROOT.TGraph(len(linear_fit_indices))
    graph_2nd_deg_fit = ROOT.TGraph(point_difference*2+1)

   
    # Find points to draw the shade showing the charge
    pedestal_points = p_calc.getConsecutiveSeries(data, np.argwhere(data > pedestal).flatten())
    n = len(pedestal_points)+1
    charge_fill = ROOT.TGraph(2*n)
    fillOnce = True

    # Draw the waveform and the charge fill
    for index in range(0, len(data)):
        
        graph_waveform.SetPoint(index, index*0.1, data[index]*1000)

        if index > pedestal_points[0]-1 and fillOnce:

            for i in range(0, n):

                charge_fill.SetPoint(i,   0.1 * (i+index),     data[i+index] * 1000)
                charge_fill.SetPoint(n+i, 0.1 * (n-i+index-1), pedestal * 1000)

            fillOnce = False


    # Draw the second degree fit
    first_index = np.argmax(data) - point_difference
    last_index = np.argmax(data) + point_difference
    poly_fit_range = np.arange(first_index, last_index, 0.1)

    i = 0
    for index in range(0, len(poly_fit_range)):
        time = poly_fit_range[index]*timeScope
        value = poly_fit[0] * np.power(time, 2) + poly_fit[1] * time + poly_fit[2] + pedestal
        graph_2nd_deg_fit.SetPoint(i, time, value*1000)
        i += 1
    
    # Draw the linear fit
    i = 0
    for index in range(0, len(linear_fit_indices)):
        time = linear_fit_indices[index]*timeScope
        value = linear_fit[0]*time + linear_fit[1]
        graph_linear_fit.SetPoint(i, time, value*1000)
        i+=1

    # Draw lines (by setting two points at the beginning and the end)
    graph_threshold.SetPoint(0,0, threshold*1000)
    graph_threshold.SetPoint(1,1002, threshold*1000)

    graph_noise.SetPoint(0,0, noise*1000)
    graph_noise.SetPoint(1,1002, noise*1000)

    graph_pedestal.SetPoint(0,0, pedestal*1000)
    graph_pedestal.SetPoint(1,1002, pedestal*1000)
    
    graph_pulse_amplitude.SetPoint(0,0, peak_value*1000)
    graph_pulse_amplitude.SetPoint(1,1002, peak_value*1000)
    
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
    graph_waveform.SetMarkerStyle(6)
    graph_waveform.SetLineColor(2)

    graph_linear_fit.SetLineWidth(3)
    graph_linear_fit.SetLineColor(1)
    graph_linear_fit.SetMarkerColorAlpha(1, 0.0)
    
    graph_2nd_deg_fit.SetLineWidth(3)
    graph_2nd_deg_fit.SetLineColor(3)
    graph_2nd_deg_fit.SetMarkerColorAlpha(1, 0.0)

    graph_cfd.SetLineStyle(7)
    graph_cfd.SetLineColor(8)
   
    graph_pulse_amplitude.SetLineColor(4)

    graph_peak_time.SetLineColor(8)
    graph_pedestal.SetLineColor(6)
    graph_noise.SetLineColor(7)
    graph_threshold.SetLineColor(1)
    graph_max_sample.SetLineColor(2)
    graph_10.SetLineColor(7)
    graph_90.SetLineColor(7)
    charge_fill.SetFillStyle(3013)
    charge_fill.SetFillColor(4)
    

    # Add the graphs to multigraph
    multi_graph.Add(graph_waveform)
    multi_graph.Add(graph_noise)
    multi_graph.Add(graph_threshold)
    multi_graph.Add(graph_2nd_deg_fit)
    multi_graph.Add(graph_linear_fit)
    multi_graph.Add(graph_pulse_amplitude)
    multi_graph.Add(graph_max_sample)
    multi_graph.Add(graph_10)
    multi_graph.Add(graph_90)
    multi_graph.Add(graph_cfd)
    multi_graph.Add(graph_peak_time)
    multi_graph.Add(graph_pedestal)
    multi_graph.Add(charge_fill, "f")

    
    # Add the information to a legend box
    legend.AddEntry(graph_waveform, "Waveform " + md.getSensor(), "l")
    legend.AddEntry(graph_noise, "Noise: "+str(noise*1000)[:4]+" mV", "l")
    legend.AddEntry(graph_pedestal, "Pedestal: "+str(pedestal*1000)[:4]+" mV", "l")
    legend.AddEntry(graph_threshold, "Threshold: "+str(threshold*1000)[:5]+" mV", "l")
    legend.AddEntry(graph_max_sample, "Max sample: "+str(max_sample*1000)[:5]+" mV", "l")
    legend.AddEntry(graph_waveform, "Points above threshold: "+str(point_count), "l")
    legend.AddEntry(graph_pulse_amplitude, "Pulse amplitude: "+str(peak_value[0]*1000)[:5]+" mV", "l")
    legend.AddEntry(graph_peak_time, "Time at peak: " + str(peak_time[0])[0:5] + " ns", "l")
    legend.AddEntry(graph_linear_fit, "Rise time: "+str(rise_time*1000)[:5]+" ps", "l")
    legend.AddEntry(graph_90, "10% and 90% limit", "l")
    legend.AddEntry(graph_cfd, "CFD0.5: " + str(cfd)[0:5] + " ns", "l")
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

    # Set ranges on axes
    multi_graph.GetYaxis().SetRangeUser(-30,350)
    multi_graph.GetXaxis().SetRangeUser(cfd-5,cfd+5) # This centers the canvas around the cfd time location point
    #multi_graph.GetXaxis().SetRangeUser(0,100)


    # Export the PDF file
    fileName = dm.getPlotsSourceFolder()+"/waveforms/waveform"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(event)+"_"+str(sensor)+".pdf"

    canvas.Print(fileName)

    print "PDF Produced at", fileName+"."



printWaveform(batch, sensor, event)
