# HGTD Efficiency Analysis



# Overall info

 ```main.py```

The code runs  ```noise.py```,  ```pulse.py``` and  ```telescope.py``` in order to make the analysis of efficiencies of sensors tested in test beam experiment in September 2017. The code receives an input ROOT file, structured in TTree with eight channels, chan0 to chan7 where each of the four channels represent two oscilloscopes. The ROOT file is data collected from the two oscilloscopes which represents a run number and batch number, enlisted in  ```resources/run_list_tb_sep_2017.csv``` which has been modified to the original HGTD Runlist September 2017, which is available here (not providing explicit link to Google Drive, for security reasons).

```https://twiki.cern.ch/twiki/bin/view/LAr/HGTDTBSensorsSep17```

The output is in form of distribution plots for  ```noise```,  ```pulse``` and  ```telescope```  as well as obtained data
information in ```pickle_files``` which can be used for future reference.



# Noise analysis

 ```noise.py``` and ```noise_plot.py```
 
 The code searches for noise level and pedestal level among all entries in selected files. The output is in form of distribution
 plots and exported pedestal and noise values for each channel among all entries for each run number.
 
 
 
# Pulse analysis

 ```pulse.py``` and  ```pulse_plot.py```

The code calculates the maximal amplitude value for found pulses and also calculates the rise time. Using the noise level and pedestal, the code is adapted to introduce a ```sigma```-value which is conventionally set to ```sigma=10``` which identifies a pulse above the noise level. This is then exported as a data file and distribution plots for each run number





# Telescope analysis

 ```telescope.py``` and  ```telescope_plot.py```
 
 

