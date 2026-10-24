from cadgen import step, stl
from lib.geometry import half

@step(out='../STEP/deflector_right.step')
@stl(out='../STL/deflector_right.stl', mesh_tolerance=0.0002)
def deflector_right():
    return half(False)

if __name__ == '__main__':
    deflector_right()
