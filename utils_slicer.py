import os
import gc
import slicer
import numpy as np
from vtk import vtkWindowToImageFilter, vtkPNGWriter

def clear_all():
    slicer.mrmlScene.Clear()
    gc.collect()

def load_data(model, patient):
    path_main = r"\\10.125.208.30\gpu_server_data\Guhong\Airway\res\Visualization"
    path_patient = os.path.join(path_main, model)

    # 세 개의 파일 이름
    list_seg = [f'{patient}_FN.nii.gz',
                f'{patient}_FP.nii.gz',
                f'{patient}_y_data.nii.gz']

    for seg in list_seg:
        path = os.path.join(path_patient, seg)
        data = slicer.util.loadSegmentation(path)
        print(f'Load: {model}/{seg}')

path_save = 'C:/Users/amilab/AppData/Local/slicer.org/Slicer 5.5.0-2023-10-09/utils/view_setting.npy'
def save_view(path_save=path_save):
    layoutManager = slicer.app.layoutManager()
    threeDView = layoutManager.threeDWidget(0).threeDView()
    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    camera = renderer.GetActiveCamera()

    cameraPosition = list(camera.GetPosition())  
    focalPoint = list(camera.GetFocalPoint())
    viewUp = list(camera.GetViewUp())
    isOrthographic = bool(camera.GetParallelProjection()) 
    parallelScale = float(camera.GetParallelScale()) if isOrthographic else None 

    data = {
        'cameraPosition': cameraPosition,
        'focalPoint': focalPoint,
        'viewUp': viewUp,
        'parallelScale': parallelScale,
        'isOrthographic': isOrthographic}
    
    np.save(path_save, data, allow_pickle=True)
    print(f'Saving: {path_save}')

def load_view(path_save=path_save):
    layoutManager = slicer.app.layoutManager()
    threeDView = layoutManager.threeDWidget(0).threeDView()
    
    renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
    camera = renderer.GetActiveCamera()

    data = np.load(path_save, allow_pickle=True).item()
    camera.SetPosition(data['cameraPosition'])
    camera.SetFocalPoint(data['focalPoint'])
    camera.SetViewUp(data['viewUp'])

    camera.SetParallelProjection(data['isOrthographic'])
    if data['isOrthographic'] and data['parallelScale'] is not None:
        camera.SetParallelScale(data['parallelScale'])

    threeDView.renderWindow().Render()
    print(f'Loading: {path_save}')

def show_data():
    # Seg Rendering
    segmentation_nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for node in segmentation_nodes:
        display_node = node.GetDisplayNode()
        display_node.SetVisibility3D(True)

        display_node.SetSegmentVisibility3D('All', True)
        display_node.SetPreferredDisplayRepresentationName3D('Closed surface')

        segmentation = node.GetSegmentation()
        segmentation.SetConversionParameter("Smoothing factor", "0.0")
        segmentation.SetConversionParameter("Decimation factor", "0.0")
        segmentation.SetConversionParameter("Surface smoothing", "off")
        
        segmentation.CreateRepresentation("Closed surface")

def set_color():
    # Background Color
    threeDWidget = slicer.app.layoutManager().threeDWidget(0)
    threeDView = threeDWidget.threeDView()
    renderWindow = threeDView.renderWindow()
    renderer = renderWindow.GetRenderers().GetFirstRenderer()

    renderer.SetBackground(1.0, 1.0, 1.0)      # Upper
    renderer.SetBackground2(1.0, 1.0, 1.0)     # Bottom

    renderer.GradientBackgroundOn()
    renderWindow.Render()
    
    for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode"):
        name = node.GetName()
        segment_id = node.GetSegmentation().GetNthSegmentID(0)
        display_node = node.GetDisplayNode()

        if "FN" in name:
            rgb, opacity = (1.0, 0.0, 0.0), 1.0   # Red
        elif "FP" in name:
            rgb, opacity = (0.0, 1.0, 0.0), 1.0   # Green
        elif "y_data" in name:
            rgb, opacity = (147/255, 145/255, 201/255), 0.2   # True

        node.GetSegmentation().GetSegment(segment_id).SetColor(*rgb)
        display_node.SetSegmentOpacity3D(segment_id, opacity)
        display_node.SetSegmentOpacity2DFill(segment_id, opacity)
        display_node.SetSegmentOpacity2DOutline(segment_id, opacity)

def capture(path_main='C:/Users/amilab/AppData/Local/slicer.org/Slicer 5.5.0-2023-10-09/capture', 
            name = 'img.png', 
            scale_factor=4):
    renderWindow = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow()
    original_size = renderWindow.GetSize()

    scale_factor = scale_factor
    renderWindow.SetSize(original_size[0]*scale_factor, original_size[1]*scale_factor)
    renderWindow.Render()

    w2i = vtkWindowToImageFilter()
    w2i.SetInput(renderWindow)
    w2i.Update()

    save_path = f'{path_main}/{name}'
    writer = vtkPNGWriter()
    writer.SetFileName(save_path)
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.Write()

    renderWindow.SetSize(original_size)
    renderWindow.Render()
    print(f'save_path: {save_path}')

def show(model, patient):
    load_data(model, patient)
    show_data()
    set_color()
    load_view()
    name = f'{patient}_{model}.png'
    capture(name=name)
    gc.collect()
