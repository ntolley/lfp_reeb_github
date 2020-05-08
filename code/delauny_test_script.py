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
    height = T.GetColumn(2).GetValue(r)*100
    points.InsertPoint(r, T.GetColumn(0).GetValue(r),T.GetColumn(1).GetValue(r),height)
    data.InsertNextValue(height)
    

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
   #
#

grid.SetPolys(tris)

decimate = vtk.vtkDecimatePro()
decimate.SetInputData(grid)
decimate.SetTargetReduction(0.99)
# decimate.PreserveTopologyOn()
decimate.Update()

decimated = vtk.vtkPolyData()
decimated.ShallowCopy(decimate.GetOutput())



# Define colors
colors = vtk.vtkNamedColors()
backFaceColor = colors.GetColor3d("gold")
inputActorColor = colors.GetColor3d("flesh")
decimatedActorColor = colors.GetColor3d("flesh")
colors.SetColor('leftBkg', [0.6, 0.5, 0.4, 1.0])
colors.SetColor('rightBkg', [0.4, 0.5, 0.6, 1.0])

inputMapper = vtk.vtkPolyDataMapper()
inputMapper.SetInputData(grid)

backFace = vtk.vtkProperty()
backFace.SetColor(backFaceColor)

inputActor = vtk.vtkActor()
inputActor.SetMapper(inputMapper)
inputActor.GetProperty().SetInterpolationToFlat()
inputActor.GetProperty().SetColor(inputActorColor)
inputActor.SetBackfaceProperty(backFace)

decimatedMapper = vtk.vtkPolyDataMapper()
decimatedMapper.SetInputData(decimated)

decimatedActor = vtk.vtkActor()
decimatedActor.SetMapper(decimatedMapper)
decimatedActor.GetProperty().SetColor(decimatedActorColor)
decimatedActor.GetProperty().SetInterpolationToFlat()
decimatedActor.SetBackfaceProperty(backFace)



# There will be one render window
renderWindow = vtk.vtkRenderWindow()
renderWindow.SetSize(600, 300)

# And one interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# Define viewport ranges
# (xmin, ymin, xmax, ymax)
leftViewport = [0.0, 0.0, 0.5, 1.0]
rightViewport = [0.5, 0.0, 1.0, 1.0]

# Setup both renderers
leftRenderer = vtk.vtkRenderer()
renderWindow.AddRenderer(leftRenderer)
leftRenderer.SetViewport(leftViewport)
leftRenderer.SetBackground((colors.GetColor3d('leftBkg')))

rightRenderer = vtk.vtkRenderer()
renderWindow.AddRenderer(rightRenderer)
rightRenderer.SetViewport(rightViewport)
rightRenderer.SetBackground((colors.GetColor3d('rightBkg')))

# Add the sphere to the left and the cube to the right
leftRenderer.AddActor(inputActor)
rightRenderer.AddActor(decimatedActor)


# Shared camera
# Shared camera looking down the -y axis
camera = vtk.vtkCamera()
camera.SetPosition (0, -1, 0)
camera.SetFocalPoint (0, 0, 0)
camera.SetViewUp (0, 0, 1)
camera.Elevation(30)
camera.Azimuth(30)

leftRenderer.SetActiveCamera(camera)
rightRenderer.SetActiveCamera(camera)

leftRenderer.ResetCamera()
leftRenderer.ResetCameraClippingRange()

renderWindow.Render()
renderWindow.SetWindowName('Decimation')

interactor.Start()







