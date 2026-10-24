from cadgen import build123d as bd, step
from fit_frame_left import fit_frame_left
from fit_frame_right import fit_frame_right

@step(out='../STEP/fit_frame_assembly.step')
def fit_frame_assembly():
    return bd.Compound(children=[fit_frame_left(),fit_frame_right()],label='vent_fit_frame')

if __name__ == '__main__':
    fit_frame_assembly()
