import ROOT
import numpy as np

#### OSCILLOSCOPE ANALYSIS ####
#
# Without plotting graphs
#
###############################

# Create TFile object from .root-file
# NB! Use the correct file-path
#f = ROOT.TFile("/eos/user/k/kastanas/TB/osci_conv/data_1504818689.tree.root")
f = ROOT.TFile("~/cernbox/oscilloscope_data/data_1504818689.tree.root")

# get the TTree from the TFile
t  = f.Get("oscilloscope")

# Sampling period of the scope
dt = 0.1

# Data points, for each entry, there are 8 channels, with noise points
# E.g. data[0][1][2] is for entry 0, channel 1 and point 2
data = []

# loop over entries
for e in range(0,40000): #t.GetEntries()
    
    data.append([])
    t.GetEntry(e)
    
    # Loop over all channels
    for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
        # Convert ROOT-array to numpy-array and set in mV
        chan_np = np.asarray(chan,'d')*1000
        
        # Selected points which fulfill condition
        points_condition = []
        
        # Put all points until the pulse, that is below 25 mV.
        for point in chan_np:
            if abs(point) < 25:
                points_condition.append(point)
            else:
                break
    
        # Removing three points to make the collection smoother.
        data[e].append(points_condition[:-3])

# maybe remove some points before the pulse?
# are there channels which give two pulses?
# are there differences between the pulses

pedestal = []
bins = 100 # Convention to see a better resolution

histogram = ROOT.TH1D("Histograms","Histograms",1,-1,1)

for entry in data:
    for channel in entry:
            
        # Defining structure of histogram
        min_bin = min(channel)*0.9
        max_bin = max(channel)*1.1
        histogram.SetBins(bins,min_bin,max_bin)
        
        # Sorting the channel-list to use the distribution function
        channel.sort()
        for i in channel:
            histogram.Fill(i)
    
        pedestal.append(histogram.GetMean())


c = ROOT.TCanvas("Distributions", "Distributions") # Dictionary for drawing

# Define attributes for the histogram
min_bin = min(pedestal)*0.9
max_bin = max(pedestal)*1.1
histogram = ROOT.TH1D("Pedestal","Pedestal",bins,min_bin,max_bin)
histogram.SetLineColor(1)
histogram.SetMarkerColor(1)
histogram.GetYaxis().SetTitle("Amount in each bin (N)")
histogram.GetXaxis().SetTitle("Pedestal (mV)")
setTitleAboveGraph = "Pedestal distribution for all entries"
histogram.SetTitle(setTitleAboveGraph)

# Sort and fill TH1D - histogram
pedestal.sort()
for i in pedestal:
    histogram.Fill(i)

# Draw and fit with a Gaus curve
histogram.Draw()
histogram.Fit("gaus")
pedestal_total = histogram.GetMean()
std_pedestal = histogram.GetStdDev()

print "\nThe pedestal value is " + str(pedestal_total) + " mV.\n"

print "\nThe STD value is " + str(std_pedestal) + " mV.\n"

# Export plot as .pdf
file_name = "distribution_pedestal.pdf"
c.Update()
c.Print(file_name)


