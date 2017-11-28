
import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md


def produceTelescopeGraphs(data, amplitude, number):

    global xMin
    global xMax
    global xBins
    global yMin
    global yMax
    global yBins
    global chan
    global batchNumber
    
    # Check how to fix that the graphs fit
    
    xMin = -5
    xMax = 0
    xBins = 1000
    yMin = 10
    yMax = 15
    yBins = 1000
    batchNumber = number

    canvas_graph = ROOT.TCanvas("TelescopeGraph","TelescopeGraph")
    canvas_error = ROOT.TCanvas("Standard Deviation","Standard Deviation")
    canvas_eff   = ROOT.TCanvas("Efficiency","Efficiency")
    canvas_hist  = ROOT.TCanvas("Histogram","Histogram")

    graph_meanValue = dict()
    graph_std = dict()
    graph_eff   = dict()
    graph_hist  = dict()

    channels = amplitude.dtype.names
    
    for chan in channels:
    
        produceMeanPlot(data, amplitude, graph_meanValue, canvas_graph)
        produceStdPlot(data, graph_std, graph_meanValue, canvas_error)
        produceEfficiencyPlot(data,amplitude, graph_eff, canvas_eff)
        produceMeanDistributionPlots(data, graph_hist, graph_meanValue, canvas_hist)


def produceMeanDistributionPlots(data, graph_hist, graph_meanValue, canvas):

    graph_hist[chan] = ROOT.TH1F("distribution_"+chan+"_histogram","Mean value distribution "+str(int(chan[-1:])+1),200,0,400)
  
    bins = graph_meanValue[chan].GetSize()
    
    for bin in range(0, int(bins)):
        error = graph_meanValue[chan].GetBinError(bin)
        meanVal = graph_meanValue[chan].GetBinContent(bin)
        if error != 0.0:
            graph_hist[chan].Fill(meanVal)
        

    headTitle = "Mean amplitude value distribution from each bin (mV)"
    fileName = "_hist.pdf"
    produceTH1Plot(graph_hist[chan], canvas, headTitle, fileName)


def produceMeanPlot(data, amplitude, graph_meanValue, canvas_graph):

    graph_meanValue[chan] = ROOT.TProfile2D("telescope_"+chan,"Telescope channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    
    
    for index in range(0,len(data)):
         if data['X'][index] > -9.0 and amplitude[chan][index] > 0:
            graph_meanValue[chan].Fill(data['X'][index], data['Y'][index], amplitude[chan][index])

    headTitle = "Maximal amplitude mean value (mV) in each bin"
    fileName = ".pdf"
    produceTH2Plot(graph_meanValue[chan], canvas_graph, headTitle, fileName)


def produceStdPlot(data, graph_std, graph_meanValue, canvas_error):

    graph_std[chan] = ROOT.TH2F("telescope_"+chan+"_error","Telescope channel "+str(int(chan[-1:])+1)+" Standard Deviation",xBins,xMin,xMax,yBins,yMin,yMax)
   
    bins = graph_meanValue[chan].GetSize()
    
    for bin in range(0, int(bins)):
        error = graph_meanValue[chan].GetBinError(bin)
        if error != 0.0:
            graph_std[chan].SetBinContent(bin, error)
            graph_std[chan].SetBinError(bin, 0)
        

    headTitle = "Standard deviation of amplitude values (mV) in each bin"
    fileName = "_std.pdf"
    produceTH2Plot(graph_std[chan], canvas_error, headTitle, fileName)


def produceEfficiencyPlot(data, amplitude, graph_eff, canvas_eff):
    
    LGAD_particles = ROOT.TH2F("LGAD_particles"+chan+"","LGAD particles channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    
    tel_particles = ROOT.TH2F("telescope_particles"+chan+"","Telescope particles channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    
    for index in range(0,len(data)):
        if data['X'][index] > -9.0:
            tel_particles.Fill(data['X'][index], data['Y'][index], 1.0)
            if amplitude[chan][index] > 0:
                LGAD_particles.Fill(data['X'][index], data['Y'][index], 1.0)


    graph_eff[chan] = ROOT.TEfficiency(LGAD_particles, tel_particles)
    
    
    # Log: This function is for trying to find the mean value bin for which the
    # conditions are high enough. Try to restrict filling with minimum amount of entries
    # per bin, say 10. Do this as the first stage when the comparison begins L: 56
    
#
#    graph_selected = ROOT.TEfficiency("TEfficiency_selected","Telescope particles higher conditions channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
#
#    for bin in range(0, int(graph_eff[chan].GetSize()):
#        binValue = graph_eff[chan].GetEfficiency(bin)
#        if binValue > 0.9:
#            graph_selected.SetBinContent(bin,binValue)
#
#

    

#    print "TEfficiency mean " + " batch " + str(batchNumber) + ", channel: " + chan
#    print "TEfficiency mean x: " + graph_eff[chan].GetMean(1)
#    print "TEfficiency mean y: " + graph_eff[chan].GetMean(2)
#    print "TEfficiency mean z: " + graph_eff[chan].GetMean(3) + "\n"
    
    headTitle = "Efficiency of hit particles in each bin"
    fileName = "_eff.pdf"
    produceTH2Plot(graph_eff[chan], canvas_eff, headTitle, fileName)


def produceTH2Plot(graph, canvas, headTitle, fileName):
    
    title = headTitle + ", Sep 2017 batch " + str(batchNumber)+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw("COLZ")
    canvas.Update()
    canvas.Print("plots/telescope_2d_distributions/telescope_"+str(batchNumber)+"_"+str(chan) + fileName)


def produceTH1Plot(graph, canvas, headTitle, fileName):

    title = headTitle + ", Sep 2017 batch " + str(batchNumber)+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "Mean amplitude value per bin" + "; " + "Entries (N)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw()
    canvas.Update()
    canvas.Print("plots/telescope_2d_distributions/telescope_"+str(batchNumber)+"_"+str(chan) + fileName)



