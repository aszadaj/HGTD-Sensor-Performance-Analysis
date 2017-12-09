import ROOT
import root_numpy as rnm
import numpy as np

import metadata as md
import data_management as dm

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform(runNumber, entries):

    for entry in entries:
    
        timeStamp = md.getTimeStamp(runNumber)
        row = md.getRowForRunNumber(runNumber)
        md.defineGlobalVariableRun(row)
        dm.checkIfRepositoryOnStau()
        
        noise = dm.importNoiseFile("noise")
        
        #amplitudes = dm.importPulseFile("amplitudes")
        
        SiPM_name = "SiPM-AFP"
        SiPM_chan = md.getChannelNameForSensor(SiPM_name)
        
        dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"

        data = rnm.root2array(dataPath, start=entry, stop=entry+1)
        
        # Structure of data[chan][event][index] = value

        graph = dict()
        graph_line_noise = dict()
        
        canvas = dict()
        leg = dict()
        
       

        channels = data.dtype.names
        first = True
        
        sigma = 5
        channels = ["chan2"]
        
        for chan in channels:
        
            leg[chan] = ROOT.TLegend (0.73, 0.6, 0.93, 0.9)
            leg[chan].SetHeader("Waveforms, sensors")
            
            leg[chan].Draw()
        
        
            canvas[chan] = ROOT.TCanvas("Waveforms"+chan,"Waveforms"+chan)
       
            graph[chan] = ROOT.TGraph(1002)

            for index in range(0, len(data[chan][0])):
                
                graph[chan].SetPoint(index,index*0.1, data[chan][0][index]*-1000)

            titleAbove = "Waveform for run number " +str(runNumber)+ ", batch "+str(md.getBatchNumber(runNumber))+ ", entry " + str(entry)
            
            xAxisTitle = "Time (ns)"
            yAxisTitle = "Voltage (mV)"
            
            if first:
                graph[chan].Draw("AL")
                first=False

            else:
                graph[chan].Draw("L")
      
            graph_line_noise[chan] = ROOT.TGraph(1002)
            for index in range(0,1002):
        
                graph_line_noise[chan].SetPoint(index, index*0.1, noise[chan]*sigma)
            
            graph_line_noise[chan].SetLineColor(int(chan[-1])+1)
            graph_line_noise[chan].SetMarkerColor(2)
            graph_line_noise[chan].Draw("L")
            n=str(noise[chan][0])
            leg[chan].AddEntry(graph_line_noise[chan],"Noise: "+n[:-8]+" mV, \sigma: "+str(sigma),"l")

            graph[chan].SetLineColor(int(chan[-1])+1)
            graph[chan].SetMarkerColor(1)
            graph[chan].GetYaxis().SetTitle(yAxisTitle)
            graph[chan].GetXaxis().SetTitle(xAxisTitle)
            graph[chan].GetYaxis().SetRangeUser(-40,400)
            graph[chan].GetXaxis().SetRangeUser(0,100)
            leg[chan].AddEntry(graph[chan], md.getNameOfSensor(chan) + " Waveform ","l")
            
            
            graph[chan].SetTitle(titleAbove)
        
            fileName = "../../HGTD_material/plots/waveforms/waveform_"+str(runNumber)+"_entry_"+str(entry)+"_"+str(chan)+".pdf"
            leg[chan].Draw()
            canvas[chan].Update()
            canvas[chan].Print(fileName)
