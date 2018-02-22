import ROOT
import numpy as np
import root_numpy as rnm
import metadata as md
import data_management as dm

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform(runNumber, event, peak_time_LGAD, peak_time_SiPM, peak_value, channel, ifSmallPeak):

    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
  
    if dm.isOnHDD():
    
        dataPath = "/Volumes/HDD500/" + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    data = rnm.root2array(dataPath, start=event, stop=event+1)
    
    peak_fit = dm.importPulseFile("peak_fit")
    
    channels = data.dtype.names

    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    legend = ROOT.TLegend(0.65, 0.9, 0.9, 0.7)
    
    graph_waveform = dict()
    graph_vertical = dict()
    graph_peak_fit = dict()
    
    timeScope = 0.1
    
    if channel != "":
        channels = [channel, md.getChannelNameForSensor("SiPM-AFP")]

    for chan in channels:
    

        peak_fit_indices = np.arange(np.argmin(data[chan][0])-4, np.argmin(data[chan][0])+4, 0.05)
        
        
        graph_waveform[chan] = ROOT.TGraph(1002)
        graph_vertical[chan] = ROOT.TGraph(2)
        graph_peak_fit[chan] = ROOT.TGraph(len(peak_fit_indices))
        
        i = 0
        
        for index in range(0, len(data[chan][0])):
            
            graph_waveform[chan].SetPoint(i,i*timeScope, data[chan][0][index]*-1000)
            i+=1
        

        i = 0

        for index in range(0, len(peak_fit_indices)):
        
            t = peak_fit_indices[index]*timeScope
            value = (peak_fit[chan][event][0][0]*np.power(t,2)+peak_fit[chan][event][0][1]*t+peak_fit[chan][event][0][2])*-1000
            
            graph_peak_fit[chan].SetPoint(i, t, value)
            i+=1

        if chan == md.getChannelNameForSensor("SiPM-AFP"):
        
            graph_vertical[chan].SetPoint(0,peak_time_SiPM,-30)
            graph_vertical[chan].SetPoint(1,peak_time_SiPM,500)
            
            graph_waveform[chan].SetLineColor(2)
            graph_vertical[chan].SetLineColor(4)
            
            legend.AddEntry(graph_vertical[chan], "SiPM time location: "+str(peak_time_SiPM)[0:5], "l")

        else:
        
            graph_vertical[chan].SetPoint(0,peak_time_LGAD,-30)
            graph_vertical[chan].SetPoint(1,peak_time_LGAD,500)
            
            graph_waveform[chan].SetLineColor(6)
            graph_vertical[chan].SetLineColor(7)
            
            legend.AddEntry(graph_vertical[chan], md.getNameOfSensor(chan)+" time location: "+str(peak_time_LGAD)[0:6], "l")


        graph_peak_fit[chan].SetLineColorAlpha(3, 0.9)
        graph_peak_fit[chan].SetMarkerColorAlpha(3, 0.01)

        multi_graph.Add(graph_waveform[chan])
        multi_graph.Add(graph_vertical[chan])
        multi_graph.Add(graph_peak_fit[chan])


        legend.AddEntry(graph_waveform[chan], md.getNameOfSensor(chan), "l")



    xAxisTitle = "Time (ns)"
    yAxisTitle = "Voltage (mV)"
    titleAbove = "Waveform, sensor: "+md.getNameOfSensor(channel)+", batch "+str(md.getBatchNumber(runNumber))+", run "+str(md.getRunNumber())+", "+channel


    multi_graph.Draw("ALP")
    
    graph_waveform[chan].SetMarkerStyle(1)

    multi_graph.SetTitle(titleAbove)
    multi_graph.GetXaxis().SetTitle(xAxisTitle)
    multi_graph.GetYaxis().SetTitle(yAxisTitle)
    multi_graph.GetYaxis().SetRangeUser(-30,500)
    
    if peak_time_LGAD < peak_time_SiPM:
    
        multi_graph.GetXaxis().SetRangeUser(peak_time_LGAD-5, peak_time_SiPM+5)
    
    else:
        multi_graph.GetXaxis().SetRangeUser(peak_time_SiPM-5, peak_time_LGAD+5)
    legend.AddEntry(graph_vertical[chan], md.getNameOfSensor(channel)+" time difference: "+str(peak_time_LGAD-peak_time_SiPM)[0:6], "")

    textSmallOrLarge = "_large_peak"
    folderSmallOrLarge = "/large_peak"

    if ifSmallPeak:
        textSmallOrLarge = "_small_peak"
        folderSmallOrLarge = "/small_peak"

    
    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/double_peak/"+str(md.getNameOfSensor(channel))+folderSmallOrLarge+"/waveform"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(event)+"_"+str(channel)+"_"+str(md.getNameOfSensor(channel))+textSmallOrLarge+".pdf"
    legend.Draw()
    canvas.Print(fileName)

