# HGTD Efficiency Analysis



# Overall info

 ```main.py```

The code runs  ```noise.py```,  ```pulse.py``` and  ```telescope.py``` in order to make the analysis of efficiencies
of sensors tested in test beam experiment in September 2017. The code receives an input ROOT file, structured in TTree
with eight channels, chan0 to chan7 where each of the four channels represent two oscilloscopes. The ROOT file is data
collected from the two oscilloscopes which represents a run number and batch number, enlisted in
```resources/run_list_tb_sep_2017.csv``` which has been modified to the original HGTD Runlist September 2017,
which is available here (not providing explicit link to Google Drive, for security reasons).


```https://twiki.cern.ch/twiki/bin/view/LAr/HGTDTBSensorsSep17```


The output is in form of distribution plots for  ```noise```,  ```pulse``` and  ```telescope```  as well as obtained data
information in ```pickle_files``` which can be used for future reference.


# Analysis

 ```analysis.py```
 
This takes care of all the run files which are part of the HGTD TB September 2017 experiment. The code selects runs which
are not done and runs noise and pulse analysis. 



# Noise analysis

 ```noise.py``` and ```noise_plot.py```
 
 The code searches for noise level and pedestal level among all entries in selected files. The output is in form of distribution
 plots and exported pedestal and noise values for each channel among all entries for each run number.
 
 
 
# Pulse analysis

 ```pulse.py``` and  ```pulse_plot.py```

The code calculates the maximal amplitude value for found pulses and also calculates the rise time. Using the noise level and
pedestal, the code is adapted to introduce a ```sigma```-value which is conventionally set to ```sigma=10``` which identifies
a pulse above the noise level. This is then exported as a data file and distribution plots for each run number.




# Telescope analysis

 ```telescope.py``` and  ```telescope_plot.py```
 
 Given the the found amplitudes the code uses the data recorded from the MIMOSA-s and notes where the hitting is.
 
 
# Comments

0. Runs with corresponding time stamps which cannot be converted using combinedNTuple.C

Run 3691, timestamp: 1504853409
Run 3693, timestamp: 1504854923
Run 3697, timestamp: 1504863572

Run 3889, timestamp: 1505056046
Run 3890, timestamp: 1505057795
Run 3891, timestamp: 1505059124
Run 3892, timestamp: 1505060526
Run 3893, timestamp: 1505062148
Run 3894, timestamp: 1505063433
Run 3895, timestamp: 1505064756
Run 3896, timestamp: 1505065984
Run 3897, timestamp: 1505067467
Run 3898, timestamp: 1505068982

Run 3978, timestamp: 1505232503
Run 3979, timestamp: 1505233734
Run 3980, timestamp: 1505234974
Run 3981, timestamp: 1505236230

Run 3999, timestamp: 1505246053
Run 4000, timestamp: 1505246642
Run 4001, timestamp: 1505247000

yellow marked in Run Log


Runs which cannot be converted with the analysis program

3919 (exported files can be corrupted, check this)




