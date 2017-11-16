
import ROOT
import numpy as np
import root_numpy as rnm
import pickle



##########################################
#                                        #
#                                        #
#              FUNCTIONS                 #
#                                        #
#                                        #
##########################################


# Define the code to make the analysis
def produceTelescopeGraphs(amplitude, data, runNumber):

    canvas = ROOT.TCanvas("TProfile2D","TProfile2D")
    telescope_graph = dict()

    channels = amplitude.dtype.names
    
    for chan in channels:
    
        telescope_graph[chan] = ROOT.TProfile2D("telescope_"+chan,"Telescope "+chan,100,-6000,7200,100,6000,15300)
        
        for index in range(0,len(data)):
            if data['X'][index] != -9999 and amplitude[chan][index] > 0:
                telescope_graph[chan].Fill(data['X'][index], data['Y'][index], amplitude[chan][index])

        canvas.cd()
        telescope_graph[chan].Draw("COLZ")
        canvas.Update()
        filename = "plot_telescope/telescope_"+str(runNumber)+"_"+str(chan)+".pdf"
        canvas.Print(filename)

