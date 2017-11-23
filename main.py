
import analysis
import metadata as md
import pulse as ps

def main():

    numberOfRuns = 88 # 88 max
    threads = 4
    step = 10000
    sigma = 8
    sourceFolderPath = "../../HGTD_material/"
    #rootFolderPath = "../../HGTD_material/oscilloscope_data_sep_2017/"
    rootFolderPath = "/Volumes/HDD500"
    
    md.defineFolderPath(sourceFolderPath)
    ps.defineSigmaConstant(sigma)
    
    analysis.startAnalysis(numberOfRuns, threads, step, rootFolderPath)
    
    exit()


main()
