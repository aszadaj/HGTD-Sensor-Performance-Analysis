# Noise analysis from oscilloscope data

For now, there are two files which are being under test, one file which Alex created and the other one of me:
```noise_alex.py```
```noise_antek.py```
both of them reads a ROOT file (just one to begin with) and determines the pedestal and the noise which are shown as distributions for each channel (for all entries), these are put in the folder ```pedestal_per_channel_alex``` and   ```pedestal_per_channel_antek``` .

Both files produces different distribution plots. For this reason a test of plotting waveforms is done, which plots the noises for all channels in one plot, for ten entries , and the results of those are put in the folder ```check_alex``` and   ```check_antek```, to compare if the results are the same.

Folder  ```Waveform - Original``` contain graphs for all channels with pulses, for the purpose to compare if nothing is wrong.

Folder  ```old_files``` are saved code which has been modified since before.
