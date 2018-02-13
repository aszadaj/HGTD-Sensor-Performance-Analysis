import ROOT
import numpy as np
import root_numpy as rnm
import metadata as md
import data_management as dm

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform():

    runNumber = 3793
    startEntry = 52093
    entries = 1

    md.setIfOnHDD(False)
    md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
    dm.checkIfRepositoryOnStau()

    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    if md.isOnHDD():
    
        dataPath = "/Volumes/HDD500/" + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    data = rnm.root2array(dataPath, start=startEntry, stop=startEntry+entries)
    
    peak_value = dm.importPulseFile("peak_value")
    timing_difference = dm.importTimingFile()
    
    
    channels = data.dtype.names

    multi_graph = ROOT.TMultiGraph()
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    
    graph_waveform = dict()
    
    channels = ["chan4", "chan6"]

    for chan in channels:
        
        graph_waveform[chan]        = ROOT.TGraph(1002*entries)
        
        i = 0
        
        for event in range(0, entries):
            for index in range(0, len(data[chan][event])):
                
                graph_waveform[chan].SetPoint(i,i*0.1, data[chan][event][index]*-1000)
                i+=1

        graph_waveform[chan].SetLineColor(int(chan[-1])+1)
        multi_graph.Add(graph_waveform[chan])



    xAxisTitle = "Time (ns)"
    yAxisTitle = "Voltage (mV)"
    titleAbove = "Waveform, "+chan+", sensor: "+md.getNameOfSensor(chan)+" batch "+str(md.getBatchNumber(runNumber))

    multi_graph.SetTitle(titleAbove)
    multi_graph.Draw("ALP")
    multi_graph.GetXaxis().SetTitle(xAxisTitle)
    multi_graph.GetYaxis().SetTitle(yAxisTitle)

    multi_graph.GetYaxis().SetRangeUser(-30,300)
    multi_graph.GetXaxis().SetRangeUser(0,100*entries)
    #multi_graph.GetXaxis().SetRangeUser(47,52)


    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/waveforms/waveform_"+str(runNumber)+"_entry_"+str(startEntry)+"_"+str(channels)+".pdf"

    canvas.Print(fileName)

printWaveform()

