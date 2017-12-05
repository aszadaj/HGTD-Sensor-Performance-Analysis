import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(255)

def produceTelescopeGraphs(data_telescope, data_amplitude):
   
    global xMin
    global xMax
    global xBins
    global yMin
    global yMax
    global yBins
    global chan
    global data
    global amplitude
    global canvas
    global minEntries
    
    xMin = -6
    xMax = 2.0
    xBins = 700
    yMin = 10
    yMax = 15
    yBins = 700
    
    data = data_telescope
    amplitude = data_amplitude

    canvas = ROOT.TCanvas("Telescope","telescope")
    channels = amplitude.dtype.names
    
    minEntries = 3
    
    channels = channels[0:1]
    
    for chan in channels:
    
        # 1. Shows the mean amplitude in each filled bin (with or without conditions)
        # 2. Shows efficiency between telescope data and amplitude data
        
        produceTProfile2DPlot()
        produceTEfficiencyPlot()


def produceTProfile2DPlot():

    graph = ROOT.TProfile2D("telescope_"+chan,"Telescope channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)

    for index in range(0,len(data)):
         if data['X'][index] > -9.0 and amplitude[chan][index] > 0.0:
            graph.Fill(data['X'][index], data['Y'][index], amplitude[chan][index])

    graphFiltered = graph.Clone()
    
    totalEntries = int(graphFiltered.GetEntries())
    unwantedEntries = 0

    # Remove bins which have less than x entries
    for bin in range(0, int(graphFiltered.GetSize())):
        entries = int(graphFiltered.GetBinEntries(bin))
        
        if 0 < entries < minEntries:
        
            graphFiltered.SetBinContent(bin, 0)
            graphFiltered.SetBinEntries(bin, 0)
            unwantedEntries += 1

    graphFiltered.SetEntries((totalEntries-unwantedEntries))

    headTitle = "Maximal amplitude mean value (mV) in each bin, entries " + str(int(graphFiltered.GetEntries()))
    fileName = ".pdf"
    produceTH2Plot(graphFiltered, headTitle, fileName)

    # Given the filtered values, produce histogram
    produceTH1MeanPlot(graphFiltered)
    
    del graph, graphFiltered



def produceTEfficiencyPlot():
    
    LGAD_hits_temp = ROOT.TProfile2D("LGAD_particles"+chan+"","LGAD particles channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    
    telescope_hits_temp = ROOT.TProfile2D("telescope_particles"+chan+"","Telescope particles channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    
    for index in range(0,len(data)):
        if data['X'][index] > -9.0:
            telescope_hits_temp.Fill(data['X'][index], data['Y'][index], 1.0)
            if amplitude[chan][index] > 0:
                LGAD_hits_temp.Fill(data['X'][index], data['Y'][index], 1.0)

    LGAD_hits = LGAD_hits_temp.Clone()
    telescope_hits = telescope_hits_temp.Clone()

    for bin in range(0, int(LGAD_hits.GetSize())):
    
        entries_LGAD = int(LGAD_hits.GetBinEntries(bin))
        entries_telescope = int(telescope_hits.GetBinEntries(bin))
        
        if 0 < entries_LGAD < minEntries:

            LGAD_hits.SetBinContent(bin, 0)
            LGAD_hits.SetBinEntries(bin, 0)
        
        if 0 < entries_telescope < minEntries:

            telescope_hits.SetBinContent(bin, 0)
            telescope_hits.SetBinEntries(bin, 0)


    graph = ROOT.TEfficiency(LGAD_hits, telescope_hits)


    headTitle = "Efficiency of hit particles in each bin"
    fileName = "_eff.pdf"
    produceTH2Plot(graph, headTitle, fileName)

    del LGAD_hits, LGAD_hits_temp, telescope_hits, telescope_hits_temp, graph



def produceTH1MeanPlot(graphTH2):

    graphTH1 = ROOT.TH1F("distribution_"+chan+"_histogram","Mean value distribution "+str(int(chan[-1:])+1),200,0,400)


    for bin in range(0, int(graphTH2.GetSize())):
        error = graphTH2.GetBinError(bin)
        if error != 0.0:
            meanVal = graphTH2.GetBinContent(bin)
            graphTH1.Fill(meanVal)
    

    headTitle = "Mean amplitude value distribution from each bin (mV)"
    fileName = "_hist.pdf"
    produceTH1Plot(graphTH1, headTitle, fileName)

    del graphTH1


def produceTH1Plot(graph, headTitle, fileName):

    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "Mean amplitude value per bin" + "; " + "Entries (N)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw()
    canvas.Update()
    canvas.Print("plots/telescope_2d_distributions/telescope_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()


def produceTH2Plot(graph, headTitle, fileName):
    
    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw("COLZ")
    canvas.Update()
    canvas.Print("plots/telescope_2d_distributions/telescope_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()

