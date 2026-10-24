from cadgen import step, stl
from lib.geometry import fit_frame

@step(out='../STEP/fit_frame_right.step')
@stl(out='../STL/fit_frame_right.stl', mesh_tolerance=0.0002)
def fit_frame_right():
    return fit_frame(False)

if __name__ == '__main__':
    fit_frame_right()
