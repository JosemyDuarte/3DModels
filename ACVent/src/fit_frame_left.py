from cadgen import step, stl
from lib.geometry import fit_frame

@step(out='../STEP/fit_frame_left.step')
@stl(out='../STL/fit_frame_left.stl', mesh_tolerance=0.0002)
def fit_frame_left():
    return fit_frame(True)

if __name__ == '__main__':
    fit_frame_left()
