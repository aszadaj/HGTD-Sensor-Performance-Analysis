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
 
1. Given the run list, these runs with corresponding time stamps have different dataset:

channels w/o chan7
3785    1504944107
3787    1504946329
3788    1504947269
3789    1504948123
3790    1504949018
3791    1504949898
3792    1504950714
3793    1504951486
3794    1504952424
3795    1504953251
3797    1504955229
3798    1504956054
3799    1504956907
3800    1504957873
3801    1504958794
3802    1504959706
3803    1504960732

chan0, chan1, chan3
3889    1505056046
3890    1505057795
3891    1505059124
3893    1505062148
3894    1505063433
3895    1505064756
3896    1505065984
3897    1505067467
3898    1505068982
3899    1505070204
3900    1505071452
3901    1505072697
3902    1505074143
3903    1505075550

chan0, chan1, chan2, chan3
3978    1505232503
3979    1505233734
3980    1505234974
3981    1505236230
3982    1505239044
3999    1505246053
4000    1505246642
4001    1505247000


2. Not all runs are compatible with the code. Apparently corrupted ROOT files or some other reason. These are:
 
3889    1505056046
3890    1505057795
3891    1505059124
3893    1505062148
3894    1505063433
3895    1505064756
3896    1505065984
3897    1505067467
3898    1505068982
3899    1505070204
3900    1505071452
3901    1505072697
3902    1505074143
3903    1505075550

3978    1505232503
3979    1505233734
3980    1505234974
3981    1505236230
3982    1505239044
3999    1505246053
4000    1505246642
4001    1505247000

3. Two run is shorter than expected, run 3738, and 3869


