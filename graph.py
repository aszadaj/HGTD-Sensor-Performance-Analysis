import ROOT
import numpy as np
import root_numpy as rnm
import metadata as md
import data_management as dm

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform():

    runNumber = 3791
    startEntry = 200
    entries = 5

    timeStamp = md.getTimeStamp(runNumber)
    row = md.getRowForRunNumber(runNumber)
    md.defineGlobalVariableRun(row)
    dm.checkIfRepositoryOnStau()
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"
    data = rnm.root2array(dataPath, start=startEntry, stop=startEntry+entries)
    channels = data.dtype.names
    
    noise_average = dm.importNoiseFile("pedestal")
    noise_std = dm.importNoiseFile("noise")
  
    #rise_time = dm.importPulseFile("rise_time")
    
    graph_waveform = dict()
    graph_line_threshold = dict()
    graph_line_noise = dict()
    graph_line_pedestal = dict()

    N = 6
    
    noise = dict()
    pedestal = dict()
    
    for chan in channels:
        pedestal[chan]     = np.average(np.take(noise_average[chan], np.nonzero(noise_average[chan]))[0])*-1000
        noise[chan]  = np.average(np.take(noise_std[chan], np.nonzero(noise_std[chan]))[0])*1000

    
    for chan in channels:
        
        threshold = noise[chan] * N + pedestal[chan]
   
        canvas = ROOT.TCanvas("Waveforms","Waveforms")
        leg = ROOT.TLegend (0.73, 0.6, 0.93, 0.9)
        leg.SetHeader("N = "+str(sigma))
    
        graph_waveform[chan]        = ROOT.TGraph(1002*entries)
        graph_line_threshold[chan]  = ROOT.TGraph(1002*entries)
        graph_line_pedestal[chan]   = ROOT.TGraph(1002*entries)
        graph_line_noise[chan]      = ROOT.TGraph(1002*entries)
        
        i = 0
        
        for event in range(0, entries):
            for index in range(0, len(data[chan][event])):
                
                graph_waveform[chan].SetPoint(i,i*0.1, data[chan][event][index]*-1000)
                i+=1

        for index in range(0,1002*entries):
    
            graph_line_threshold[chan].SetPoint(index, index*0.1, threshold)
            graph_line_pedestal[chan].SetPoint(index, index*0.1, pedestal[chan])
            graph_line_noise[chan].SetPoint(index, index*0.1, noise[chan])


        graph_waveform[chan].SetLineColor(2)
        graph_waveform[chan].Draw("AL")
        
        graph_line_threshold[chan].SetLineColor(3)
        #graph_line_threshold[chan].Draw("L")
        
        graph_line_pedestal[chan].SetLineColor(6)
        #graph_line_pedestal[chan].Draw("L")
        
        graph_line_noise[chan].SetLineColor(7)
        #graph_line_noise[chan].Draw("L")

        leg.AddEntry(graph_line_threshold[chan],"Threshold = "+str(threshold)[1:7]+" mV","l")
        leg.AddEntry(graph_line_pedestal[chan],"Pedestal = "+str(pedestal[chan])[1:7]+" mV","l")
        leg.AddEntry(graph_line_noise[chan],"Noise  = "+str(noise[chan])[1:7]+" mV","l")


        titleAbove = "Waveform, sensor "+str(md.getNameOfSensor(chan))+", channel: "+str(int(chan[-1:]))+", batch "+str(md.getBatchNumber(runNumber))
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Voltage (mV)"

        
        graph_waveform[chan].GetYaxis().SetTitle(yAxisTitle)
        graph_waveform[chan].GetXaxis().SetTitle(xAxisTitle)
        graph_waveform[chan].SetTitle(titleAbove)
        
        graph_waveform[chan].GetYaxis().SetRangeUser(-30,300)
        graph_waveform[chan].GetXaxis().SetRangeUser(0,100*entries)
        

        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/waveforms/waveform_"+str(runNumber)+"_entry_"+str(startEntry)+"_"+str(chan)+".pdf"
        #leg.Draw()
        
        canvas.Update()
        canvas.Print(fileName)
        canvas.Clear()

        del canvas
        del leg



printWaveform()

