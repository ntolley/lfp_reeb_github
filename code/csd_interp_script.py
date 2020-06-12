import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import seaborn as sns
import csd_functions
import os
import sys

file_prefix = 'gbarEvPyrAmpa_reversed_inputs'
hnn_dir = os.path.abspath('template_hnn_github/data/' + file_prefix + '/hnn_out/data')

os.mkdir('data/' + file_prefix + '/points/')
save_dir = os.path.abspath('data/' + file_prefix + '/points/') #directory to store param files

for idx, f in enumerate(os.listdir(hnn_dir)):
    data_path = hnn_dir + '/' +  f + '/'
    save_path = save_dir + '/' + f + '.csv'
    Z_hnn = csd_functions.csd_interp(data_path,20)
    csd_points = csd_functions.grid2points(Z_hnn)
    np.savetxt(save_path, csd_points, delimiter=',')

