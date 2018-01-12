import ROOT
import metadata as md
import numpy as np

ROOT.gStyle.SetOptFit()

def produceTimingDistributionPlots(time_difference, peak_value, peak_time):
    
    time_difference_graph = dict()
    times_2d = dict()
    time_diff_2d_lgad = dict()
    time_diff_2d_sipm = dict()
    
    canvas = dict()
    canvas_lgad = dict()
    canvas_sipm = dict()
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names
    channels = ["chan4"]
    
    for chan in channels:
        if chan != md.getChannelNameForSensor("SiPM-AFP"):
            
            index = int(chan[-1:])

            time_difference_graph[chan] = ROOT.TH1D("Time Difference channel "+str(index), "time_difference" + chan, 1000, -4, -2)
            times_2d[chan] = ROOT.TH2F("telescope_"+chan,"Times channel "+str(int(chan[-1:])+1),500,-14,0,500,5,80)
            time_diff_2d_lgad[chan] = ROOT.TH2F("telescope_1"+chan,"Time difference, lgad channel "+str(int(chan[-1:])+1), 500,-18,3,500,-50,500)
            time_diff_2d_sipm[chan] = ROOT.TH2F("telescope_2"+chan,"Time diffence, sipm channel "+str(int(chan[-1:])+1),500,-18,3,500,-50,500)
            
            canvas[chan] = ROOT.TCanvas("Telescope"+chan, "telescope")
            canvas_lgad[chan] = ROOT.TCanvas("Telescope2"+chan, "telescope")
            canvas_sipm[chan] = ROOT.TCanvas("Telescope3"+chan, "telescope")

            for entry in range(0, len(time_difference[chan])):

                if time_difference[chan][entry] != 0:
                    time_difference_graph[chan].Fill(time_difference[chan][entry])

                if peak_time[chan][entry] != 0 and peak_time[SiPM_chan][entry] != 0:
                    
                    times_2d[chan].Fill(time_difference[chan][entry], peak_time[chan][entry], 1)
                    
                    time_diff_2d_lgad[chan].Fill(time_difference[chan][entry], peak_value[chan][entry], 1)
               
                    time_diff_2d_sipm[chan].Fill(time_difference[chan][entry], peak_value[SiPM_chan][entry], 1)

            time_difference_graph[chan].Fit("gaus","","", time_difference_graph[chan].GetMean()-0.3, time_difference_graph[chan].GetMean()+0.3)
            
            produceTH1Plot(time_difference_graph[chan], canvas[chan], chan)

            headTitle = "Time difference vs time position 2D plot "
            fileName = ".pdf"
            produceTH2Plot(times_2d[chan], headTitle, fileName, chan, canvas[chan], 1)
    
            headTitle = "Time difference LGAD 2d plot "
            fileName = ".pdf"
            produceTH2Plot(time_diff_2d_sipm[chan], headTitle, fileName, chan, canvas_lgad[chan], 2)

            headTitle = "Time difference SIPM 2d plot "
            fileName = ".pdf"
            produceTH2Plot(time_diff_2d_lgad[chan], headTitle, fileName, chan, canvas_sipm[chan], 3)


# Produce TH1 plots and export them as a PDF file
def produceTH1Plot(graphList, canvas, chan):

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


def produceTH2Plot(graph, headTitle, fileName, chan, canvas, num):

    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "\Delta t_{LGAD-SIPM} (ns)" + "; " + "t_{SiPM} (ns)"

    if num == 2:
        title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "\Delta t_{LGAD-SIPM} (ns)" + "; " + "SiPM Amplitude (mV)"
    
    elif num == 3:
        title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "\Delta t_{LGAD-SIPM} (ns)" + "; " + "LGAD Amplitude (mV)"

    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw("COLZ")
    canvas.Update()
    
    if num == 2:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_diff_sipm_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    elif num == 3:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_diff_lgad_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    else:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)

    canvas.Clear()
