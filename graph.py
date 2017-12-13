import ROOT
import root_numpy as rnm
import numpy as np

import metadata as md
import data_management as dm

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform(runNumber, entry):

    timeStamp = md.getTimeStamp(runNumber)
    row = md.getRowForRunNumber(runNumber)
    md.defineGlobalVariableRun(row)
    dm.checkIfRepositoryOnStau()
    
    noise = dm.importNoiseFile("noise")
    pedestal = dm.importNoiseFile("pedestal")
    
    #amplitudes = dm.importPulseFile("amplitudes")
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"

    data = rnm.root2array(dataPath, start=entry, stop=entry+1)
    
    # Structure of data[chan][event][index] = value

    graph = dict()
    graph_line_noise = dict()
    
    channels = data.dtype.names
    first = True
    
    sigma = 6.0
    
    leg = ROOT.TLegend (0.73, 0.6, 0.93, 0.9)
    leg.SetHeader("Waveforms, sensors")
    
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    
    # SiPM chan6
    
    channels = ["chan6"]
    
    for chan in channels:

        graph[chan] = ROOT.TGraph(1002)

        for index in range(0, len(data[chan][0])):
            
            graph[chan].SetPoint(index,index*0.1, data[chan][0][index]*-1000)

        titleAbove = "Waveform for run number " +str(runNumber)+ ", batch "+str(md.getBatchNumber(runNumber))+ ", entry " + str(entry)
        
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Voltage (mV)"
        
        if first:
        
            graph[chan].Draw("ALP")
            first=False

        else:
        
            graph[chan].Draw("LP")


        graph_line_noise[chan] = ROOT.TGraph(1002)
        
        # Check what happens if the limit is pedestal corrected!
        for index in range(0,1002):
    
            graph_line_noise[chan].SetPoint(index, index*0.1, noise[chan]*sigma-pedestal[chan])
        
        graph_line_noise[chan].SetLineColor(int(chan[-1])+1)
        graph_line_noise[chan].SetMarkerColor(2)
        graph_line_noise[chan].Draw("L")
      
        leg.AddEntry(graph_line_noise[chan],"Threshold="+str(noise[chan]*sigma-pedestal[chan])[1:5]+" mV, \sigma: "+str(sigma),"l")

        graph[chan].SetLineColor(int(chan[-1])+1)
        graph[chan].SetMarkerColor(1)
        
        graph[chan].GetYaxis().SetTitle(yAxisTitle)
        graph[chan].GetXaxis().SetTitle(xAxisTitle)
        
        graph[chan].GetYaxis().SetRangeUser(-40,400)
        graph[chan].GetXaxis().SetRangeUser(0,100)
        
        leg.AddEntry(graph[chan], md.getNameOfSensor(chan) + " Waveform ","l")
    
        graph[chan].SetTitle(titleAbove)
        canvas.Update()
    
    
    fileName = "../../HGTD_material/plots_hgtd_efficiency_sep_2017/waveforms/waveform_"+str(runNumber)+"_entry_"+str(entry)+".pdf"
    leg.Draw()
    canvas.Update()
    canvas.Print(fileName)

