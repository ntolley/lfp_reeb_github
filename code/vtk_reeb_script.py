import vtk
import os
import numpy as np


#Enter Sweep name
file_prefix = 'gbarEvPyrAmpa_sweep'


#Prepare directories
parent_dir = os.path.abspath('data/' + file_prefix)
os.mkdir(parent_dir + '/skeleton')

data_dir = os.path.abspath(parent_dir + '/points')
save_dir = os.path.abspath(parent_dir + '/skeleton')

file_list = os.listdir(data_dir)

for file_name in file_list:
   file_path = os.path.abspath(data_dir + '/' + file_name)

   #Load data into VTK table object (https://github.com/Kitware/VTK/blob/master/Examples/Infovis/Python/tables3.py)
   csv_source = vtk.vtkDelimitedTextReader()
   csv_source.SetFieldDelimiterCharacters(",")
   csv_source.SetHaveHeaders(False)
   csv_source.SetDetectNumericColumns(True)
   csv_source.SetFileName(file_path)
   csv_source.Update()

   T = csv_source.GetOutput()

   # USER: vtkReebGraph's Build() function will rely on a vtkPolyData that
   #  specifically only has triangles.  vtkUnstructuredGrid could be used
   #  for tetrahedra.  
   #  See http://www.vtk.org/doc/nightly/html/classvtkReebGraph.html#details
   grid = vtk.vtkPolyData()

   points = vtk.vtkPoints()
   data = vtk.vtkFloatArray()
   data.SetNumberOfComponents(1)
   data.SetName("Function Value")

   points.SetNumberOfPoints(T.GetNumberOfRows())
   for r in range(T.GetNumberOfRows()):
      points.InsertPoint(r, T.GetColumn(0).GetValue(r),T.GetColumn(1).GetValue(r),T.GetColumn(2).GetValue(r))
      data.InsertNextValue(T.GetColumn(2).GetValue(r))
      

   grid.SetPoints(points)
   grid.GetPointData().SetScalars(data)

   point_bounds = points.GetBounds()
   x, y = int(point_bounds[1]), int(point_bounds[3])


   tris = vtk.vtkCellArray()

   for j in range(y) :
      for i in range(x) :
         tri = [j*x+i, j*x+i+1, (j+1)*x+i]
         tris.InsertNextCell(3, tri)
         
         tri = [j*x+i+1, (j+1)*x+i, (j+1)*x+i+1]
         tris.InsertNextCell(3, tri)

   grid.SetPolys(tris)

   #Simplify with mesh decimate
   decimate = vtk.vtkDecimatePro()
   decimate.SetInputData(grid)
   decimate.SetTargetReduction(0.99)
   decimate.PreserveTopologyOn()
   decimate.Update()

   decimated = vtk.vtkPolyData()
   decimated.ShallowCopy(decimate.GetOutput())


   data_decimated = vtk.vtkFloatArray()
   data_decimated.SetNumberOfComponents(1)
   data_decimated.SetName("Function Value")

   #Build Reeb Graph with decimated mesh
   reeb_graph = vtk.vtkReebGraph()
   err = reeb_graph.Build(decimated, decimated.GetPointData().GetScalars())


   #Iterate over nodes and store x,y,z position
   iter_vertex = vtk.vtkVertexListIterator()
   iter_vertex.SetGraph(reeb_graph)

   point_data = decimated.GetPoints().GetData() # Vertex coordinates are stored under original mesh ID's 
   vertex_mapping = reeb_graph.GetVertexData().GetAbstractArray(0)

   vertex_list = []
   while iter_vertex.HasNext():
      graph_vertex_id = iter_vertex.Next()
      mesh_vertex_id = int(vertex_mapping.GetTuple(graph_vertex_id)[0])

      vertex_pos = point_data.GetTuple(mesh_vertex_id) 
      vertex_list.append(list(vertex_pos))




   #Iterate over edges and store source/target ID's
   iter_edge = vtk.vtkEdgeListIterator()
   iter_edge.SetGraph(reeb_graph)

   edge_list = []
   while iter_edge.HasNext():
      temp_edge = iter_edge.NextGraphEdge()
      source = temp_edge.GetSource()
      target = temp_edge.GetTarget()
      edge_list.append([source, target])

      
   #Save Skeleton Data
   node_points = np.array(vertex_list)
   node_connectivity = np.array(edge_list)

   file_name_stripped = file_name.strip('.csv')
   node_points_path = os.path.abspath(save_dir + '/' + file_name_stripped + '_nodes.csv')
   node_connectivity_path = os.path.abspath(save_dir + '/' + file_name_stripped + '_arcs.csv')

   np.savetxt(node_points_path, node_points, delimiter=',')
   np.savetxt(node_connectivity_path, node_connectivity, delimiter=',')