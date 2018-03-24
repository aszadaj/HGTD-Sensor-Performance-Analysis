import numpy as np
import metadata as md

def timingAnalysisPerRun(peak_time):
    
    time_difference = np.zeros(len(peak_time), dtype = peak_time.dtype)
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    for chan in peak_time.dtype.names:

        if chan != SiPM_chan:
            
            for event in range (0, len(peak_time)):
                if peak_time[SiPM_chan][event] != 0 and peak_time[chan][event] != 0:
                    
                    # This is for the case if the SiPM is in the same oscilloscope as the DUT
                    time_difference[chan][event] = peak_time[event][chan] - peak_time[event][SiPM_chan]


    return time_difference


# This is used to produce ROOT files which have multiple solutions
def timingAnalysisPerRunSysEq(peak_time):
    
    dt = (  [('chan0',  '<f8', 3), ('chan1',  '<f8', 3) ,('chan2',  '<f8', 3) ,('chan3',  '<f8', 3) ,('chan4',  '<f8', 3) ,('chan5',  '<f8', 3) ,('chan6',  '<f8', 3) ,('chan7',  '<f8', 3)] )
    
    time_difference = np.zeros(len(peak_time), dtype = dt)

    osc1 = ["chan0", "chan1", "chan2", "chan3"]
    osc2 = ["chan4", "chan5", "chan6", "chan7"]
    
    if int(md.getBatchNumber()/100) == 3:
        osc2 = ["chan4", "chan5", "chan6"]
    
    oscilloscope_chan = [osc1, osc2]
    
    for channels_part in oscilloscope_chan:
        for chan in channels_part:
        
            chan2_list = list(channels_part)
            chan2_list.remove(chan)
            
            for event in range(0, len(peak_time[chan])):
                
                time_difference[chan][event] = np.zeros(3)
                
                for index in range(0, len(chan2_list)):
                    chan2 = chan2_list[index]
                    if peak_time[chan][event] != 0 and peak_time[chan2][event] != 0:
                       
                        value = (peak_time[chan][event] - peak_time[chan2][event])*1000
                        time_difference[chan][event][index] = value


    return time_difference

# Solve system of linear equation
# Note, there are multiple to choose from, 4 unknowns, 6 different equations, not all are independent
def solveLinearEq(sigmas_mix):

    vector_1 = [1, 1, 0, 0]
    vector_2 = [1, 0, 1, 0]
    vector_3 = [1, 0, 0, 1]
    vector_4 = [0, 1, 1, 0]
    vector_5 = [0, 1, 0, 1]
    vector_6 = [0, 0, 1, 1]


    pos_vec = [vector_1, vector_2, vector_3, vector_4, vector_5, vector_6]

    for subset in itertools.combinations(pos_vec, 4):
        matrix = np.matrix(subset)
        try:
            inverse = np.linalg.inv(matrix)
        except:
            continue
    
    # Non-singular matrix selected
    matrix = np.matrix([[1, 0, 0, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 0, 1]])
    inverse = np.linalg.inv(matrix)
    vector = np.array([sigmas_mix[0][3], sigmas_mix[1][2], sigmas_mix[2][3], sigmas_mix[1][3]])
    vector = np.power(vector, 2)
    solution = inverse.dot(vector)
    sigma_chan = np.sqrt(solution)


    return sigma_chan
