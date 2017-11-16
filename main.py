
from pulse import *
from noise import *
from noise_plot import *
from pulse_plot import *


def main():
    
    runInfo = getRunInfo()
    selectedRuns = [3657,3658,3659,3660] # batch 101 for now
    runInfo = selectRuns(runInfo, selectedRuns)
    final_entry = raw_input ("Until which entry? m = max: ")
    
    for runNumber in runInfo.keys():
        analyseFileForRunNumber(runNumber, runInfo[runNumber], final_entry)
        print "Done with run " + str(runNumber)
    
    exit()


# Perform noise and pulse analysis
def analyseFileForRunNumber(runNumber, timeStamp, final_entry):
    
    print "Importing file for run number " + str(runNumber) + " ... "
    data, sensors = importOscilloscopeData(timeStamp,final_entry)

    noise_average = noise_std = amplitudes = risetimes = small_amplitudes = np.zeros(0, dtype = data.dtype)

    step = 1000
    
    # Noise
    print "Done importing file. Start noise analysis."
    noiseAnalysisPerFile(data, step, runNumber, noise_average, noise_std)
    
    # Pulse
    print "Done with noise analysis. Start pulse analysis."
    pulseAnalysisPerFile(data, step, runNumber, timeStamp, sensors, amplitudes, risetimes, small_amplitudes)


# Noise analysis in chunks
def noiseAnalysisPerFile(data, step, runNumber, noise_average, noise_std):

    for chunk in range(0, len(data), step):
    
        noise_average_chunk, noise_std_chunk = noiseAnalysisPerFilePerChunk(data[chunk:chunk+step])
        
        noise_average = np.append(noise_average, noise_average_chunk)
        noise_std = np.append(noise_std, noise_std_chunk)
    
    
    pedestal, noise = getPedestalNoiseValuePerChannel(noise_average, noise_std)
    
    produceNoiseDistributionPlots(noise_average, noise_std, runNumber)
    exportNoiseInfo(pedestal, noise, runNumber)


# Pulse analysis in chunks
def pulseAnalysisPerFile(data, step, runNumber, timeStamp, sensors, amplitudes, risetimes, small_amplitudes):

    pedestal, noise = importNoiseProperties(runNumber)
    timeScope = getTimeScope(timeStamp)

    for chunk in range(0, len(data), step):
    
        amplitudes_chunk, risetimes_chunk, small_amplitudes_chunk = pulseAnalysisPerFilePerChunk(runNumber, timeStamp, data[chunk:chunk+step], timeScope, pedestal, noise)
   
        amplitudes = np.append(amplitudes,amplitudes_chunk)
        risetimes = np.append(risetimes, risetimes_chunk)
        small_amplitudes = np.append(small_amplitudes, small_amplitudes_chunk)
    
    
    amplitudes, risetimes, criticalValues = stripUnwantedAmplitudesRiseTimes(data, amplitudes, risetimes, noise)
    
    producePulseDistributionPlots(amplitudes, risetimes, sensors, pedestal, runNumber, timeStamp, small_amplitudes)
    exportPulseInfo(amplitudes, risetimes, small_amplitudes, criticalValues, runNumber)
    
    print "Number of small amplitudes: " + str(np.count_nonzero(small_amplitudes))


# Function which removes amplitudes which are in the range being critical amplitude values
def stripUnwantedAmplitudesRiseTimes(data, amplitudes, risetimes, noise):
    criticalValues = findCriticalValues(data)
    
    for chan in amplitudes.dtype.names:
        
        indices = amplitudes[chan] > criticalValues[chan]*0.95
        amplitudes[chan][indices] = 0
        risetimes[chan][indices] = 0
        
        indices = amplitudes[chan] < noise[chan]*10
        amplitudes[chan][indices] = 0

    return amplitudes, risetimes, criticalValues


# Calculates pedestal and noise mean values per channel for all entries
def getPedestalNoiseValuePerChannel(noise_average, noise_std):

    pedestal = dict()
    noise = dict()

    for chan in noise_average.dtype.names:
        pedestal[chan] = np.mean(noise_average[chan])
        noise[chan] = np.mean(noise_std[chan])
    
    return pedestal, noise


# Search for critical amplitude values
def findCriticalValues(data):
    
    channels = data.dtype.names
    criticalValues = dict()
    
    for chan in channels:
        criticalValues[chan] = 0
    
    for chan in channels:
        for entry in range(0,len(data)):
            if criticalValues[chan] < np.amax(data[chan][entry]):
                criticalValues[chan] = np.amax(data[chan][entry])

    return criticalValues


# Import data file,  all entries
def importOscilloscopeData(timeStamp, final_entry):

    dataFileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_"+str(timeStamp)+".tree.root"
   
    # Future issue, to fix names from metadata
    sensors = ["W9-LGA35","50D-GBGR2","W4-LG12","SiPM-AFP","W4-S215","W4-S215","W4-S215","W4-S215"]
    
    if final_entry == "m":
        data = rnm.root2array(dataFileName)
    else:
        data = rnm.root2array(dataFileName, start=0, stop=int(final_entry))

    # Invert minus sign and change from V to mV
    for chan in data.dtype.names:
        data[chan] = np.multiply(data[chan],-1000)

    return data, sensors


# Generates which runs are considered located in runlist.csv with corresponding time stamps.
def getRunInfo():
    
    fileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/runlist.csv"
    df = pd.read_csv(fileName, header=None, sep="\t")
    
    runInfo = dict()
    
    for index in range(0,len(df)):
        runInfo[df.iloc[index,0]] = df.iloc[index,1]
   
    return runInfo


# Choose run numbers with corresponding time stamp to be run
def selectRuns(runInfo, selectedRuns):

    selectedRunInfo = dict()

    for key in selectedRuns:
        selectedRunInfo[key] = runInfo[key]

    return selectedRunInfo


# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importNoiseProperties(runNumber):
    
    pedestal = ""
    fileName = "/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pedestal_"+str(runNumber)+".pkl"
    
    with open(fileName,"rb") as input:
        pedestal = pickle.load(input)
        noise = pickle.load(input)

    return pedestal, noise

# Obtain time scope from metadata for selected run number
def getTimeScope(timeStamp):

    fileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/data_" + str(timeStamp) + str(".csv")
    matrix = pd.read_csv(fileName, header=None)
    timeScope = matrix.iloc[0,4]
    
    return timeScope*1000000000


# Export pedestal info (noise analysis)
def exportNoiseInfo(pedestal, noise, runNumber):
    
    fileName = "/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pedestal_"+str(runNumber)+".pkl"
    with open(fileName,"wb") as output:
        pickle.dump(pedestal,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(noise,output,pickle.HIGHEST_PROTOCOL)


# Export dictionaries amplitude and risetime and list of channels in a .pkl file
def exportPulseInfo(amplitude,risetime,small_amplitudes,criticalValues,runNumber):
    
    with open("/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pulse_info_"+str(runNumber)+".pkl","wb") as output:
        
        pickle.dump(amplitude,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(risetime,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(small_amplitudes,output,pickle.HIGHEST_PROTOCOL)
        pickle.dump(criticalValues,output,pickle.HIGHEST_PROTOCOL)


########## MAIN ###########

main()

