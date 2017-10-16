import ROOT
import numpy as np
import root_numpy as rnm
#import multiprocessing

data = rnm.root2array("~/cernbox/oscilloscope_data/data_1504818689.tree.root",stop=10, )

channels = data.dtype.names

pedestals = dict()
noise = dict()

for channel in channels:
    pedestals[channel] = ROOT.TH1D("pedestal"+channel,"Pedestal "+channel,100,-5,5)
    noise[channel] = ROOT.TH1D("noise"+channel,"Noise "+channel,100,0,10)

for event in data:
    channelCounter = 0
    #print data.dtype.names # prints the name of the data types
    for chan in channels:
        #print np.sum(abs(event[chan])<25*0.001) #no of elements for the condition
        # Select elements below
        pulse_compatible_samples = event[chan]<-25*0.001
        max_index = np.where(pulse_compatible_samples)[0][0] - 3 if len( np.where(pulse_compatible_samples)[0] ) else 1002
        chan_average = np.average(event[chan][0:max_index])*1000
        chan_std = np.std(event[chan][0:max_index])*1000
        pedestals[chan].Fill(chan_average)
        noise[chan].Fill(chan_std)
    

# The check is done, that the same data is being analysed as in noise_antek.py

canvas = ROOT.TCanvas("Pedestal per Channel", "Pedestal per Channel")
canvas2 = ROOT.TCanvas("Noise per Channel", "Noise per Channel")
for chan in channels:
    canvas.cd()
    pedestals[chan].Draw()
    canvas2.cd()
    noise[chan].Draw()
    canvas.Update()
    canvas2.Update()
    file_name = "pedestal_per_channel_alex/distribution_pedestal_"+chan+".pdf"
    canvas.Print(file_name)
    file_name2 = "pedestal_per_channel_alex/distribution_noise_"+chan+".pdf"
#canvas2.Print(file_name2)


