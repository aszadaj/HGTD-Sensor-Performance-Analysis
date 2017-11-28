
import analysis
import telescope

def main():

    numberOfRuns = 88 # 88 max,
    step = 30000 # 10000 minimum
    sigma = 8 # At least 8 for acceptable results
    
    numberOfRunsPerBatch = 1 # 12 runs in batch 301
    numberOfBatches = 1
    
    #analysis.startAnalysis(numberOfRuns, step, sigma)
    
    
    telescope.telescopeAnalysis(numberOfRunsPerBatch, numberOfBatches)
    
    exit()


main()
