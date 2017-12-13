import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(255)


# The function receives two arrays, for a specific batch. They are structured as
# data[event][chan], where event spans along all run files. Example for B306 the max event is
# 11 files * 200 000 = 2 200 000 events

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
    xBins = 500
    yMin = 10
    yMax = 15
    yBins = 500
    
    data = data_telescope
    amplitude = data_amplitude

    canvas = ROOT.TCanvas("Telescope", "telescope")
    channels = amplitude.dtype.names
    
    minEntries = 2
    
    for chan in channels:
    
        # 1. Shows the mean amplitude in each filled bin (with or without conditions)
        # 2. Shows efficiency between telescope data and amplitude data
        if chan == "chan0" or chan == "chan1":
            produce2DPlots()
            produceTEfficiencyPlot()


def produce2DPlots():

    graphOrignal = ROOT.TProfile2D("telescope_"+chan,"Telescope channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    
    # Original mean value TProfile2D
    for index in range(0,len(data)):
         if data['X'][index] > -9.0 and amplitude[chan][index] > 0.0:
            graphOrignal.Fill(data['X'][index], data['Y'][index], amplitude[chan][index])

    graphStd = graphOrignal.Clone()

    # Standard deviation TProfile2D
    for bin in range(0, int(graphStd.GetSize())):
    
        errorPerBin   = int(graphOrignal.GetBinError(bin))
        entriesPerBin = int(graphOrignal.GetBinContent(bin))
        
        graphStd.SetBinContent(bin, errorPerBin)
        graphStd.SetBinEntries(bin, entriesPerBin)

    # Begin filtering
    graphFiltered = graphOrignal.Clone()
    graphStdFiltered =  graphStd.Clone()

    for bin in range(0, int(graphFiltered.GetSize())):
        entries = int(graphFiltered.GetBinEntries(bin))
        
        if entries <= minEntries:

            graphFiltered.SetBinContent(bin, 0)
            #graphFiltered.SetBinEntries(bin, 0)
            
            graphStdFiltered.SetBinContent(bin, 0)
            #graphStdFiltered.SetBinEntries(bin, 0)


    # Print original TProfile2D
    headTitle = "Pulse amplitude mean value (mV) in each bin, entries " + str(int(graphOrignal.GetEntries()))
    fileName = ".pdf"
    produceTH2Plot(graphOrignal, headTitle, fileName)

    # Efficiency and inefficiency
    headTitle = "Efficiency of hit particles in each bin"
    fileName = ".pdf_eff"
    #produceEfficiencyPlot(graphOrignal)

    headTitle = "Efficiency of hit particles in each bin"
    fileName = ".pdf_eff"
    #produceInefficiencyPlot(graphOrignal)


    # Print filtered TProfile2D
    headTitle = "Pulse amplitude mean value (mV) in each bin (filtered), entries " + str(int(graphFiltered.GetEntries()))
    fileName = "filtered.pdf"
    produceTH2Plot(graphFiltered, headTitle, fileName)

    # Efficiency and inefficiency
    headTitle = "Efficiency of hit particles in each bin (filtered)"
    fileName = "filtered_eff.pdf"
    #produceEfficiencyPlot(graphFiltered)

    headTitle = "Efficiency of hit particles in each bin (filtered)"
    fileName = "filtered_eff.pdf"
    #produceInefficiencyPlot(graphFiltered)


    # Print original std TProfile2D
    headTitle = "Pulse amplitude standard deviation (mV) in each bin, entries " + str(int(graphStd.GetEntries()))
    fileName = "_std.pdf"
    produceTH2Plot(graphStd, headTitle, fileName)


    # Print filtered std TProfile2D
    headTitle = "Pulse amplitude standard deviation (mV) in each bin (filtered), entries " + str(int(graphStdFiltered.GetEntries()))
    fileName = "_filtered_std.pdf"
    produceTH2Plot(graphStdFiltered, headTitle, fileName)


    del graphOrignal, graphStd, graphFiltered, graphStdFiltered



def produceTEfficiencyPlot():
    
    efficiencyOrig = ROOT.TEfficiency("Efficiency_particles"+chan+"","Effciency particles channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    
    LGADHitsOrig = ROOT.TProfile2D("LGAD_particles"+chan+"","LGAD particles channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    MIMOSAHitsOrig = ROOT.TProfile2D("telescope_particles"+chan+"","Telescope particles channel "+str(int(chan[-1:])+1),xBins,xMin,xMax,yBins,yMin,yMax)
    


    # Original TEfficiency, efficiency graph
    for index in range(0,len(data)):
        if data['X'][index] > -9.0:
            MIMOSAHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)
            
            efficiencyOrig.Fill(amplitude[chan][index] > 0.0, data['X'][index], data['Y'][index] ) # New TEfficiency object
            
            if amplitude[chan][index] > 0.0:
                LGADHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)
#
#    for bin in range(0, int(efficiencyOrig.GetTotalHistogram().GetSize())):




    LGADNoHitsOrig = LGADHitsOrig.Clone()
    
    # Orginial TEfficiency, inefficiency graph
    for index in range(0,len(data)):
        if data['X'][index] > -9.0:
            MIMOSAHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)
            if amplitude[chan][index] == 0.0:
                LGADNoHitsOrig.Fill(data['X'][index], data['Y'][index], 1.0)

    # Filter the results

    LGADHits = LGADHitsOrig.Clone()
    MIMOSAHits = MIMOSAHitsOrig.Clone()
    LGADNoHits = LGADNoHitsOrig.Clone()

    for bin in range(0, int(LGADHitsOrig.GetSize())):
    
        entries_LGAD = int(LGADHits.GetBinEntries(bin))
        entries_telescope = int(MIMOSAHits.GetBinEntries(bin))
        entries_LGAD_no_hits = int(LGADNoHits.GetBinEntries(bin))
        
        if 0 < entries_LGAD <= minEntries:

            LGADHits.SetBinContent(bin, 0)
            LGADHits.SetBinEntries(bin, 0)
        
        if 0 < entries_telescope <= minEntries:

            MIMOSAHits.SetBinContent(bin, 0)
            MIMOSAHits.SetBinEntries(bin, 0)

        if 0 < entries_LGAD_no_hits <= minEntries:
            
            LGADNoHits.SetBinContent(bin, 0)
            LGADNoHits.SetBinEntries(bin, 0)




    # Orginial efficiency graph
    
    headTitle = "Efficiency of hit particles in each bin"
    fileName = "_eff.pdf"
    #efficiency.GetHistogram().GetZAxis().SetRangeUser(0.9, 1.0)
    produceTH2Plot(efficiencyOrig, headTitle, fileName)
    
    
    
    
    
    # Original inefficiency graph
    inEfficiencyOrig = ROOT.TEfficiency(LGADNoHitsOrig, MIMOSAHitsOrig)
    headTitle = "Infficiency of hit particles in each bin"
    fileName = "_ineff.pdf"
    #efficiency.GetHistogram().GetZAxis().SetRangeUser(0.9, 1.0)
    produceTH2Plot(inEfficiencyOrig, headTitle, fileName)


    # Filtered results
    
    # Modified efficiency graph
    efficiencyMod = ROOT.TEfficiency(LGADHits, MIMOSAHits)
    headTitle = "Efficiency of hit particles in each bin (filtered)"
    fileName = "_eff_mod.pdf"
    #efficiency.GetHistogram().GetZAxis().SetRangeUser(0.9, 1.0)
    produceTH2Plot(efficiencyMod, headTitle, fileName)
    
    
    # Modified inefficiency graph
    inEfficiencyMod = ROOT.TEfficiency(LGADNoHits, MIMOSAHits)
    headTitle = "Inefficiency of hit particles in each bin (filtered)"
    fileName = "_ineff_mod.pdf"
    #inEfficiency.GetHistogram().GetZAxis().SetRangeUser(0.9, 1.0)
    produceTH2Plot(inEfficiencyMod, headTitle, fileName)


    del efficiencyOrig, inEfficiencyOrig, efficiencyMod, inEfficiencyMod, LGADHitsOrig, MIMOSAHitsOrig, LGADNoHitsOrig, LGADHits, MIMOSAHits, LGADNoHits


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
    canvas.Print("../../HGTD_material/plots_hgtd_efficiency_sep_2017/telescope/telescope_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()


def produceTH2Plot(graph, headTitle, fileName):
    
    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "X position (mm)" + "; " + "Y position (mm)"
    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw("COLZ")
    canvas.Update()
    canvas.Print("../../HGTD_material/plots_hgtd_efficiency_sep_2017/telescope/telescope_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()


