
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
    
    runsPerBatch = 7    # Example: 12 runs in batch 301
    batches = 2         # All batches 38
    
    ##################################################
    
    ######  GRAPH ONLY   ######
    
    runNumber = 3656
    entries = [60010]
    
    ###########################
    
    #noise.noiseAnalysis            (runsPerBatch, batches)
    
    pulse.pulseAnalysis             (runsPerBatch, batches)
    
    #telescope.telescopeAnalysis    (runsPerBatch, batches)
    
    #timing.timingAnalysis          (runsPerBatch, batches)
    
    #graph.printWaveform            (runNumber, entries)
    
    exit()


main()


# Available batch numbers:
# 101, 102, 103, 104, 105, 106, 107, 108
# 203, 204, 205, 206, 207,
# 301, 302, 303, 304, 305, 306,
# 401, 403, 404, 405, 406,
# 501, 502, 503, 504, 505, 506, 507,
# 701, 702, 703, 704, 705, 706, 707


