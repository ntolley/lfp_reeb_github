import vtk
import os
import numpy as np
import vtk_functions
import pandas as pd
import networkx as nx


#Enter Sweep name
file_prefix = 'gbarEvPyrAmpa_reversed_inputs'


#Prepare directories
parent_dir = os.path.abspath('data/' + file_prefix)
os.mkdir(parent_dir + '/skeleton')

data_dir = os.path.abspath(parent_dir + '/points')
save_dir = os.path.abspath(parent_dir + '/skeleton')

file_list = os.listdir(data_dir)

for file_name in file_list:
   file_path = os.path.abspath(data_dir + '/' + file_name)


   grid = vtk_functions.csd_to_mesh(file_path)
   decimated = vtk_functions.decimate_mesh(grid, 0.99)

   reeb_graph = vtk.vtkReebGraph()
   err = reeb_graph.Build(decimated, decimated.GetPointData().GetScalars())

   node_points, node_connectivity = vtk_functions.reeb_to_skeleton(reeb_graph,decimated)

   #Save Skeleton Data
   file_name_stripped = file_name.strip('.csv')
   node_points_path = os.path.abspath(save_dir + '/' + file_name_stripped + '_nodes.csv')
   node_connectivity_path = os.path.abspath(save_dir + '/' + file_name_stripped + '_arcs.csv')

   np.savetxt(node_points_path, node_points, delimiter=',')
   np.savetxt(node_connectivity_path, node_connectivity, delimiter=',')



   G = nx.Graph()
   G.add_edges_from(node_connectivity)
   print(file_name_stripped, 'Tree: ', nx.is_tree(G))
   G.clear()