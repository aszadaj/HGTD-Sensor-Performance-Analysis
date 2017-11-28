
import analysis
import telescope

def main():

    numberOfRuns = 88 # 88 max, that is those which can be run atm
    step = 30000 # 10000 minimum, due to restrictions on criticalValue
    sigma = 8 # At least 8 for acceptable results, related to passing amplitudes
    
    numberOfRunsPerBatch = 15 # Example: 12 runs in batch 301
    numberOfBatches = 3 # For quicker results
    
    analysis.startAnalysis(numberOfRuns, step, sigma)
    telescope.telescopeAnalysis(numberOfRunsPerBatch, numberOfBatches)
    
    exit()


main()
