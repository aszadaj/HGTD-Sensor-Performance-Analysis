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

#metadata.setupATLAS()

def main():
    
    metadata.printTime()
    
    # This is only used for me, for storing the oscilloscope on an external drive
    data_management.setIfOnHDD(False)
    
    #### Settings used for debugging noise and pulse analysis ####
    metadata.setLimitRunNumbers(0)
    metadata.setEntriesForQuickAnalysis(0)
    ##############################################################
    
    # Here select which batches to consider. Example [101, 102, 103].
    # Replace list with string "all" to consider all batches
    # This is automated to used with all methods listed below.
    metadata.setBatchNumbers([306, 504])
 
    ####### METHODS ########
    
    # NOISE AND PULSE ANALYSIS # (oscilloscope files needed, not provided)
    #noise.noiseAnalysis()
    #pulse.pulseAnalysis()
    
    # TIMING RESOLUTION ANALYSIS # (pulse files needed, provided)
    timing.timingAnalysis()
    
    # PRODUCE PLOTS # (noise, pulse files needed, provided)
    noise_plot.noisePlots()
    pulse_plot.pulsePlots()
    timing_plot.timingPlots()
    
    # TRACKING ANALYSIS # (pulse and tracking files needed, tracking files only for batch 306, 504 and 607)
    tracking.trackingAnalysis()
   
   ####### END OF METHODS ########
   
    metadata.printTime()
    exit()


main()
