import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm
import pulse_calculations as p_calc

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform():

    batchNumber = 701
    sensor = "W4-S204_6e14"
    N = 4
    
    runNumber = md.getRunNumberForBatch(batchNumber)
    md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
    dm.checkIfRepositoryOnStau()
    chan = md.getChannelNameForSensor(sensor)

    dataPath = dm.getDataPath()
    
    # Import properties to be studied
    rise_time_import = dm.importPulseFile("rise_time")
    peak_value_import = dm.importPulseFile("peak_value")
    peak_time_import = dm.importPulseFile("peak_time")
    pedestal = dm.importNoiseFile("pedestal")
    noise = dm.importNoiseFile("noise")
    

    # Randomly select event based on a property and import it
    selected_event =  np.argwhere((rise_time_import[chan] > 0) & (rise_time_import[chan] < 70)).flatten()
    np.random.shuffle(selected_event)
    event = selected_event[0]
    data_import = rnm.root2array(dataPath, start=event, stop=event+1)
    
    data = data_import[chan][0]
    pedestal = pedestal[chan]
    noise = noise[chan]
    
    data = -data
    pedestal = -pedestal

    # Set linear fit
    timeScope = 0.1
    threshold = N * noise + pedestal
    
    rise_time, cfd05, linear_fit, linear_fit_indices = p_calc.calculateRiseTime(data, pedestal, noise)
    peak_value, peak_time, poly_fit = p_calc.calculatePeakValue(data, pedestal)

    # Create TMultigraph and define underlying graphs

    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    legend = ROOT.TLegend(0.55, 0.9, 0.9, 0.7)


    graph_waveform = ROOT.TGraph(1002)
    graph_threshold = ROOT.TGraph(2)
    graph_linear_fit = ROOT.TGraph(2)
    graph_first_index = ROOT.TGraph(2)
    graph_last_index = ROOT.TGraph(2)
    graph_peak_value = ROOT.TGraph(2)
#    graph_2nd_deg_fit = ROOT.TGraph(point_difference*2+1)
    graph_2nd_deg_fit = ROOT.TGraph(2+1)
    # Define points for all selected values
    i = 0
    
    for index in range(0, len(data)):
        
        graph_waveform.SetPoint(i,i*0.1, data[index]*-1000)
        i+=1
        
    i = 0
    
    # Plot based on 5 points
    point_difference = 2
    first_index = np.argmax(data) - point_difference
    last_index = np.argmax(data) + point_difference
    
    poly_fit_range = np.arange(first_index, last_index+1)
    for index in range(0, len(poly_fit_range)):
        time = index*0.1
        value = poly_fit[0] * np.power(time, 2) + poly_fit[1] * time + poly_fit[2] + pedestal
        graph_2nd_deg_fit.SetPoint(i, time, value*-1000)
        i+=1

    graph_linear_fit.SetPoint(0, first_index*timeScope, (linear_fit[0]*first_index*timeScope + linear_fit[1])*-1000)
    graph_linear_fit.SetPoint(1, last_index*timeScope, (linear_fit[0]*last_index*timeScope + linear_fit[1])*-1000)

    graph_threshold.SetPoint(0,0, threshold*0.9*-1000)
    graph_threshold.SetPoint(1,1002, threshold*0.9*-1000)

    graph_first_index.SetPoint(0,0, np.amin(data)*0.1*-1000)
    graph_first_index.SetPoint(1,1002, np.amin(data)*0.1*-1000)

    # Define line and marker attributes

    graph_waveform.SetLineWidth(2)
    graph_waveform.SetMarkerStyle(6)

    graph_waveform.SetLineColor(2)
    graph_linear_fit.SetLineColor(3)
    graph_2nd_deg_fit.SetLineColor(4)
    graph_peak_value.SetLineColor(6)
    graph_first_index.SetLineColor(7)
    graph_last_index.SetLineColor(7)

    graph_linear_fit.SetMarkerColorAlpha(1, 0.0)
    graph_2nd_deg_fit.SetMarkerColorAlpha(1, 0.0)
    graph_2nd_deg_fit.SetMarkerColorAlpha(1, 0.0)


    # Add the graphs to multigraph
    multi_graph.Add(graph_threshold)
    multi_graph.Add(graph_waveform)
#    multi_graph.Add(graph_2nd_deg_fit)
#    multi_graph.Add(graph_linear_fit)
#    multi_graph.Add(graph_peak_value)
    multi_graph.Add(graph_first_index)
#    multi_graph.Add(graph_last_index)


    # Add the information to a legend box
    #legend.AddEntry(graph_threshold, "Noise: "+str(noise[0]*1000)[:3]+" mV", "l")
    legend.AddEntry(graph_threshold, "Threshold: "+str(threshold[0]*-1000)[:5]+" mV", "l")
    legend.AddEntry(graph_linear_fit, "Rise time: "+str(rise_time[0])[:5]+" ns", "l")
    legend.AddEntry(graph_peak_value, "Peak value: "+str(peak_value[0]*-1000)[:5]+" mV", "l")
    legend.AddEntry(graph_waveform, "Number of points: "+str(point_count_import[chan][event]), "l")
    legend.AddEntry(graph_first_index, "10 % of data max: "+str((np.amin(data)+pedestal)[0]*0.1*-1000)[0:3] + " mV", "l")

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
    multi_graph.GetYaxis().SetRangeUser(-30,400)
    #multi_graph.GetXaxis().SetRangeUser(peak_time_import[chan][event]-5,peak_time_import[chan][event]+5)
    multi_graph.GetXaxis().SetRangeUser(0,100)

    # Export the PDF file
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/waveforms/waveform"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(event)+"_"+str(sensor)+".pdf"
    canvas.Print(fileName)



# Group each consequential numbers in each separate list
def group_consecutives(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

i = 0
while i < 20:
    i+=1

    printWaveform()
