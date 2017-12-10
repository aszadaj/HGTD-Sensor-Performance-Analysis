#############################################
#                                           #
#                                           #
#         HGTD EFFICIENCY ANALYSIS          #
#                                           #
#                                           #
#############################################

import noise
import pulse
import telescope
import timing
import graph

import metadata as md

#md.setupATLAS()

def main():

    ######  NOISE, PULSE, TELESCOPE AND TIMING   ######
    
    batchNumber = [306]   # All batches 38, or "all" to consider them all
    
    ##################################################
    
    ######  GRAPH ONLY   ######
    
    runNumber = 3791
    entries = [10001]
    
    ###########################
    
    #noise.noiseAnalysis            (batchNumber)
    
    #pulse.pulseAnalysis            (batchNumber)
    
    #telescope.telescopeAnalysis     (batchNumber)
    
    timing.timingAnalysis           (batchNumber)
    
    #graph.printWaveform            (runNumber, entries)
    
    exit()


main()

# Log1 09.12.2017
# redefined sigma value after check in the waveforms function
# Program is adapted to receive code in batches and exports them as pickle files
# amplitudes and rise time are large, but not too large.
# New file rise time half maximum is a reference point for

# Log2
# The lowered sigma gives more values but the SiPM have a higher noise and the sigma is
# too low. There fore testing with sigma = 6 for SiPM and sigma=5 for rest of the sensors

# Available batch numbers:
# 101, 102, 103, 104, 105, 106, 107, 108
# 203, 204, 205, 206, 207,
# 301, 302, 303, 304, 305, 306,
# 401, 403, 404, 405, 406,
# 501, 502, 503, 504, 505, 506, 507,
# 701, 702, 703, 704, 705, 706, 707


