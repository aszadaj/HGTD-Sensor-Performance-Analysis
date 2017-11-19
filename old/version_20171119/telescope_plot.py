
import ROOT
import numpy as np
import root_numpy as rnm
import pickle


# Define the code to make the analysis
def produceTelescopeGraphs(data, amplitude, runNumber, sensors):

    canvas = ROOT.TCanvas("TProfile2D","TProfile2D")
    telescope_graph = dict()

    channels = amplitude.dtype.names
    
    for chan in channels:
    
        chan_index = int(chan[-1:])
    
        telescope_graph[chan] = ROOT.TProfile2D("telescope_"+chan,"Telescope channel "+str(int(chan[-1:])+1),500,-4,4,500,10,15.3)
        
        for index in range(0,len(data)):
            if data['X'][index] != -9999 and amplitude[chan][index] > 0:
                telescope_graph[chan].Fill(data['X'][index], data['Y'][index], amplitude[chan][index])
    
        titleAbove = "Distribution of found hits in each bin, Sep 2017 run "+str(runNumber)+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
        xAxisTitle = "X position (mm)"
        yAxisTitle = "Y position (mm)"
        telescope_graph[chan].GetYaxis().SetTitle(yAxisTitle)
        telescope_graph[chan].GetXaxis().SetTitle(xAxisTitle)
        canvas.cd()
        telescope_graph[chan].Draw("COLZ")
        #telescope_graph[chan].LabelsOption("")
        canvas.Update()
        filename = "plots/telescope_plot/telescope_"+str(runNumber)+"_"+str(chan)+".pdf"
        canvas.Print(filename)

