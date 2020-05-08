"""
#######################################################################
 
 Copyright (C) 2016, Joshua A. Levine
 Clemson University
 
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to
 the following conditions:
 
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 
 
#######################################################################
"""

#######################################################################
#
# Sample VTK code to experiment with the vtkReebGraph object
# Author: Joshua A. Levine
# Email: levinej@clemson.edu
# Date: Feb. 22, 2016
#
# This code builds a sample 2 triangulated grid with random values
# It computes a vtkReebGraph, and then displays it using a
# vtkGraphLayout.  It's also a simple example of using vtkLookupTable
# and vtkColorTransferFunction and multiple render windows
#
# Some "helpful" comments begin with the phrase "USER:"
#
#######################################################################


import vtk
import random
from math import cos, sin, pi

#Load data into VTK table object (https://github.com/Kitware/VTK/blob/master/Examples/Infovis/Python/tables3.py)
csv_source = vtk.vtkDelimitedTextReader()
csv_source.SetFieldDelimiterCharacters(",")
csv_source.SetHaveHeaders(False)
csv_source.SetDetectNumericColumns(True)
csv_source.SetFileName('/home/ntolley/Jones_Lab/lfp_reeb_local/data/gbarEvPyrAmpa_sweep/points/gbarEvPyrAmpa_sweep1.csv')
csv_source.Update()

T = csv_source.GetOutput()
# points = vtk.vtkPoints()

# for r in range(T.GetNumberOfRows()):
#     points.InsertNextPoint(T.GetColumn(0).GetValue(r),T.GetColumn(1).GetValue(r),T.GetColumn(2).GetValue(r))

# aPolyData = vtk.vtkPolyData()
# aPolyData.SetPoints(points)













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
min_z, max_z = point_bounds[4], point_bounds[5]

tris = vtk.vtkCellArray()

for j in range(y-1) :
   for i in range(x-1) :
      tri = [j*x+i, j*x+i+1, (j+1)*x+i]
      tris.InsertNextCell(3, tri)
      
      tri = [j*x+i+1, (j+1)*x+i, (j+1)*x+i+1]
      tris.InsertNextCell(3, tri)
   #
#

grid.SetPolys(tris)

# USER: Reduce number of points to speed up computation
decimate = vtk.vtkDecimatePro()
decimate.SetInputData(grid)
decimate.SetTargetReduction(0.99)
# decimate.PreserveTopologyOn()
decimate.Update()

decimated = vtk.vtkPolyData()
decimated.ShallowCopy(decimate.GetOutput())


# USER: write out the input file, for testing
# writer = vtk.vtkXMLPolyDataWriter()
# writer.SetFileName("test.vtp")
# writer.SetInputData(grid)
# writer.Write()


reeb_graph = vtk.vtkReebGraph()
err = reeb_graph.Build(decimated, decimated.GetPointData().GetScalars())
# USER: uncomment to see Build() error codes
#print err
# USER: uncomment to see stats on the Reeb Graph
#print reeb_graph


# USER: Reeb Graph does not (seem to) pass the data array around, it
#  only stores the Vertex Ids in the graph that's constructed.  The next
#  few lines add it back for coloring in the vtkGraphLayoutView
data2 = vtk.vtkFloatArray()
data2.SetNumberOfComponents(1)
data2.SetName("Function Value")
data3 = vtk.vtkFloatArray()
data3.SetNumberOfComponents(1)
data3.SetName("Glyph Size")

info = reeb_graph.GetVertexData().GetAbstractArray("Vertex Ids")
for i in range(info.GetNumberOfTuples()) :
   # USER: uncomment the following to see data values in the Reeb graph
   # print info.GetTuple(i), data.GetTuple(int(info.GetTuple(i)[0]))
   data2.InsertNextValue(data.GetTuple(int(info.GetTuple(i)[0]))[0])
   # USER: this controls the scale / size of glyphs in graph
   data3.InsertNextValue(4.0)

reeb_graph.GetVertexData().AddArray(data2)
reeb_graph.GetVertexData().AddArray(data3)



# Set up the graph view and its render window

view = vtk.vtkGraphLayoutView()
view.AddRepresentationFromInput(reeb_graph)
theme = vtk.vtkViewTheme.CreateMellowTheme()
lut = vtk.vtkLookupTable()
lut.SetRange(min_z,max_z)
# "hawaii" color LUT, disabled
#lut.SetHueRange(0.7, 0)
#lut.SetSaturationRange(1.0, 0)
#lut.SetValueRange(0.5, 1.0)
#lut.Build()

# Manually configured CTF, green-to-white-to-orange
ctf = vtk.vtkColorTransferFunction()
ctf.SetColorSpaceToDiverging()
#ctf.AddRGBPoint(0.0, 0.085, 0.532, 0.201)
#ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
#ctf.AddRGBPoint(1.0, 0.677, 0.492, 0.093)
for i in range(6) :
   f = float(i)/5.0
   f2 = f*0.7 + 0.3
   if i%2 == 1 :
      ctf.AddRGBPoint(f, 0.085, f2*0.532, 0.201)
   else :
      ctf.AddRGBPoint(f, f2*0.677, f2*0.492, 0.093)

num_values = 256
lut.SetNumberOfTableValues(num_values)
lut.Build()

for i in range(num_values) :
   rgb = ctf.GetColor(float(i)/num_values)
   lut.SetTableValue(i,rgb[0],rgb[1],rgb[2])

theme.SetPointLookupTable(lut)
view.ApplyViewTheme(theme)

# USER: could color the vertices by their vertex index instead of their
#  function value
#view.SetVertexColorArrayName("Vertex Ids")
view.SetVertexColorArrayName("Function Value")
view.SetColorVertices(True)
#view.SetVertexScalarBarVisibility(True)

view.SetVertexLabelArrayName("Vertex Ids")
view.SetVertexLabelVisibility(True)
view.SetVertexLabelFontSize(20)
view.SetLayoutStrategyToSimple2D()
view.SetGlyphType(vtk.vtkGraphToGlyphs.SQUARE)
view.SetScaledGlyphs(True)
view.SetScalingArrayName("Glyph Size")

view.GetRenderWindow().SetSize(600, 600)
view.ResetCamera()
view.Render()


# Set up the view that draws the polyData

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(decimated)
mapper.SetScalarRange(min_z,max_z)
mapper.SetLookupTable(lut)
bar = vtk.vtkScalarBarActor()
bar.SetLookupTable(mapper.GetLookupTable())
bar.SetTitle(data2.GetName())
actor = vtk.vtkActor()
actor.SetMapper(mapper)
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.AddActor2D(bar)
view2 = vtk.vtkRenderWindow()
view2.AddRenderer(renderer)
view2.SetSize(500,500)
renderer.ResetCamera()
view2.Render()
rwi = vtk.vtkRenderWindowInteractor()
rwi.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
rwi.SetRenderWindow(view2)

view.GetInteractor().Start()
rwi.Start()