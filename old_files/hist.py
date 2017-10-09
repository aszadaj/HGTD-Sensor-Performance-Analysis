import ROOT
import numpy as np
import root_numpy as rn

# create the TFile object for reading the input file
# information regarding timestep, number of elements etc is in the metadata!

f = ROOT.TFile("~/data_1504818689.tree.root")

# get the TTree from the TFile, the name can be found by runnning in bash
# > root data_1504818689.tree.root
# from there, open up TBrowser
# > TBrowser a
# Inside, locate the root file, open it and the first characters are the name

t  = f.Get("oscilloscope") # Consists of eight channels

# get the first entry
t.GetEntry(0)

# Time scope, defined in the metadata
dt = 0.1

# loop over the channels and draw them
c = {}
 # this is what we draw on

channelCounter = 0
graphs = {} # empty dictionary holding the graph objects if needed later, used only in the code for ROOT to access it and print out in the PDF.

#for chan in [t.chan0,t.chan1, t.chan2,t.chan3,t.chan4,t.chan5,t.chan6,t.chan7]:
for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5,]:
    
    s1 = "Histogram" + str(channelCounter+1)
    c[channelCounter] = ROOT.TCanvas(s1, s1)
    chan = np.asarray(chan,'d')
    chan.sort()
    graphs[channelCounter] = ROOT.TH1D("hist","Histogram",80,min(chan)*0.9,max(chan)*1.1)
    graphs[channelCounter].SetLineColor(channelCounter+1)
    graphs[channelCounter].SetMarkerColor(channelCounter+1)
    
    for i in chan:
        graphs[channelCounter].Fill(i)
    
    graphs[channelCounter].Draw()
    s2 = "hist/" + s1 + ".pdf"
    c[channelCounter].Print(s2)
    c[channelCounter].Update()

    channelCounter += 1

#####################################
#
# Next to do: Check how to draw a linear
# graph and try to fit it with a gaussian
#
#
#####################################





