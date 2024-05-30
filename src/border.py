import vtk


def create_border(x1, y1, z1, x2, y2, z2):
    line_source = vtk.vtkLineSource()
    line_source.SetPoint1(x1, y1, z1)
    line_source.SetPoint2(x2, y2, z2)

    line_mapper = vtk.vtkPolyDataMapper()
    line_mapper.SetInputConnection(line_source.GetOutputPort())

    line_actor = vtk.vtkActor()
    line_actor.SetMapper(line_mapper)

    return line_actor
