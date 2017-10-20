
import ROOT
#import langaus # a C-file which determines landau(*)gauss fit, future project
import numpy as np
import root_numpy as rnm
import json


# The code obtains amplitudes and risetime for pulses for each channel for all selected entries
# and orders them in a nested list within "amplitudes" and "risetime".
def main():
    
    
    data, first_entry, last_entry = importFileData()
    
    print len(data)
    
    exit()




# Prompt for choosing entry and if file is locally or on lxplus
def importFileData():
    
    first_entry = raw_input ("From which entry? (0-220 000) or 'm' as max: ")
    last_entry = 0
    if first_entry != "m":
        last_entry = raw_input ("Until which entry? ("+str(first_entry)+"-220 000) or 'l' as last: ")
        if last_entry == "l":
            last_entry = 200263
    else:
        first_entry = 0
        last_entry = 200263

    dataFileName = "~/cernbox/SH203X/HGTD_material/telescope_data_sep_2017/run003656.processed.root"

    data = rnm.root2array(dataFileName, start=int(first_entry), stop=int(last_entry))

    return data, first_entry, last_entry




############# MAIN #############

main()

################################

