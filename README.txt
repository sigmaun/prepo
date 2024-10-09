Last updated: Oct 8, 2024

This repository contains documentation files (ending in 'txt', 'pptx', 'mp4'), Python code in Jupyter Notebook format (ending in 'ipynb'), and a few example calibrations (ending in 'csv'). 

Jupyter Notebook file contains multiple 'markdown' documentation blocks and 2 code blocks: 
* Executing the first code block brings in the necessary modules and defines the necessary function objects. 
* Executing the second code block triggers a series of prompts (explained in the markdown documentation), e.g., name of the csv input file with the calibriation, range and granularity of marginal savings curves, name of the csv output file. 

If you wish to replicate computation examples in the recorded documentation (mp4 files), select any of the 'Parameters' csv files and use the following answers to prompts:
* Minumum prepo value used in marginal savings function calc: 0
* Maxumum prepo value used in marginal savings function calc: 20000
* Enter the difference between two consecutive prepo values (ie, integer step size used for computing the curves). Step size of marginal savings functions: 50

Download to your server and begin experimenting and playing with the code. You are encouraged to modify and enhance the code to suit needs and interests. In these cases, consider uploading your revised code with a related documentation txt file so that others may benefit.

Scott Webster and Mahyar Eftekhar
