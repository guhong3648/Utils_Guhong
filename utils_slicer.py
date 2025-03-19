import os
import slicer
import numpy as np

path_save = 'C:/Users/amilab/AppData/Local/slicer.org/Slicer 5.5.0-2023-10-09/utils/view_setting.npy'

def save_view():
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

def load_view():
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
