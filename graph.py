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
    
    #amplitudes = dm.importPulseFile("amplitudes")
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"

    data = rnm.root2array(dataPath, start=entry, stop=entry+1)
    
    # Structure of data[chan][event][index] = value

    graph = dict()
    graph_line_noise = dict()
    
    channels = data.dtype.names
    first = True
    
    sigma = 5
    
    leg = ROOT.TLegend (0.73, 0.6, 0.93, 0.9)
    leg.SetHeader("Waveforms, sensors")
    
    canvas = ROOT.TCanvas("Waveforms","Waveforms")
    
    channels = ["chan3","chan6"]
    
    for chan in channels:

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
        n = str(noise[chan][0])
        leg.AddEntry(graph_line_noise[chan],"Noise: "+n[:-8]+" mV, \sigma: "+str(sigma),"l")

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

# Batch 306, channels which have strange time differences, the next peak
#chan1 144
#chan1 374
#chan3 403
#chan5 494
#chan4 553
#chan5 715
#chan0 752
#chan5 841
#chan2 862
#chan5 1060
#chan3 1219
#chan1 1324
#chan2 1365
#chan2 1701
#chan3 2124
#chan3 2148
#chan3 2492
#chan1 2583
#chan2 2603
#chan3 2909
#chan4 2926
#chan5 3010
#chan1 3136
#chan1 3167
#chan2 3203
#chan3 3235
#chan3 3544
#chan2 3572
#chan0 3597
#chan3 3785
#chan5 3793
#chan5 3837
#chan3 3845
#chan1 3879
#chan5 3995
#chan3 4039
#chan4 4198
#chan3 4216
#chan1 4464
#chan0 4497
#chan1 4986
#chan4 5119
#chan5 5411
#chan3 5412
#chan1 5915
#chan3 5925
#chan1 6378
#chan4 6397
#chan0 6435
#chan3 6854
#chan2 6980
#chan3 7076
#chan3 7120
#chan4 7223
#chan5 7467
#chan1 7527
#chan4 7619
#chan3 8082
#chan2 8101
#chan4 8145
#chan5 8253
#chan3 8965
#chan3 9072
#chan1 9127
#chan3 9133
#chan5 9158
#chan4 9490
#chan1 9560
#chan5 9717
#chan3 9743
#chan1 9994
#chan1 10039
#chan1 10395
#chan4 10981
#chan4 11083
#chan1 11129
#chan1 11235
#chan3 11514
#chan1 11632
#chan1 11831
#chan5 11883
#chan5 12026
#chan2 12378
#chan2 12607
#chan1 12623
#chan1 13117
#chan1 13242
#chan2 13314
#chan3 13354
#chan1 13374
#chan0 13379
#chan2 13516
#chan3 13694
#chan5 13724
#chan3 13769
#chan3 13977
#chan2 14060
#chan4 14135
#chan2 14264
#chan3 14264

