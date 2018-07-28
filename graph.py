import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm
import pulse_calculations as p_calc

ROOT.gROOT.SetBatch(True)

batch = 108
sensor = ""
event = 0

# Start analysis of selected run numbers
def printWaveform(batchNumber, sensor, event=0):

#    batchNumber = 301
#    sensor = "W4-S203"
    N = 4
    
    runNumber = md.getRunNumberForBatch(batchNumber)
    md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
    dm.defineDataFolderPath()
    chan = md.getChannelNameForSensor(sensor)
    
    

    dataPath = dm.getDataPath()
    
    # Import properties to be studied
    rise_time_import = dm.importPulseFile("rise_time")
    peak_value_import = dm.importPulseFile("peak_value")
    peak_time_import = dm.importPulseFile("peak_time")
    pedestal = dm.importNoiseFile("pedestal")
    noise = dm.importNoiseFile("noise")
    points_import = dm.importPulseFile("points")
    

    # Randomly select event based on a property and import it
    if event == 0:
        selected_event =  np.argwhere(rise_time_import[chan]).flatten()
        np.random.shuffle(selected_event)
        event = selected_event[0]
    
        
    data_import = rnm.root2array(dataPath, start=event, stop=event+1)
    
    data = data_import[chan][0]
    pedestal = pedestal[chan]
    noise = noise[chan]

    data = -data
    pedestal = -pedestal

    # Set linear fit
    timeScope = p_calc.defTimeScope()
    threshold = N * noise + pedestal

    
    # Define point difference for 2nd degree fit
    point_difference = 2
    
    rise_time, cfd05, linear_fit, linear_fit_indices = p_calc.calculateRiseTime(data, pedestal, noise, True)
    peak_value, peak_time, poly_fit = p_calc.calculatePeakValue(data, pedestal, noise, 350, True)
    point_count = p_calc.calculatePoints(data, threshold)
    
    noise_event = np.std(data[0:int(cfd05)*10-10])

    # Create TMultigraph and define underlying graphs

    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    legend = ROOT.TLegend(0.55, 0.9, 0.9, 0.7)


    graph_waveform = ROOT.TGraph(1002)
    graph_threshold = ROOT.TGraph(2)
    graph_peak_value = ROOT.TGraph(2)
    graph_cfd05 = ROOT.TGraph(2)
    graph_10 = ROOT.TGraph(2)
    graph_90 = ROOT.TGraph(2)
    graph_pedestal = ROOT.TGraph(2)
    
    histogram_std = ROOT.TH1D("h1", "h1", 200, -20, 20)
    
    graph_linear_fit = ROOT.TGraph(len(linear_fit_indices))
    graph_2nd_deg_fit = ROOT.TGraph(point_difference*2+1)
    # Define points for all selected values
    
    i = 0
    for index in range(0, len(data)):
        
        graph_waveform.SetPoint(i,i*0.1, data[index]*1000)
        i+=1
        histogram_std.Fill(data[index]*1000)
        
    i = 0
    # Plot based on 5 points
    first_index = np.argmax(data) - point_difference
    last_index = np.argmax(data) + point_difference
    
    poly_fit_range = np.arange(first_index, last_index+1)
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
    
    graph_cfd05.SetPoint(0,cfd05, -30)
    graph_cfd05.SetPoint(1,cfd05, 500)
    
    graph_pedestal.SetPoint(0,0, pedestal)
    graph_pedestal.SetPoint(1,1002, pedestal)
    
    graph_10.SetPoint(0,0, peak_value*0.1*1000)
    graph_10.SetPoint(1,1002, peak_value*0.1*1000)
    graph_90.SetPoint(0,0, peak_value*0.9*1000)
    graph_90.SetPoint(1,1002, peak_value*0.9*1000)
    
    # Define line and marker attributes

    graph_waveform.SetLineWidth(2)
    graph_waveform.SetMarkerStyle(6)

    graph_waveform.SetLineColor(2)
    graph_linear_fit.SetLineColor(3)
    graph_2nd_deg_fit.SetLineColor(4)
    graph_peak_value.SetLineColor(6)
    graph_10.SetLineColor(7)
    graph_90.SetLineColor(7)
    graph_linear_fit.SetMarkerColorAlpha(1, 0.0)
    graph_2nd_deg_fit.SetMarkerColorAlpha(1, 0.0)
    graph_2nd_deg_fit.SetMarkerColorAlpha(1, 0.0)
    graph_pedestal.SetLineColor(9)


    # Add the graphs to multigraph
    multi_graph.Add(graph_waveform)
    multi_graph.Add(graph_threshold)
    multi_graph.Add(graph_2nd_deg_fit)
    multi_graph.Add(graph_linear_fit)
    #multi_graph.Add(graph_peak_value)
    #multi_graph.Add(graph_10)
    #multi_graph.Add(graph_90)
    #multi_graph.Add(graph_cfd05)
    multi_graph.Add(graph_pedestal)

    
    # Add the information to a legend box
    #legend.AddEntry(graph_threshold, "Noise: "+str(noise[0]*1000)[:3]+" mV", "l")
    legend.AddEntry(graph_threshold, "Threshold: "+str(threshold[0]*1000)[:5]+" mV", "l")
    legend.AddEntry(graph_waveform, "Noise event: "+str(noise_event*1000)[:3]+" mV", "l")
    legend.AddEntry(graph_pedestal, "Pedestal: "+str(pedestal[0]*1000)[:3]+" mV", "l")
   # legend.AddEntry(graph_waveform, "Points above threshold: "+str(point_count), "l")
    legend.AddEntry(graph_linear_fit, "Rise time: "+str(rise_time[0]*1000)[:5]+" ps", "l")
    #legend.AddEntry(graph_peak_value, "Peak value: "+str(peak_value_import[chan][event]*-1000)[:5]+" mV", "l")
    #legend.AddEntry(graph_90, "10% and 90% limit", "l")
    #legend.AddEntry(graph_cfd05, "cfd05 " + str(cfd05[0])[0:4] + " ns", "l")

    #legend.AddEntry(graph_cfd05, "Point count above 10% " + str(point_count), "l")

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
    multi_graph.GetYaxis().SetRangeUser(-30,300)
    multi_graph.GetXaxis().SetRangeUser(cfd05-3,cfd05+5)
    #multi_graph.GetXaxis().SetRangeUser(0,100)

    # Export the PDF file
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/waveforms/waveform"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(event)+"_"+str(sensor)+".pdf"

    canvas.Print(fileName)

    canvas.Clear()

    histogram_std.Draw()
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/waveforms/histogram"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(event)+"_"+str(sensor)+".pdf"

    #canvas.Print(fileName)



# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)


def mainPrint():

    i = 0
    while i < 20:
        i+=1
        printWaveform(batch, sensor)

mainPrint()
