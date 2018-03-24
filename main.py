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

import numpy as np
import itertools

#metadata.setupATLAS()

def main():
    
    data_management.printTime()
    
    # This is only used for me, for storing the oscilloscope on an external drive
    data_management.setIfOnHDD(False)
    data_management.setIfOnHITACHI(False)
    
    #### Settings used for debugging noise and pulse analysis ####
    metadata.setLimitRunNumbers(0)
    metadata.setEntriesForQuickAnalysis(0)
    #############################################################
    
    # Here select which batches to consider. Example [101, 102, 103].
    # Replace list with string "all" to consider all batches
    # This is automated to used with all methods listed below.
    # If all, then second argument excludes selected batch numbers
    #metadata.setBatchNumbers("all", [101,102,103,104,105,106,107,108,203,204,205,206,207, 301, 302, 303, 304, 305, 306, 401, 402, 403, 404, 405, 406, 407, 501, 502, 503, 504, 505, 506, 507, 701, 702, 703, 704, 705])
    #metadata.setBatchNumbers("all", [405, 406, 704, 705, 706])
    metadata.setBatchNumbers([108])
    #metadata.setBatchNumbers("all", [101,102,103,104,105,106,107,108,203,204,205,206,207, 301, 302, 303, 304, 305, 306, 401, 402, 403, 404, 405, 406])


    ####### METHODS ########
    
    # NOISE ANALYSIS #
    #noise.noiseAnalysis()
    
    # PULSE ANALYSIS #
    #pulse.pulseAnalysis()
    
    # TRACKING ANALYSIS AND PLOT PRODUCTION#
    tracking.trackingAnalysis()
    
    # TIMING RESOLUTION ANALYSIS #
    #timing.timingAnalysis()
    
    # PRODUCE PLOTS #
    #noise_plot.noisePlots()
    #pulse_plot.pulsePlots()
    #timing_plot.timingPlots()
    
    
    ###### END OF METHODS ########
   
    data_management.printTime()
    exit()




main()






















