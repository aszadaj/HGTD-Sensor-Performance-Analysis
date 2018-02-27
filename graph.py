import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm
import pulse_calculations as p_calc

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform():


    runNumber = 3921
    firstEvent = 16492
    entries = 1
    N = 5

    dm.setIfOnHDD(True)
    dm.setIfOnHITACHI(False)
    md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
    dm.checkIfRepositoryOnStau()


    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    if dm.isOnHDD():
    
        dataPath = "/Volumes/HDD500/" + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
        
    elif dm.isOnHITACHI():
    
        dataPath = "/Volumes/HITACHI/" + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    data = rnm.root2array(dataPath, start=firstEvent, stop=firstEvent+entries)
 

  
    pedestal, noise = p_calc.getPedestalAndNoise(dm.importNoiseFile("pedestal"), dm.importNoiseFile("noise"))
    pedestal, noise  = dm.convertNoiseData(pedestal, noise)
    

    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    legend = ROOT.TLegend(0.65, 0.9, 0.9, 0.7)
    
    graph_waveform = dict()
    graph_threshold = dict()
    
    
    channels = data.dtype.names
    channels = ["chan4"]

    for chan in channels:
    
        graph_waveform[chan] = ROOT.TGraph(1002*entries)
        graph_threshold[chan] = ROOT.TGraph(2)
        
        i = 0
        
        for event in range(0, entries):
            for index in range(0, len(data[chan][event])):
                
                graph_waveform[chan].SetPoint(i,i*0.1, data[chan][event][index]*-1000)
                i+=1

        graph_waveform[chan].SetLineColor(int(chan[-1])+1)
        graph_threshold[chan].SetLineColor(int(chan[-1])+1)
        
        threshold = noise[chan] * N + pedestal[chan]
        graph_threshold[chan].SetPoint(0,0, threshold[0])
        graph_threshold[chan].SetPoint(1,1002*entries, threshold[0])
        
        multi_graph.Add(graph_threshold[chan])
        multi_graph.Add(graph_waveform[chan])
        legend.AddEntry(graph_waveform[chan], md.getNameOfSensor(chan), "l")
        legend.AddEntry(graph_threshold[chan], "Threshold: "+str(threshold[0])[:5]+" mV", "l")


    xAxisTitle = "Time (ns)"
    yAxisTitle = "Voltage (mV)"
    headTitle = "Waveform, batch: "+str(md.getBatchNumber(runNumber)) + ", run: "+ str(md.getRunNumber())


    multi_graph.Draw("ALP")
    legend.Draw()
    multi_graph.SetTitle(headTitle)
    multi_graph.GetXaxis().SetTitle(xAxisTitle)
    multi_graph.GetYaxis().SetTitle(yAxisTitle)

    multi_graph.GetYaxis().SetRangeUser(-30,400)
    multi_graph.GetXaxis().SetRangeUser(0,100*entries)
    #multi_graph.GetXaxis().SetRangeUser(40,70)


    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/waveforms/waveform"+"_"+str(md.getBatchNumber())+"_"+str(runNumber)+"_event_"+str(firstEvent)+".pdf"


    canvas.Print(fileName)

printWaveform()

