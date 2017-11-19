# HGTD Efficiency Analysis



# Noise analysis

 ```noise.py``` and ```noise_plot.py```
 
The input file is a ROOT file with a chosen timestamp for a specific run in TB 2017. The code translates
the scilloscope data, to obtain noise and analyse impulses. To do so, the code calculates the distributions
in each channel for all entries. The data points are selected in such way to have information only until
each pulse for each entry. The output of this code is in form of plots for each channel (all entries) with
a histogram for mean values from each entry, to see how they change over each entry and have value
for each channel's pedestal. This also creates distribution plots of mean noise value for all entries in the
file as well as creating a distribution plot for standard deviation values (here noise).

Reads a ROOT file organized in TTree with leafs with 8 channels, labeled tchan0, tchan 1,...,tchan7


# Pulse analysis

 ```pulse.py``` and  ```pulse_plot.py```




# Telescope analysis

 ```telescope.py``` and  ```telescope_plot.py```

