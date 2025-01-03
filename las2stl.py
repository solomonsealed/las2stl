import pyvista as pv
import laspy as lp
import numpy as np
import trimesh

SAMPLE_RATE = 0.001
SCALEXY = 0.01
SCALEZ = 0.01
BASE_THICKNESS = 2

filename = input("Enter the filename (without extension) of a *.las file in the 'las' folder: ")

print("Load...")
cloud = lp.read('./las/' + filename + '.las')

points = np.vstack((cloud.x, cloud.y, cloud.z)).transpose()

print("Extracting Sample...")
if SAMPLE_RATE < 1.0:
    indices = np.random.choice(points.shape[0], size=int(points.shape[0] * SAMPLE_RATE), replace=False)
    points = points[indices]

print("Surface reconstruction...")
mesh = pv.wrap(points).delaunay_2d(alpha=0.0, progress_bar=True)
mesh = mesh.compute_normals(progress_bar=True)

print("Re-save...")
mesh.save('./stl/' + filename + '.stl')

print("Translation...")
tmesh = trimesh.load('./stl/' + filename + '.stl')
bounding_box = tmesh.bounds

# Z translation is base height for common ground and minheight for non-common ground
z_translation = -bounding_box[0][2]

# Move the entire mesh to (0,0,0)
translation_vector = [-bounding_box[0][0], -bounding_box[0][1], z_translation]
tmesh.apply_translation(translation_vector)
tmesh.export('./stl/' + filename + '.stl')

print("Extrusion...")
# Extrude the surface mesh downwards to create a volume
mesh = pv.read("./stl/" + filename + ".stl")
size = bounding_box[1] - bounding_box[0]
xcenter = 0.5 * size[0]
ycenter = 0.5 * size[1]
plane = pv.Plane(
    center=(xcenter, ycenter, -BASE_THICKNESS * (1 - SCALEZ)),
    direction=(0, 0, -1),
    i_size=size[0],
    j_size=size[1],
)
mesh = mesh.extrude_trim((0, 0, -1.0), plane, progress_bar=True)

print("Scale...")
# Scale the mesh according to the settings
mesh = mesh.scale([SCALEXY, SCALEXY, SCALEZ], inplace=False)

print("Saving...")
mesh.save('./stl/' + filename + '.stl')

spacer = bounding_box[0][2] * SCALEZ
print("This tile needs a " + str(spacer) + "mm spacer")

print("Done.")
