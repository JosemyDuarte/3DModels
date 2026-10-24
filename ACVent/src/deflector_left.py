from cadgen import step, stl
from lib.geometry import half

@step(out='../STEP/deflector_left.step')
@stl(out='../STL/deflector_left.stl', mesh_tolerance=0.00001)
def deflector_left():
    return half(True)

if __name__ == '__main__':
    deflector_left()
