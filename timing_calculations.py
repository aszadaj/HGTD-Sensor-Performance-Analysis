import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import data_management as dm
import timing_plot as t_plot


ROOT.gROOT.SetBatch(True)


def timingAnalysisPerRun(peak_time):

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    time_difference = np.zeros(len(peak_time), dtype = peak_time.dtype)
    
    channels = peak_time.dtype.names

    for chan in channels:

        if chan != SiPM_chan:
            
            for event in range (0, len(peak_time)):

                if peak_time[chan][event] != 0 and peak_time[SiPM_chan][event] != 0:

                    time_difference[chan][event] = peak_time[event][chan] - peak_time[event][SiPM_chan]



    return time_difference

