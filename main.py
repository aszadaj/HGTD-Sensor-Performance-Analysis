
import noise
import pulse
import telescope
import timing
import graph

def main():

    numberOfRuns = 10 # /Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/plots/timing/timing_101_chan0.pdf88 max, that is those which can be run atm
    step = 8000 # 10000 minimum, due to restrictions on criticalValue
    sigma = 7 # At least 8 for acceptable results, related to passing amplitudes
    
    numberOfRunsPerBatch = 20 # Example: 12 runs in batch 301
    numberOfBatches = 3 # For quicker results, all batches: 38
    
    runNumber = 3656
    entry = 156400
    channel = "chan0"
    
    #noise.noiseAnalysis(numberOfRuns, step)
    #pulse.pulseAnalysis(numberOfRuns, step, sigma)
    #telescope.telescopeAnalysis(numberOfRunsPerBatch, numberOfBatches)
    timing.timingAnalysis(numberOfRunsPerBatch, numberOfBatches)
    #graph.printWaveform(runNumber, entry, channel)
    
    exit()


main()

# Available batch numbers:
# 101, 102, 103, 104, 105, 106, 107, 108
# 203, 204, 205, 206, 207,
# 301, 302, 303, 304, 305, 306,
# 401, 403, 404, 405, 406,
# 501, 502, 503, 504, 505, 506, 507,
# 701, 702, 703, 704, 705, 706, 707


