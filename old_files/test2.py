import ROOT

# create the TFile object for reading the input file
f = ROOT.TFile("~/data_1504818689.tree.root")

# get the TTree from the TFile
t  = f.Get("oscilloscope")

# create a canvas to draw on
c = ROOT.TCanvas("Noise and Pulse", "Noise and Pulse") # this is what we draw on

# need some spacing in the x-axis for the samples, i.e. the sampling period of the scope
dt = 0.1 # guessing, in ns

# loop over entries
for e in range(5, 10): #t.GetEntries()):
    t.GetEntry(e-1)
    setTitleAboveGraph = "Sep 2017 Run 3656: Oscilloscope data (from 8 channels) - Entry "+ str(e) # To be used later
    
    # loop over the channels and draw them
    channelCounter = 0
    graphs = {} # empty dictionary holding the graph objects if needed later
    legend = {}
    for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
        
        # create a graph for this channel and set its colors
        graphs[channelCounter] = ROOT.TGraph(len(t.chan0))
        
        # Legend
#        legend[channelCounter] = ROOT.TLegend(0.6,0.7,0.85,0.9)
#        graphs[channelCounter].SetName("chan")
#        legend[channelCounter].AddEntry("chan","Ar:CO_{2}(80:20)","p");
#        legend[channelCounter].SetHeader("Channels")
#        legend[channelCounter].Draw()
        graphs[channelCounter].SetLineColor(channelCounter+1)
        graphs[channelCounter].SetMarkerColor(channelCounter+1)
        
        # loop over the sample points and fill the TGraph to see the oscilloscope waveform
        for i in range(0,len(chan)):
            graphs[channelCounter].SetPoint(i, i*dt, chan[i]*1000)
        
        drawOpt = "LP" # draw with Line and Points
        if channelCounter == 0:
            drawOpt += "A" # also draw Axes if first to be drawn
        graphs[channelCounter].Draw(drawOpt)
        graphs[channelCounter].GetYaxis().SetRangeUser(-300, 50)
        graphs[channelCounter].GetYaxis().SetTitle("Voltage (mV)")
        graphs[channelCounter].GetXaxis().SetTitle("Time (ns)")
        graphs[channelCounter].SetTitle(setTitleAboveGraph) # Title above graph
        
        graphs[channelCounter].Draw(drawOpt)
        #print "Drew channel %d" % (channelCounter+1)
        channelCounter += 1

    c.Update()
    c.Print("original_noise_and_pulse/Noise_and_pulse_entry%d.pdf" % e)
    #c.WaitPrimitive()
