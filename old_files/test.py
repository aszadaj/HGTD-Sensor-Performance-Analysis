import ROOT
# create the TFile object for reading the input file, one on lxplus, the other is local
#f = ROOT.TFile("/eos/user/k/kastanas/TB/osci_conv/data_1504818689.tree.root")
f = ROOT.TFile("~/data_1504818689.tree.root")

# get the TTree from the TFile
t  = f.Get("oscilloscope")

# get the first entry, have to get it.
t.GetEntry(0)

# check the length of the vector for channel 0
len(t.chan0)

# need some spacing in the x-axis for the samples, i.e. the sampling period of the scope
dt = 0.1

# loop over the channels and draw them

c = ROOT.TCanvas("Waveforms", "Waveforms") # this is what we draw on

channelCounter = 0
graphs = {} # empty dictionary holding the graph objects if needed later
    #for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
for chan in [t.chan1]:

    # create a graph for this channel and set its colors
    graphs[channelCounter] = ROOT.TGraph(len(t.chan0))
    graphs[channelCounter].SetLineColor(channelCounter+1)
    graphs[channelCounter].SetMarkerColor(channelCounter+1)

    # loop over the sample points and fill the TGraph to see the oscilloscope waveform
    for i in range(0,len(chan)):
        graphs[channelCounter].SetPoint(i, i*dt, chan[i])

    drawOpt = "LP" # draw with Line and Points
    if channelCounter == 0:
        drawOpt += "A" # also draw Axes if first to be drawn
    graphs[channelCounter].Draw(drawOpt)
    graphs[channelCounter].GetYaxis().SetRangeUser(-0.05, 0.05)
    graphs[channelCounter].Draw(drawOpt)
    #print "Drew channel %d" % (channelCounter+1)
    channelCounter += 1

c.Update()
c.Print("test/Waveforms.pdf")
