
import ROOT
import numpy as np
import root_numpy as rnm
import json
import pickle


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
    
    amplitude, risetime, channels = importInfo()
    
    for chan in channels:
        print chan
        for index in range(0,len(amplitude[chan])):
            if amplitude[chan][index] != 0:
                print str(index) + ": " + str(amplitude[chan][index])
        print "\n"
    
    exit()



def importInfo():
    amplitude = ""
    risetime = ""
    with open("amplitude_risetime.pkl","rb") as input:
        amplitude = pickle.load(input)
        risetime = pickle.load(input)
        channels = pickle.load(input)

    return amplitude, risetime, channels

############# MAIN #############

main()

################################

