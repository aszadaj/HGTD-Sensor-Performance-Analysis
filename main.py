from pulse import *
from noise import *
from debugFunctions import *


def main():
    
    runInfo = getRunInfo()
    
    runInfo = selectRuns(runInfo)
    
    #main_debugFunctions(runInfo)

    main_noise(runInfo)

    main_pulse(runInfo)

    exit()


# Generates which runs are considered located in runlist.csv with corresponding time stamps.
def getRunInfo():
    
    fileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/runlist.csv"
    df = pd.read_csv(fileName, header=None, sep="\t")
    
    runInfo = dict()
    
    for index in range(0,len(df)):
        runInfo[df.iloc[index,0]] = df.iloc[index,1]
   
    return runInfo

def selectRuns(runInfo):

    selectedRuns = [3656,3657,3658]

    selectedRunInfo = dict()

    for key in selectedRuns:
        selectedRunInfo[key] = runInfo[key]

    return selectedRunInfo

main()
