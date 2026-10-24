from cadgen import step, stl
from lib.geometry import first_layers

@step(out='../STEP/first_layers_right.step')
@stl(out='../STL/first_layers_right.stl', mesh_tolerance=0.0002)
def first_layers_right():
    return first_layers(False)

if __name__ == '__main__':
    first_layers_right()
