
import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md


def produceTelescopeGraphs(data, amplitude):

    runNumber = md.getRunNumber()
    sensors = md.getSensorNames()
    
    canvas_graph = ROOT.TCanvas("TelescopeGraph","TelescopeGraph")
    canvas_error = ROOT.TCanvas("TelescopeGraph2","TelescopeGraph2")

    telescope_graph = dict()
    
    telescope_error = dict()

    channels = amplitude.dtype.names
    
    for chan in channels:
    
        xMin = -6
        xMax = 2
        xBins = 500
        yMin = 10
        yMax = 15.3
        yBins = 500
    
        chan_index = int(chan[-1:])
        
        telescope_graph[chan] = ROOT.TProfile2D("telescope_"+chan,"Telescope channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
        
        # amplitude[chan][index] is maximal amplitude value in mV. If not found, then 0.
        
        for index in range(0,len(data)):
             if data['X'][index] != -9999 and amplitude[chan][index] > 0:
                telescope_graph[chan].Fill(data['X'][index], data['Y'][index], amplitude[chan][index])
    
        titleAbove = "Distribution of found hits in each bin, Sep 2017 run "+str(runNumber)+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
        xAxisTitle = "X position (mm)"
        yAxisTitle = "Y position (mm)"
        
        telescope_graph[chan].GetYaxis().SetTitle(yAxisTitle)
        telescope_graph[chan].GetXaxis().SetTitle(xAxisTitle)
        
        canvas_graph.cd()
        telescope_graph[chan].Draw("COLZ")

        canvas_graph.Update()
        
        filename = "plots/telescope_2d_distributions/telescope_"+str(runNumber)+"_"+str(chan)+".pdf"
        
        canvas_graph.Print(filename)


        # Error profile
        
        telescope_error[chan] = ROOT.TH2F("telescope_"+chan+"_error","Telescope channel "+str(int(chan[-1:])+1)+" Standard Deviation",xBins,xMin,xMax,yBins,yMin,yMax)
        
        
        bins = telescope_graph[chan].GetNumberOfBins()
        for bin in range(0, int(bins)):
            e = telescope_graph[chan].GetBinError(bin)
            if e != 0.0:
                telescope_error[chan].SetBinContent(bin, e)
                telescope_error[chan].SetBinError(bin, 0)

        titleAbove = "Standard deviation of found hits in each bin, Sep 2017 run "+str(runNumber)+", channel " + str(chan_index+1) + ", sensor: " + str(sensors[chan_index])
        xAxisTitle = "X position (mm)"
        yAxisTitle = "Y position (mm)"
        
        telescope_error[chan].GetYaxis().SetTitle(yAxisTitle)
        telescope_error[chan].GetXaxis().SetTitle(xAxisTitle)
        
        canvas_error.cd()
        telescope_error[chan].Draw("COLZ")

        canvas_error.Update()
        
        filename = "plots/telescope_2d_distributions/telescope2_"+str(runNumber)+"_"+str(chan)+".pdf"
        
        canvas_error.Print(filename)












        

