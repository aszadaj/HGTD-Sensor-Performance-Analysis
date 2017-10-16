import ROOT
import numpy as np

#### OSCILLOSCOPE ANALYSIS ######
#                               #
#   Without plotting graphs     #
#                               #
#################################


f = ROOT.TFile("~/cernbox/oscilloscope_data/data_1504818689.tree.root")

# get the TTree from the TFile
t  = f.Get("oscilloscope")

# Sampling period of the scope
dt = 0.1

# Data points, for each entry, there are 8 channels, with noise points
# E.g. data[0][1] is the noise data for entry 0, channel 1
data = []
entries = 10 #t.GetEntries()
# loop over entries

c_waveforms = ROOT.TCanvas("Waveforms", "Waveforms")
for e in range(0,entries):
    
    data.append([])
    t.GetEntry(e)
    
    ####################
    channelCounter = 0
    graphs = {}
    ####################
    
    # Loop over all channels
    for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
        # Convert ROOT-array to numpy-array and set in mV
        chan_np = np.asarray(chan,'d')*1000 #work in numpy lists
        
        # Selected points which fulfill condition
        points_condition = []
        
        # Put all points until the pulse, that is below 25 mV.
        
        for point in chan_np:
            if abs(point) < 25:
                points_condition.append(point)
            else:
                break
    
        # check per entry pedestal values if they change
    
        # Removing three points to make the collection smoother, could be a problem
        data[e].append(points_condition[:-3])
        
################### PRINT TGRAPH ###########################

        # create a graph for this channel and set its colors
        graphs[channelCounter] = ROOT.TGraph(len(data[e][channelCounter]))
        graphs[channelCounter].SetLineColor(channelCounter+1)
        graphs[channelCounter].SetMarkerColor(channelCounter+1)

        # loop over the sample points and fill the TGraph to see the oscilloscope waveform
        for i in range(0,len(data[e][channelCounter])):
            graphs[channelCounter].SetPoint(i, i*dt, data[e][channelCounter][i])
        
        drawOpt = "LP" # draw with Line and Points
        if channelCounter == 0:
            drawOpt += "A" # also draw Axes if first to be drawn
        graphs[channelCounter].Draw(drawOpt)
        graphs[channelCounter].GetYaxis().SetRangeUser(-300, 50)
        graphs[channelCounter].Draw(drawOpt)
        channelCounter += 1
    c_waveforms.Update()
    c_waveforms.Print("check_antek/Waveforms_entry%d.pdf" % e)

########################################################

pedestal = [[] for _ in range(8)]
bins = 100 # Convention to see a better resolution

histogram = ROOT.TH1D("Histograms","Histograms",100,-1,1)

for entry in data:
    channelCounter = 0
    for channel in entry:
            
        # Defining structure of histogram
        min_bin = min(channel)*0.9
        max_bin = max(channel)*1.1
        histogram.SetBins(bins,min_bin,max_bin)

        # Sorting the channel-list to use the distribution function
        channel.sort()
        for i in channel:
            histogram.Fill(i)
        
        pedestal[channelCounter].append(histogram.GetMean())
        histogram.Reset("ICE")
        channelCounter += 1


c = ROOT.TCanvas("Pedestal per Channel", "Pedestal per Channel") # Dictionary for drawing
histogram = ROOT.TH1D("Pedestal","Pedestal",1,-1,1)
bins = 100 # Convention to see a better resolution
channelCounter = 0
for channel in pedestal:

    # Define attributes for the histogram
    min_bin = -0.7
    max_bin = -0.65
    histogram = ROOT.TH1D("Pedestal","Pedestal",bins,min_bin,max_bin)
    histogram.SetLineColor(1)
    histogram.SetMarkerColor(1)
    histogram.GetYaxis().SetTitle("Amount in each bin (N)")
    histogram.GetXaxis().SetTitle("Pedestal (mV)")
    setTitleAboveGraph = "Pedestal distribution for channel " + str(channelCounter+1)
    histogram.SetTitle(setTitleAboveGraph)

    # Sort and fill TH1D - histogram
    channel.sort()
    for i in channel:
        histogram.Fill(i)

    # Draw and fit with a Gauss curve
    histogram.Draw()
    histogram.Fit("gaus")
# check Fit in ROOT documentation for more variables
    pedestal_per_channel = histogram.GetMean()
    pedestal_std_channel = histogram.GetStdDev()

    print "\nThe pedestal for channel " + str(channelCounter+1) +" is " + str(pedestal_per_channel) + " mV.\n"

    print "\nThe STD value for channel " + str(channelCounter+1) + " is " + str(pedestal_per_channel) + " mV.\n"

    # Export plot as .pdf
    file_name = "pedestal_per_channel_antek/distribution_pedestal_"+str(channelCounter+1)+".pdf"
    c.Update()
    c.Print(file_name)
    channelCounter += 1

# Idea: export the data to not make it multiple times.


