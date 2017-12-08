import ROOT
import root_numpy as rnm
import numpy as np

import pulse_calculations as p_calc
import pulse_plot as p_plot
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform(runNumber, entries):

    for entry in entries:
    
        timeStamp = md.getTimeStamp(runNumber)
        row = md.getRowForRunNumber(runNumber)
        md.defineGlobalVariableRun(row)
        dm.checkIfRepositoryOnStau()
        
        pedestal = dm.importNoiseFile("pedestal")
        amplitudes = dm.importPulseFile("amplitudes")
        
        SiPM_name = "SiPM-AFP"
        SiPM_chan = md.getChannelNameForSensor(SiPM_name)
        SiPM_index = int(SiPM_chan[-1])
        
        for entry in range(0,len(amplitudes[chan])):
            for chan in amplitudes.dtype.names:
                if chan != SiPM_chan and amplitudes[chan][entry] != 0:
                    print entry, chan
                    count += 1
                    
            if count == 15:
                break
        

        dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"

        data = rnm.root2array(dataPath, start=entry, stop=entry+1)
        
        # Structure of data[chan][event][index] = value

        graph = dict()
        
        canvas = ROOT.TCanvas("Waveforms","Waveforms")
        
        leg = ROOT.TLegend (0.73, 0.6, 0.93, 0.9)
        leg.SetHeader("Waveforms, sensors")
        
        leg.Draw()

        channels = data.dtype.names
        first = True

        for chan in channels:

            graph[chan] = ROOT.TGraph(1002)

            for index in range(0, len(data[chan][0])):
                
                graph[chan].SetPoint(index,index*0.1, data[chan][0][index]*-1000)

            titleAbove = "Waveform for run number " +str(runNumber)+ ", entry " + str(entry)
            
            xAxisTitle = "Time (ns)"
            yAxisTitle = "Voltage (mV)"
            
            if first:
                graph[chan].Draw("AL")
                first=False

            else:
                graph[chan].Draw("L")
            
            graph[chan].SetLineColor(int(chan[-1])+1)
            graph[chan].SetMarkerColor(1)
            graph[chan].GetYaxis().SetTitle(yAxisTitle)
            graph[chan].GetXaxis().SetTitle(xAxisTitle)
            graph[chan].GetYaxis().SetRangeUser(-40,400)
            graph[chan].GetXaxis().SetRangeUser(40,60)
            leg.AddEntry(graph[chan], md.getNameOfSensor(chan) + " pedestal " + str(pedestal[chan])[:-10] + " mV","l")
            
            
            graph[chan].SetTitle(titleAbove)
        

        fileName = "plots/waveforms/waveform_"+str(runNumber)+"_entry_"+str(entry)+".pdf"
        leg.Draw()
        canvas.Update()
        canvas.Print(fileName)


