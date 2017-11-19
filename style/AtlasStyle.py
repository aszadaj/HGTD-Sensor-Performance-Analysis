#from ROOT import *
import ROOT
import os

#ROOT.gROOT.LoadMacro("./AtlasStyle.C")     # this doesn't work...
cwd = os.getcwd()
# ROOT.gROOT.LoadMacro(cwd + "/AtlasStyle.C") # neither does this

ROOT.gROOT.LoadMacro("/afs/cern.ch/user/p/psidebo/hgtd/kth-testbeam-code/HGTD-TestBeam/style/AtlasStyle.C") # this works, but uses my local path...
ROOT.SetAtlasStyle()
