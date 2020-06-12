# HNN Parameter Sweep

This repository contains scripts that perform the LFP->CSD->Reeb transformation of HNN output data

## Usage
- All relevant scripts are found in the `/code` directory
1) First run `csd_interp_script.py` by specifying the simulation output folder in the installed sub-dataset
    - All permutations of the specified parameters will be stored under `/data/<dir name>/points` as .csv files
2) Second run `vtk_reeb_script.py` by specifying the folder storing the output from step 1
    - Output will be stored under `/data/<dir name>/skeleton` as .csv files 

