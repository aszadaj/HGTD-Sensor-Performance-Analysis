import ROOT
import metadata as md
import numpy as np

ROOT.gStyle.SetOptFit()

def produceTimingDistributionPlots(time_difference, peak_value):

    canvas = ROOT.TCanvas("Time Difference Distribution", "time_difference")

    time_difference_graph = dict()
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    W4RD01_chan = md.getChannelNameForSensor("W4-RD01")
    
    channels = time_difference.dtype.names
    channels = ["chan4"]
    
    for chan in channels:
        if chan != md.getChannelNameForSensor("SiPM-AFP"):
            
            index = int(chan[-1:])

            time_difference_graph[chan] = ROOT.TH1D("Time Difference channel "+str(index), "time_difference" + chan, 1000, -4, -2)

#            for entry in range(0, len(time_difference[chan])):
#
#                if time_difference[chan][entry] != 0:
#
#                    if md.getNameOfSensor(chan) == "W4-RD01":
#
#                        if peak_value[chan][entry] > 200 and peak_value[SiPM_chan][entry] > 200:
#
#                            time_difference_graph[chan].Fill(time_difference[chan][entry])
#
#                    else:
#                        print "test"
#                        time_difference_graph[chan].Fill(time_difference[chan][entry])

            for entry in range(0, len(time_difference[chan])):

                if time_difference[chan][entry] != 0:
                    time_difference_graph[chan].Fill(time_difference[chan][entry])

            time_difference_graph[chan].Fit("gaus","","", time_difference_graph[chan].GetMean()-0.3, time_difference_graph[chan].GetMean()+0.3)
            
            defineAndProduceHistogram(time_difference_graph[chan], canvas,chan)

    del canvas


# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList, canvas, chan):

    headTitle = "Distribution of timing difference, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"


    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    graphList.SetTitle(headTitle)
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)
