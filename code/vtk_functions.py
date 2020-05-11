import vtk
import pandas as pd
import os
import numpy as np

def decimate_mesh(grid, target):
    decimate = vtk.vtkDecimatePro()
    decimate.SetInputData(grid)
    decimate.SetTargetReduction(target)
    decimate.PreserveTopologyOn()
    decimate.Update()

    decimated = vtk.vtkPolyData()
    decimated.ShallowCopy(decimate.GetOutput())


    data_decimated = vtk.vtkFloatArray()
    data_decimated.SetNumberOfComponents(1)
    data_decimated.SetName("Function Value")

    return data_decimated



def reeb_to_skeleton(reeb_graph, grid):
    #Iterate over arcs in reeb graph and store as source-target pairs
    iter_edge = vtk.vtkEdgeListIterator()
    iter_edge.SetGraph(reeb_graph)

    edge_list = []
    while iter_edge.HasNext():
        temp_edge = iter_edge.NextGraphEdge()
        source = temp_edge.GetSource()
        target = temp_edge.GetTarget()
        edge_list.append([source, target])

    #Iterate over nodes and store x,y,z position
    iter_vertex = vtk.vtkVertexListIterator()
    iter_vertex.SetGraph(reeb_graph)

    # Vertex coordinates are stored under original mesh ID's 
    point_data = grid.GetPoints().GetData()
    vertex_mapping = reeb_graph.GetVertexData().GetAbstractArray(0)

    vertex_list = []
    while iter_vertex.HasNext():
        graph_vertex_id = iter_vertex.Next()
        mesh_vertex_id = int(vertex_mapping.GetTuple(graph_vertex_id)[0])

        vertex_pos = point_data.GetTuple(mesh_vertex_id) 
        vertex_list.append(list(vertex_pos))


#Convert interpolated CSD points to a polygonal mesh
def csd_to_mesh(filename):
    #Load data values into grid
    np_points = np.array(pd.read_csv(file_name))
    point_bounds = np.max(np_points,axis=0) + 1
    int(point_bounds[0])
    topography = np.zeros((int(point_bounds[0]),int(point_bounds[1])))

    for p in range(np_points.shape[0]):
        topography[int(np_points[p,0]),int(np_points[p,1])] = np_points[p,2]

    points = vtk.vtkPoints()
    triangles = vtk.vtkCellArray()

    data = vtk.vtkFloatArray()
    data.SetNumberOfComponents(1)
    data.SetName("Function Value")

    # Build the meshgrid manually
    count = 0
    for i in range(topography.shape[0]-1):
        for j in range(topography.shape[1]-1):
            z1 = topography[i][j]
            z2 = topography[i][j + 1]
            z3 = topography[i + 1][j]

            # Triangle 1
            points.InsertNextPoint(i, j, z1)
            points.InsertNextPoint(i, (j + 1), z2)
            points.InsertNextPoint((i + 1), j, z3)

            data.InsertNextValue(z1)
            data.InsertNextValue(z2)
            data.InsertNextValue(z3)

            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, count)
            triangle.GetPointIds().SetId(1, count + 1)
            triangle.GetPointIds().SetId(2, count + 2)

            triangles.InsertNextCell(triangle)

            z1 = topography[i][j + 1]
            z2 = topography[i + 1][j + 1]
            z3 = topography[i + 1][j]

            # Triangle 2
            points.InsertNextPoint(i, (j + 1), z1)
            points.InsertNextPoint((i + 1), (j + 1), z2)
            points.InsertNextPoint((i + 1), j, z3)

            data.InsertNextValue(z1)
            data.InsertNextValue(z2)
            data.InsertNextValue(z3)
            
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, count + 3)
            triangle.GetPointIds().SetId(1, count + 4)
            triangle.GetPointIds().SetId(2, count + 5)

            count += 6

            triangles.InsertNextCell(triangle)

    # Create a polydata object
    trianglePolyData = vtk.vtkPolyData()

    # Add the geometry and topology to the polydata
    trianglePolyData.SetPoints(points)
    trianglePolyData.SetPolys(triangles)
    trianglePolyData.GetPointData().SetScalars(data)

    # Clean the polydata so that the edges are shared !
    cleanPolyData = vtk.vtkCleanPolyData()
    cleanPolyData.SetInputData(trianglePolyData)
    cleanPolyData.Update()
    dir(cleanPolyData)

    grid = cleanPolyData.GetOutput()
    return grid