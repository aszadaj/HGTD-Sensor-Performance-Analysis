
import noise
import pulse
import telescope
import timing
import graph
import metadata as md

#md.setupATLAS()

def main():

    ######  NOISE AND PULSE ######
    numberOfRuns = 2    # 88 max, that is those which can be run atm
    step = 5000         # Amount of entries for each thread (multiprocessing)
    entries = "all"     # 'all' or number of entries to be considered
    sigma = 8           # At least 8 for acceptable results, related to passing amplitudes
    
    ######  TELESCOPE AND TIMING   ######
    numberOfRunsPerBatch = 1    # Example: 12 runs in batch 301
    numberOfBatches = 1         # For quicker results, all batches: 38
    
    ######  GRAPH   ######
    runNumber = 3656
    entries = [60010]
    
    #entries=[60010,60035,60042,60044,60052,60069,60082,60090,60102,60113,60135,60147,60635]
    
    #noise.noiseAnalysis(numberOfRuns, step)
    
    pulse.pulseAnalysis(numberOfRuns, step, sigma)
    
    #telescope.telescopeAnalysis(numberOfRunsPerBatch, numberOfBatches)
    
    #timing.timingAnalysis(numberOfRunsPerBatch, numberOfBatches)
    
    #graph.printWaveform(runNumber, entries)
    
    
    exit()


main()

# Available batch numbers:
# 101, 102, 103, 104, 105, 106, 107, 108
# 203, 204, 205, 206, 207,
# 301, 302, 303, 304, 305, 306,
# 401, 403, 404, 405, 406,
# 501, 502, 503, 504, 505, 506, 507,
# 701, 702, 703, 704, 705, 706, 707


