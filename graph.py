import ROOT
import root_numpy as rnm
import numpy as np

import metadata as md
import data_management as dm

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform(runNumber, entry):

    entries = 2

    timeStamp = md.getTimeStamp(runNumber)
    row = md.getRowForRunNumber(runNumber)
    md.defineGlobalVariableRun(row)
    dm.checkIfRepositoryOnStau()
    
    noise = dm.importNoiseFile("noise")
    pedestal = dm.importNoiseFile("pedestal")
    
    #amplitudes = dm.importPulseFile("amplitudes")
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"

    data = rnm.root2array(dataPath, start=entry, stop=entry+entries)
    
    graph_waveform = dict()
    graph_line_threshold = dict()
    graph_line_noise = dict()
    graph_line_pedestal = dict()
    
    channels = data.dtype.names
    first = True
    
    sigma = 5.0
    
    leg = ROOT.TLegend (0.73, 0.6, 0.93, 0.9)
    leg.SetHeader("Waveforms, sensors")
    
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    
    # SiPM chan6
    
    channels = ["chan1", "chan6"]
    
    for chan in channels:
    
        print noise[chan], "noise", chan
        print pedestal[chan], "pedestal", chan

        graph_waveform[chan] = ROOT.TGraph(1002*entries)
        graph_line_threshold[chan] = ROOT.TGraph(1002*entries)
        graph_line_pedestal[chan] = ROOT.TGraph(1002*entries)
        graph_line_noise[chan] = ROOT.TGraph(1002*entries)
        
        i = 0
        
        for event in range(0, entries):
            for index in range(0, len(data[chan][event])):
                
                graph_waveform[chan].SetPoint(i,i*0.1, data[chan][event][index]*-1000)
                i+=1


        # Check what happens if the limit is pedestal corrected!
        for index in range(0,1002*entries):
    
            graph_line_threshold[chan].SetPoint(index, index*0.1, noise[chan]*sigma-pedestal[chan])
#            graph_line_pedestal[chan].SetPoint(index, index*0.1, pedestal[chan])
#            graph_line_noise[chan].SetPoint(index, index*0.1, noise[chan])

            
        drawOpt = "LP"
        if first:
            drawOpt = "ALP"
            first=False


        graph_waveform[chan].SetLineColor(int(chan[-1])+1)
        graph_waveform[chan].SetMarkerColor(int(chan[-1])+1)
        graph_waveform[chan].Draw(drawOpt)
        
        graph_line_threshold[chan].SetLineColor(int(chan[-1])+1)
        graph_line_threshold[chan].SetMarkerColor(int(chan[-1])+1)
        graph_line_threshold[chan].Draw("L")

        graph_line_pedestal[chan].SetLineColor(int(chan[-1])+2)
        graph_line_pedestal[chan].SetMarkerColor(int(chan[-1])+2)
        graph_line_pedestal[chan].Draw("L")
        
        graph_line_pedestal[chan].SetLineColor(int(chan[-1])+3)
        graph_line_pedestal[chan].SetMarkerColor(int(chan[-1])+3)
        graph_line_pedestal[chan].Draw("L")
        
        graph_line_noise[chan].SetLineColor(int(chan[-1])+4)
        graph_line_noise[chan].SetMarkerColor(int(chan[-1])+4)
        graph_line_noise[chan].Draw("L")

        leg.AddEntry(graph_line_threshold[chan],"Threshold "+str(chan)+ "="+str(noise[chan]*sigma-pedestal[chan])[1:5]+" mV, \sigma: "+str(sigma),"l")
#        leg.AddEntry(graph_line_pedestal[chan],"Pedestal "+str(chan)+ "="+str(pedestal[chan])[1:5]+" mV","l")
#        leg.AddEntry(graph_line_noise[chan],"Noise "+str(chan)+ "="+str(noise[chan])[1:5]+" mV","l")


        titleAbove = "Waveform, sensor "+str(md.getNameOfSensor(chan))+", batch "+str(md.getBatchNumber(runNumber))
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Voltage (mV)"

        
        graph_waveform[chan].GetYaxis().SetTitle(yAxisTitle)
        graph_waveform[chan].GetXaxis().SetTitle(xAxisTitle)
        graph_waveform[chan].SetTitle(titleAbove)
        
        graph_waveform[chan].GetYaxis().SetRangeUser(-50,450)
        graph_waveform[chan].GetXaxis().SetRangeUser(0,100*entries)

        canvas.Update()
    
    
    fileName = "../../HGTD_material/plots_hgtd_efficiency_sep_2017/waveforms/waveform_"+str(runNumber)+"_entry_"+str(entry)+"_"+str(channels)+".pdf"
    leg.Draw()
    canvas.Update()
    canvas.Print(fileName)

