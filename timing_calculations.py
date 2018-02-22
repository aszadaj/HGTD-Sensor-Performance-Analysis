import numpy as np
import metadata as md

def timingAnalysisPerRun(peak_time, peak_value):
    
    time_difference = np.zeros(len(peak_time), dtype = peak_time.dtype)
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    for chan in peak_time.dtype.names:

        if chan != SiPM_chan:
            
            for event in range (0, len(peak_time)):
                if peak_time[SiPM_chan][event] != 0 and peak_time[chan][event] != 0:
                
                    time_difference[chan][event] = peak_time[event][chan] - peak_time[event][SiPM_chan]


    return time_difference
