#############################################
#                                           #
#                                           #
#         HGTD EFFICIENCY ANALYSIS          #
#                                           #
#                                           #
#############################################

import noise
import noise_plot
import pulse
import pulse_plot
import tracking
import timing
import timing_plot
import metadata
import data_management

# DEBUG #
import timing_double_peak as dp

#metadata.setupATLAS()

def main():
    
    metadata.printTime()
    
    # This is only used for me, for storing the oscilloscope on an external drive
    data_management.setIfOnHDD(True)
    data_management.setIfOnHITACHI(False)
    
    #### Settings used for debugging noise and pulse analysis ####
    metadata.setLimitRunNumbers(0)
    metadata.setEntriesForQuickAnalysis(0)
    #############################################################
    
    # Here select which batches to consider. Example [101, 102, 103].
    # Replace list with string "all" to consider all batches
    # This is automated to used with all methods listed below.
    # If all, then second argument excludes selected batch numbers
    #metadata.setBatchNumbers("all", [101,102,103,104,105,106,107,108,203,204,205,206,207])
    metadata.setBatchNumbers([306])
    ####### METHODS ########
    
    # NOISE AND PULSE ANALYSIS #
    #noise.noiseAnalysis()
    #pulse.pulseAnalysis()
    
    # TIMING RESOLUTION ANALYSIS #
    #timing.timingAnalysis()
    
    # PRODUCE PLOTS #
    #noise_plot.noisePlots()
    #pulse_plot.pulsePlots()
    timing_plot.timingPlots()
    
    # TRACKING ANALYSIS #
    #tracking.trackingAnalysis()
    
    # DEBUG
    #dp.doublePeak()
   
   ####### END OF METHODS ########
   
    metadata.printTime()
    exit()


main()
